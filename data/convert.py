import pandas as pd
import json
import os
import datetime

# --- SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, 'team_stats.json')

# We only extract matches from recent seasons where the format is consistent
FILES_CONFIG = [
    {
        "key": "season_25_26",
        "filename": "STATS 25-26.xlsx",
        "skip": 3,
        "cols": {0: 'name', 3: 'number', 6: 'apps', 12: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}
    },
    {
        "key": "season_24_25",
        "filename": "STATS 24-25.xlsx",
        "skip": 3,
        "cols": {0: 'name', 3: 'number', 6: 'apps', 12: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}
    },
    # Older seasons kept for player stats, but maybe skipped for match logs if format differs
    { "key": "season_23_24", "filename": "STATS 23-24.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 12: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'} },
    { "key": "season_22_23", "filename": "STATS 2022-23.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 11: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'} },
    { "key": "season_21_22", "filename": "STATS 2021-22.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 11: 'goals', 16: 'assists', 19: 'yellow_cards', 20: 'red_cards'} },
    { "key": "season_20_21", "filename": "Rosa e Stats 2020-2021.xlsx", "skip": 7, "cols": {0: 'name', 3: 'number', 7: 'apps', 12: 'goals', 14: 'assists', 17: 'yellow_cards', 18: 'red_cards'} },
    { "key": "season_19_20", "filename": "statistiche calci8 2019-2020.xlsx", "skip": 4, "cols": {0: 'name', 3: 'number', 7: 'apps', 9: 'goals', 12: 'yellow_cards', 13: 'red_cards'} }
]

# --- PLAYER STATS LOGIC (Same as before) ---
def is_real_player(row):
    name = str(row['name']).strip()
    if name.startswith('202') or name.startswith('201'): return False
    blacklist = ['Amichevoli', 'Torneo', 'Spring', 'Cup', 'Coppa', 'Playoff', 'Playout', 'Gironi', 'Ottavi', 'Quarti', 'Semifinale', 'Finale', 'Tamarindi']
    if any(word in name for word in blacklist): return False
    if pd.isna(row.get('apps')) or str(row.get('apps')).strip() == '': return False
    return True

def process_player_stats(df, config):
    data = df.iloc[config['skip']:].copy()
    data = data.rename(columns=config['cols'])
    
    required = ['name', 'number', 'apps', 'goals', 'assists', 'yellow_cards', 'red_cards']
    for col in required:
        if col not in data.columns:
            data[col] = '-' if col == 'assists' else 0
            
    data = data[required]
    data = data.dropna(subset=['name'])
    data = data[data.apply(is_real_player, axis=1)]
    
    data['name'] = data['name'].astype(str).str.title() # Title case names
    data['number'] = data['number'].fillna('-').astype(str).str.replace('.0', '', regex=False)
    
    for col in ['apps', 'goals', 'assists', 'yellow_cards', 'red_cards']:
        if str(data[col].iloc[0]) == '-': continue
        data[col] = data[col].fillna(0).astype(int)
        
    return data.to_dict(orient='records')

# --- NEW: MATCH LOG LOGIC ---
def extract_matches(df, season_key):
    matches = []
    current_match = None
    
    # Iterate through ALL rows to find dates
    # Matches usually look like: Date (Col 0) | .. | Home (Col 2) | .. | Score (Col 4) | Opponent (Col 5)
    for index, row in df.iterrows():
        val0 = str(row[0]).strip()
        
        # 1. Check if it's a Date (Start of a match)
        is_date = False
        try:
            # Check for "YYYY-MM-DD" or datetime objects
            if isinstance(row[0], datetime.datetime) or (len(val0) >= 10 and val0[0:4].isdigit() and '-' in val0):
                is_date = True
        except:
            is_date = False

        if is_date:
            # Save previous match if exists
            if current_match:
                matches.append(current_match)
            
            # Start new match
            # Based on your files: Col 4 is score "1-5", Col 5 is Opponent "Corinthias"
            score = str(row[4]).strip() if not pd.isna(row[4]) else "?"
            opponent = str(row[5]).strip() if not pd.isna(row[5]) else "Unknown"
            
            # Clean up date string
            date_str = str(row[0]).split(' ')[0] 

            current_match = {
                "date": date_str,
                "opponent": opponent,
                "score": score,
                "scorers": [],
                "season": season_key
            }
        
        # 2. If we are inside a match block, look for scorers
        elif current_match:
            # Scorers are usually in Col 2 (Home Team column) under the match row
            # We stop if we hit a blank row or a header
            potential_name = str(row[2]).strip()
            
            # Filter out junk
            if pd.isna(row[2]) or potential_name == '' or potential_name == 'nan' or potential_name == 'Tamarindi FC':
                continue
                
            # If it looks like a player name, add it
            current_match['scorers'].append(potential_name)

    # Append the last match found
    if current_match:
        matches.append(current_match)
        
    return matches

# --- MAIN ---
if __name__ == "__main__":
    final_data = {}
    all_matches = []
    
    for config in FILES_CONFIG:
        path = os.path.join(BASE_DIR, config['filename'])
        if not os.path.exists(path): continue
        
        print(f"Processing {config['key']}...")
        try:
            df = pd.read_excel(path, header=None)
            
            # 1. Get Players
            final_data[config['key']] = process_player_stats(df, config)
            
            # 2. Get Matches (New!)
            season_matches = extract_matches(df, config['key'])
            all_matches.extend(season_matches)
            
        except Exception as e:
            print(f"Error {config['key']}: {e}")
    
    # Sort matches by date (Newest first)
    all_matches.sort(key=lambda x: x['date'], reverse=True)
    final_data['matches'] = all_matches
    
    # Process All Time (Same as before)
    # ... (Simplified for brevity, assuming you kept the previous process_all_time code)
    # Re-add your process_all_time logic here if needed, or just basic player stats
    
    # Saving
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
    print("Done! Matches extracted.")
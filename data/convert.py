import pandas as pd
import json
import os
import datetime
import re

# --- CONFIGURATION & SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, 'team_stats.json')

# Standard columns we need for the website
REQUIRED_COLUMNS = ['name', 'number', 'apps', 'goals', 'assists', 'yellow_cards', 'red_cards']

# Map of all season files and their unique column structure
FILES_CONFIG = [
    {"key": "season_25_26", "filename": "STATS 25-26.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 12: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}},
    {"key": "season_24_25", "filename": "STATS 24-25.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 12: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}},
    {"key": "season_23_24", "filename": "STATS 23-24.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 12: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}},
    {"key": "season_22_23", "filename": "STATS 2022-23.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 11: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}},
    {"key": "season_21_22", "filename": "STATS 2021-22.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 11: 'goals', 16: 'assists', 19: 'yellow_cards', 20: 'red_cards'}},
    {"key": "season_20_21", "filename": "Rosa e Stats 2020-2021.xlsx", "skip": 7, "cols": {0: 'name', 3: 'number', 7: 'apps', 12: 'goals', 14: 'assists', 17: 'yellow_cards', 18: 'red_cards'}},
    {"key": "season_19_20", "filename": "statistiche calci8 2019-2020.xlsx", "skip": 4, "cols": {0: 'name', 3: 'number', 7: 'apps', 9: 'goals', 12: 'yellow_cards', 13: 'red_cards'}}
]

# --- PLAYER STATS LOGIC ---
def is_real_player(row):
    # Filters out dates, competition titles, and empty rows.
    name = str(row['name']).strip()
    if name.startswith('202') or name.startswith('201') or name.startswith('200'): return False
    blacklist = ['Amichevoli', 'Torneo', 'Spring', 'Cup', 'Coppa', 'Playoff', 'Playout', 'Gironi', 'Ottavi', 'Quarti', 'Semifinale', 'Finale', 'Tamarindi']
    if any(word in name for word in blacklist): return False
    if pd.isna(row.get('apps')) or str(row.get('apps')).strip() == '': return False
    return True

def process_player_stats(df, config):
    data = df.iloc[config['skip']:].copy()
    data = data.rename(columns=config['cols'])
    
    for col in REQUIRED_COLUMNS:
        if col not in data.columns:
            data[col] = '-' if col == 'assists' else 0
            
    data = data[REQUIRED_COLUMNS]
    data = data.dropna(subset=['name'])
    data = data[data.apply(is_real_player, axis=1)]
    
    data['name'] = data['name'].astype(str).str.title() 
    data['number'] = data['number'].fillna('-').astype(str).str.replace('.0', '', regex=False)
    
    for col in ['apps', 'goals', 'assists', 'yellow_cards', 'red_cards']:
        if str(data[col].iloc[0]) == '-': continue
        # Robustly convert stats to integers
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        
    return data.to_dict(orient='records')

# --- HALL OF FAME FIX ---
def process_all_time():
    path = os.path.join(BASE_DIR, 'STATS TOTALI.xlsx')
    if not os.path.exists(path): return []
    
    try:
        df = pd.read_excel(path, header=None)
        data = df.iloc[3:].copy()
        cols = {0: 'name', 2: 'role', 11: 'total_apps', 20: 'total_goals', 29: 'total_assists'}
        
        clean = data.rename(columns=cols)
        clean = clean.dropna(subset=['name'])

        # 1. CLEANING: Ensure name and role are strings
        clean['name'] = clean['name'].astype(str)
        clean['role'] = clean['role'].astype(str).str.strip().fillna('Player')
        
        # 2. FILTERING: Remove non-player rows by checking if 'total_apps' is actually a number
        # If total_apps is junk (e.g., text header), pd.to_numeric makes it NaN, so we drop it.
        clean = clean[pd.to_numeric(clean['total_apps'], errors='coerce').notna()]
        
        # 3. TITLE CASE: Fix capitalization (as requested)
        clean['name'] = clean['name'].str.title()
        
        # 4. FINAL CONVERSION: Convert all stats to integers
        for c in ['total_apps', 'total_goals', 'total_assists']:
            clean[c] = pd.to_numeric(clean[c], errors='coerce').fillna(0).astype(int)
            
        return clean[['name', 'role', 'total_apps', 'total_goals', 'total_assists']].to_dict(orient='records')
    except Exception as e:
        # Catch and print the error specifically for Netlify log analysis
        print(f"FATAL ERROR in Hall of Fame (process_all_time): {e}")
        return []

# --- MATCH LOGIC (Kept for completeness but should be refined next) ---
def extract_matches(df, season_key):
    matches = []
    current_match = None
    
    for index, row in df.iterrows():
        val0 = str(row[0]).strip()
        is_date = False
        try:
            if isinstance(row[0], datetime.datetime) or (len(val0) >= 10 and val0[0:4].isdigit() and ('-' in val0 or '/' in val0)):
                is_date = True
        except:
            pass

        if is_date:
            if current_match: matches.append(current_match)
            
            score_col = str(row[4]).strip() if not pd.isna(row[4]) else '?-?'
            score_parts = score_col.split('-')
            
            home_team = str(row[2]).strip() if not pd.isna(row[2]) else ''
            
            if home_team.startswith('Tamarindi FC'):
                score = score_col
                opponent = str(row[5]).strip() if not pd.isna(row[5]) else 'Unknown'
                tamarindi_score = score_parts[0].strip()
                result = 'W' if tamarindi_score > score_parts[1].strip() else ('D' if tamarindi_score == score_parts[1].strip() else 'L')
                
            else:
                score = score_col
                opponent = str(row[2]).strip()
                tamarindi_score = score_parts[1].strip() if len(score_parts) == 2 else '?'
                result = 'W' if score_parts[0].strip() < tamarindi_score else ('D' if score_parts[0].strip() == tamarindi_score else 'L')
                
            date_str = str(row[0]).split(' ')[0] 

            current_match = {
                "date": date_str,
                "opponent": opponent.replace('Tamarindi FC', '').strip(),
                "score": score,
                "result": result,
                "scorers": [],
                "season": season_key
            }
        
        elif current_match:
            potential_scorer_home = str(row[2]).strip() if not pd.isna(row[2]) else ''
            potential_scorer_away = str(row[5]).strip() if not pd.isna(row[5]) else ''

            scorer = None
            if potential_scorer_home and not re.match(r'[A-Za-z]', potential_scorer_home) is None:
                 scorer = potential_scorer_home
            elif potential_scorer_away and not pd.isna(row[5]) and not re.match(r'[A-Za-z]', potential_scorer_away) is None:
                 scorer = potential_scorer_away
                 
            if scorer and not any(word in scorer for word in ['Tamarindi', 'Campioni', 'Club', 'FC', 'Coppa']):
                 current_match['scorers'].append(scorer.strip().replace('  ',' ').title())


    if current_match: matches.append(current_match)
    return [m for m in matches if m['opponent'] not in ('Unknown', '') and m['score'] != '?']


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("Starting conversion...")
    final_data = {}
    all_matches = []
    
    # Process Seasons
    for config in FILES_CONFIG:
        path = os.path.join(BASE_DIR, config['filename'])
        if not os.path.exists(path): continue
        
        try:
            df = pd.read_excel(path, header=None)
            final_data[config['key']] = process_player_stats(df, config)
            season_matches = extract_matches(df, config['key'])
            all_matches.extend(season_matches)
            
        except Exception as e:
            print(f"Error processing {config['key']}: {e}")
    
    # Process All Time (Hall of Fame)
    final_data['all_time'] = process_all_time()
    
    # Finalize Matches
    all_matches.sort(key=lambda x: x['date'], reverse=True)
    final_data['matches'] = all_matches
    
    # Save JSON
    output_path = os.path.join(BASE_DIR, 'team_stats.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
        
    print("Done! Data conversion complete.")
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

# --- HELPER FUNCTIONS ---

def is_real_player(row):
    # This logic is used to filter out competition names from the player stats section
    name = str(row['name']).strip()
    if name.startswith('202') or name.startswith('201') or name.startswith('200'): return False
    blacklist = ['Amichevoli', 'Torneo', 'Spring', 'Cup', 'Coppa', 'Playoff', 'Playout', 'Gironi', 'Ottavi', 'Quarti', 'Semifinale', 'Finale', 'Tamarindi']
    if any(word in name for word in blacklist): return False
    if pd.isna(row.get('apps')) or str(row.get('apps')).strip() == '': return False
    return True

def process_player_stats(df, config):
    # ... (player stats logic - kept separate but needs to be in final script)
    data = df.iloc[config['skip']:].copy()
    data = data.rename(columns=config['cols'])
    
    required = ['name', 'number', 'apps', 'goals', 'assists', 'yellow_cards', 'red_cards']
    for col in required:
        if col not in data.columns:
            data[col] = '-' if col == 'assists' else 0
            
    data = data[required]
    data = data.dropna(subset=['name'])
    data = data[data.apply(is_real_player, axis=1)]
    
    data['name'] = data['name'].astype(str).str.title() 
    data['number'] = data['number'].fillna('-').astype(str).str.replace('.0', '', regex=False)
    
    for col in ['apps', 'goals', 'assists', 'yellow_cards', 'red_cards']:
        if str(data[col].iloc[0]) == '-': continue
        data[col] = data[col].fillna(0).astype(int)
        
    return data.to_dict(orient='records')


def extract_matches(df, season_key):
    matches = []
    current_match = None
    
    # Pre-process the DataFrame to combine Name and Number/Score (Col 0 and Col 4-6 are key)
    
    for index, row in df.iterrows():
        val0 = str(row[0]).strip()
        
        # 1. Check if it's a Date (Start of a match) - Usually in Col 0
        is_date = False
        try:
            if isinstance(row[0], datetime.datetime) or (len(val0) >= 10 and val0[0:4].isdigit() and ('-' in val0 or '/' in val0)):
                is_date = True
        except:
            pass

        if is_date:
            if current_match: matches.append(current_match)
            
            # --- DETERMINE HOME/AWAY AND EXTRACT SCORE/OPPONENT ---
            
            # Look at Column 2 (usually the 'Home' team)
            home_team = str(row[2]).strip() if not pd.isna(row[2]) else ''
            
            # Look at Column 4 (usually the 'Score')
            score_col = str(row[4]).strip() if not pd.isna(row[4]) else ''
            
            score_parts = score_col.split('-')
            
            if home_team.startswith('Tamarindi FC'):
                # TAMARINDI (Col 2) | SCORE (Col 4) | OPPONENT (Col 5)
                score = str(row[4]).strip() if not pd.isna(row[4]) else '?-?'
                opponent = str(row[5]).strip() if not pd.isna(row[5]) else 'Unknown'
                tamarindi_score = score_parts[0].strip()
                result = 'W' if tamarindi_score > score_parts[1].strip() else ('D' if tamarindi_score == score_parts[1].strip() else 'L')
                
            else:
                # OPPONENT (Col 2) | SCORE (Col 4) | TAMARINDI (Col 6, maybe)
                # In many of the files, the opponent is in Col 2 and score in Col 4/5
                
                # Check for a "Home Score - Away Score" pattern
                if len(score_parts) == 2 and score_parts[0].isdigit() and score_parts[1].isdigit():
                    opponent = str(row[2]).strip()
                    score = score_col
                    tamarindi_score = score_parts[1].strip() # Away Score is second number
                    result = 'W' if tamarindi_score > score_parts[0].strip() else ('D' if tamarindi_score == score_parts[0].strip() else 'L')
                else:
                    # Fallback for confusing formats (e.g. 2020-2021 file)
                    opponent = str(row[5]).strip() if not pd.isna(row[5]) else 'Unknown'
                    score = str(row[4]).strip() if not pd.isna(row[4]) else '?-?'
                    result = '?'
            
            # Clean up date string
            date_str = str(row[0]).split(' ')[0] 
            
            current_match = {
                "date": date_str,
                "opponent": opponent.replace('Tamarindi FC', '').strip(), # Ensure we don't have Tamarindi vs Tamarindi
                "score": score,
                "result": result,
                "scorers": [],
                "season": season_key
            }
        
        # 2. If we are inside a match block, look for scorers (Col 2 or 5)
        elif current_match:
            # Check Col 2 (for home matches) and Col 5 (for away matches)
            potential_scorer_home = str(row[2]).strip() if not pd.isna(row[2]) else ''
            potential_scorer_away = str(row[5]).strip() if not pd.isna(row[5]) else ''

            scorer = None
            if potential_scorer_home and not re.match(r'[A-Za-z]', potential_scorer_home) is None:
                 scorer = potential_scorer_home
            elif potential_scorer_away and not re.match(r'[A-Za-z]', potential_scorer_away) is None:
                 scorer = potential_scorer_away
                 
            # Add scorer if valid
            if scorer:
                # Check if it's a team/competition name instead of a person
                if not any(word in scorer for word in ['Tamarindi', 'Campana', 'Cutroni', 'Scocco', 'Ciolli', 'Iannuccelli', 'Gioffredi', 'D\'Amato', 'Botta', 'Autogol', 'Autogol P.', 'Colella']):
                     # Skip things that look like team names or junk
                     if len(scorer) < 15 and 'FC' not in scorer and 'Club' not in scorer:
                          current_match['scorers'].append(scorer.strip().replace('  ',' ').title())


    # Append the last match found
    if current_match: matches.append(current_match)
        
    # Final cleanup (remove matches with incomplete data)
    return [m for m in matches if m['opponent'] not in ('Unknown', '') and m['score'] != '?']

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    final_data = {}
    all_matches = []
    
    for config in FILES_CONFIG:
        path = os.path.join(BASE_DIR, config['filename'])
        if not os.path.exists(path): continue
        
        try:
            df = pd.read_excel(path, header=None)
            
            # 1. Get Players
            final_data[config['key']] = process_player_stats(df, config)
            
            # 2. Get Matches
            season_matches = extract_matches(df, config['key'])
            all_matches.extend(season_matches)
            
        except Exception as e:
            print(f"Error processing {config['key']}: {e}")
            print(f"Last row processed: {df.iloc[-1].to_string()}") # Helpful for debugging
    
    # Sort all matches by date (Newest first)
    all_matches.sort(key=lambda x: x['date'], reverse=True)
    final_data['matches'] = all_matches
    
    # Process All Time (assuming you kept the previous process_all_time code)
    # ... (Re-insert your final process_all_time code here)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
        
    print("Done! All data extracted and formatted.")
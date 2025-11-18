import pandas as pd
import json
import os
import datetime
import re
import numpy as np

# --- CONFIGURATION & SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, 'team_stats.json')

REQUIRED_COLUMNS = ['name', 'number', 'apps', 'goals', 'assists', 'yellow_cards', 'red_cards']

# Map of all season files and their unique column structure (remains the same)
FILES_CONFIG = [
    {"key": "season_25_26", "filename": "STATS 25-26.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 12: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}},
    {"key": "season_24_25", "filename": "STATS 24-25.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 12: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}},
    {"key": "season_23_24", "filename": "STATS 23-24.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 12: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}},
    {"key": "season_22_23", "filename": "STATS 2022-23.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 11: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'} },
    {"key": "season_21_22", "filename": "STATS 2021-22.xlsx", "skip": 3, "cols": {0: 'name', 3: 'number', 6: 'apps', 11: 'goals', 16: 'assists', 19: 'yellow_cards', 20: 'red_cards'} },
    {"key": "season_20_21", "filename": "Rosa e Stats 2020-2021.xlsx", "skip": 7, "cols": {0: 'name', 3: 'number', 7: 'apps', 12: 'goals', 14: 'assists', 17: 'yellow_cards', 18: 'red_cards'} },
    {"key": "season_19_20", "filename": "statistiche calci8 2019-2020.xlsx", "skip": 4, "cols": {0: 'name', 3: 'number', 7: 'apps', 9: 'goals', 12: 'yellow_cards', 13: 'red_cards'} }
]

# (Other player processing functions remain unchanged for brevity)

def is_real_player(row):
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
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        
    return data.to_dict(orient='records')

def process_all_time():
    path = os.path.join(BASE_DIR, 'STATS TOTALI.xlsx')
    if not os.path.exists(path): return []
    
    try:
        df = pd.read_excel(path, header=None)
        data = df.iloc[3:].copy()
        cols = {0: 'name', 2: 'role', 11: 'total_apps', 20: 'total_goals', 29: 'total_assists'}
        
        clean = data.rename(columns=cols)
        clean = clean.dropna(subset=['name'])

        clean['name'] = clean['name'].astype(str)
        clean['role'] = clean['role'].astype(str).str.strip().fillna('Player')
        
        clean = clean[pd.to_numeric(clean['total_apps'], errors='coerce').notna()]
        
        clean['name'] = clean['name'].str.title()
        
        for c in ['total_apps', 'total_goals', 'total_assists']:
            clean[c] = pd.to_numeric(clean[c], errors='coerce').fillna(0).astype(int)
            
        return clean[['name', 'role', 'total_apps', 'total_goals', 'total_assists']].to_dict(orient='records')
    except Exception as e:
        print(f"FATAL ERROR in Hall of Fame (process_all_time): {e}")
        return []

# --- FINAL MATCH LOGIC ---
def extract_matches(df, season_key):
    matches = []
    current_match = None
    
    df_iter = df.reset_index(drop=True)
    
    for index, row in df_iter.iterrows():
        val0 = str(row[0]).strip()
        is_date = False
        try:
            if isinstance(row[0], datetime.datetime) or (len(val0) >= 10 and val0[0:4].isdigit() and ('-' in val0 or '/' in val0)):
                is_date = True
        except:
            pass

        if is_date:
            if current_match: matches.append(current_match)
            
            # (Home/Away logic - remains unchanged)
            tamarindi_is_home = False
            opponent = 'Unknown'
            if str(row[2]).strip().startswith('Tamarindi FC') or str(row[2]).strip().startswith('Tamarindi F.C.'):
                tamarindi_is_home = True
                opponent = str(row[5]).strip() if not pd.isna(row[5]) else 'Unknown'
            elif str(row[5]).strip().startswith('Tamarindi FC') or str(row[5]).strip().startswith('Tamarindi F.C.'):
                tamarindi_is_home = False
                opponent = str(row[2]).strip() if not pd.isna(row[2]) else 'Unknown'
            else:
                tamarindi_is_home = False
                opponent = str(row[2]).strip() if not pd.isna(row[2]) else 'Unknown'

            score = str(row[4]).strip() if not pd.isna(row[4]) else '?-?'
            score_parts = score.split('-')
            
            result = '?'
            shootout_score = None 
            if len(score_parts) == 2 and score_parts[0].strip().isdigit() and score_parts[1].strip().isdigit():
                home_score = int(score_parts[0].strip())
                away_score = int(score_parts[1].strip())
                
                tamarindi_score = home_score if tamarindi_is_home else away_score
                opponent_score = away_score if tamarindi_is_home else home_score

                if tamarindi_score > opponent_score: result = 'W'
                elif tamarindi_score < opponent_score: result = 'L'
                else: result = 'D'
            
            date_str = str(row[0]).split(' ')[0] 

            current_match = {
                "date": date_str,
                "opponent": opponent.replace('Tamarindi FC', '').strip(),
                "score": score,
                "result": result,
                "scorers": [],
                "yellow_cards_recipients": [], 
                "red_cards_recipients": [], 
                "shootout_score": shootout_score,
                "season": season_key,
                "home_status": "Home" if tamarindi_is_home else "Away"
            }
        
        elif current_match:
            # --- PENALTY SHOOTOUT DETECTION ---
            if pd.notna(row[4]) and 'd.c.r' in str(row[4]).lower():
                current_match['shootout_score'] = str(row[4]).strip()
                shootout_parts = str(row[4]).split('+')[-1].strip().split('-')
                
                if len(shootout_parts) == 2 and shootout_parts[0].strip().isdigit() and shootout_parts[1].strip().isdigit():
                    home_so_score = int(shootout_parts[0].strip())
                    away_so_score = int(shootout_parts[1].strip())

                    if tamarindi_is_home:
                        tamarindi_so_score = home_so_score
                    else:
                        tamarindi_so_score = away_so_score

                    if tamarindi_so_score > int(shootout_parts[1-int(tamarindi_is_home)]): # Compares TFC score to opponent score
                        current_match['result'] = 'W(SO)'
                    else: 
                        current_match['result'] = 'L(SO)'
                
                continue 
            
            # --- Normal Card/Goal Parsing ---
            potential_scorer_home = str(row[2]).strip() if not pd.isna(row[2]) else ''
            potential_scorer_away = str(row[5]).strip() if not pd.isna(row[5]) else ''

            scorer_col_value = None
            if current_match['home_status'] == 'Home':
                scorer_col_value = potential_scorer_home
            elif current_match['home_status'] == 'Away':
                scorer_col_value = potential_scorer_away

            if scorer_col_value:
                scorer_col_value = scorer_col_value.replace('  ', ' ').strip()
                
                if not any(word in scorer_col_value for word in ['Tamarindi', 'FC', 'Club', 'Torneo']):
                    
                    original_value = scorer_col_value.title()
                    
                    # 1. Filter out SAVED Penalty [R parato]
                    if 'R PARATO' in scorer_col_value.upper():
                        pass 

                    # 2. Check for Red Card [R] (FINAL CONFIRMED MARKER)
                    elif '[R]' in scorer_col_value.upper() or '(R)' in scorer_col_value.upper():
                         name_to_add = scorer_col_value.upper().replace('[R]', '').replace('(R)', '').strip().title()
                         if name_to_add:
                              current_match['red_cards_recipients'].append(name_to_add)
                    
                    # 3. Check for Yellow Card [Y]
                    elif '[Y]' in scorer_col_value.upper() or '(Y)' in scorer_col_value.upper():
                         name_to_add = scorer_col_value.upper().replace('[Y]', '').replace('(Y)', '').strip().title()
                         if name_to_add:
                              current_match['yellow_cards_recipients'].append(name_to_add)
                    
                    # 4. Check for Penalty Goal [P]
                    elif '[P]' in scorer_col_value.upper() or '(P)' in scorer_col_value.upper():
                         name_to_add = scorer_col_value.upper().replace('[P]', '').replace('(P)', '').strip().title()
                         if name_to_add:
                              current_match['scorers'].append(name_to_add + ' (Pen)')

                    # 5. Normal Goal
                    elif re.search(r'\(\d+\)', original_value) or re.match(r'[A-Za-z]', original_value):
                         current_match['scorers'].append(original_value)
            

    if current_match: matches.append(current_match)
    return [m for m in matches if m['opponent'] not in ('Unknown', '') and m['score'] != '?']


# --- MAIN EXECUTION (Remains unchanged) ---
if __name__ == "__main__":
    print("Starting conversion...")
    final_data = {}
    all_matches = []
    
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
    
    final_data['all_time'] = process_all_time()
    
    all_matches.sort(key=lambda x: x['date'], reverse=True)
    final_data['matches'] = all_matches
    
    output_path = os.path.join(BASE_DIR, 'team_stats.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
        
    print("Done! Data conversion complete.")
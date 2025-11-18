import pandas as pd
import json
import os

# --- SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, 'team_stats.json')

# Standard columns we need for the website
REQUIRED_COLUMNS = ['name', 'number', 'apps', 'goals', 'assists', 'yellow_cards', 'red_cards']

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
    {
        "key": "season_23_24",
        "filename": "STATS 23-24.xlsx",
        "skip": 3,
        "cols": {0: 'name', 3: 'number', 6: 'apps', 12: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}
    },
    {
        "key": "season_22_23",
        "filename": "STATS 2022-23.xlsx",
        "skip": 3,
        "cols": {0: 'name', 3: 'number', 6: 'apps', 11: 'goals', 18: 'assists', 21: 'yellow_cards', 22: 'red_cards'}
    },
    {
        "key": "season_21_22",
        "filename": "STATS 2021-22.xlsx",
        "skip": 3,
        "cols": {0: 'name', 3: 'number', 6: 'apps', 11: 'goals', 16: 'assists', 19: 'yellow_cards', 20: 'red_cards'}
    },
    {
        "key": "season_20_21",
        "filename": "Rosa e Stats 2020-2021.xlsx",
        "skip": 7,
        "cols": {0: 'name', 3: 'number', 7: 'apps', 12: 'goals', 14: 'assists', 17: 'yellow_cards', 18: 'red_cards'}
    },
    {
        "key": "season_19_20",
        "filename": "statistiche calci8 2019-2020.xlsx",
        "skip": 4, 
        "cols": {0: 'name', 3: 'number', 7: 'apps', 9: 'goals', 12: 'yellow_cards', 13: 'red_cards'} # No assists!
    }
]

def is_real_player(row):
    name = str(row['name']).strip()
    if name.startswith('202') or name.startswith('201'): return False
    
    blacklist = ['Amichevoli', 'Torneo', 'Spring', 'Cup', 'Coppa', 'Playoff', 'Playout', 'Gironi', 'Ottavi', 'Quarti', 'Semifinale', 'Finale']
    if any(word in name for word in blacklist): return False
    
    if pd.isna(row.get('apps')) or str(row.get('apps')).strip() == '': return False
    return True

def process_file(config):
    file_path = os.path.join(BASE_DIR, config['filename'])
    if not os.path.exists(file_path):
        print(f"Skipping {config['key']}: File not found ({config['filename']})")
        return []

    try:
        df = pd.read_excel(file_path, header=None)
        
        # 1. Slice and Rename
        data = df.iloc[config['skip']:].copy()
        data = data.rename(columns=config['cols'])
        
        # 2. Ensure ALL required columns exist (Fill missing ones with 0)
        for col in REQUIRED_COLUMNS:
            if col not in data.columns:
                data[col] = 0
        
        # 3. Keep ONLY the standard columns (Sorts them neatly too)
        data = data[REQUIRED_COLUMNS]
        
        # --- CLEANING ---
        data = data.dropna(subset=['name'])
        data = data[data.apply(is_real_player, axis=1)]
        
        data['name'] = data['name'].astype(str)
        data['number'] = data['number'].fillna('-').astype(str).str.replace('.0', '', regex=False)
        
        for col in ['apps', 'goals', 'assists', 'yellow_cards', 'red_cards']:
            data[col] = data[col].fillna(0).astype(int)
            
        return data.to_dict(orient='records')

    except Exception as e:
        print(f"Error processing {config['key']}: {e}")
        return []

def process_all_time():
    path = os.path.join(BASE_DIR, 'STATS TOTALI.xlsx')
    if not os.path.exists(path): return []
    
    try:
        df = pd.read_excel(path, header=None)
        data = df.iloc[3:].copy()
        cols = {0: 'name', 2: 'role', 11: 'total_apps', 20: 'total_goals', 29: 'total_assists'}
        
        clean = data.rename(columns=cols)
        clean = clean.dropna(subset=['name'])
        clean = clean[clean['name'].astype(str).str.strip() != '']
        
        # Filter out date rows in All Time too, just in case
        clean = clean[~clean['name'].astype(str).str.startswith('20')]
        
        for c in ['total_apps', 'total_goals', 'total_assists']:
            clean[c] = clean[c].fillna(0).astype(int)
            
        clean['role'] = clean['role'].fillna('Player')
        return clean[['name', 'role', 'total_apps', 'total_goals', 'total_assists']].to_dict(orient='records')
    except Exception as e:
        print(f"Error all time: {e}")
        return []

if __name__ == "__main__":
    final_data = {}
    
    for config in FILES_CONFIG:
        print(f"Processing {config['key']}...")
        final_data[config['key']] = process_file(config)
        
    print("Processing All Time...")
    final_data['all_time'] = process_all_time()
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
        
    print("Done! Stats updated.")
import pandas as pd
import json
import os

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_CURRENT = os.path.join(BASE_DIR, 'STATS 24-25.xlsx')
FILE_TOTAL   = os.path.join(BASE_DIR, 'STATS TOTALI.xlsx')
OUTPUT_FILE  = os.path.join(BASE_DIR, 'team_stats.json')

def is_valid_player_name(x):
    """
    Helper function to check if a 'name' is actually a player 
    and not a match date or metadata.
    """
    # 1. If it's a Datetime object (which caused the crash), it's a date, not a name.
    if hasattr(x, 'year') and hasattr(x, 'month'):
        return False
    
    # 2. If it looks like a date string (e.g. "2025-03-12"), ignore it.
    s = str(x).strip()
    if (s.startswith('202') or s.startswith('201')) and ('-' in s or '/' in s):
        return False
        
    return True

def clean_current_season(file_path):
    try:
        df = pd.read_excel(file_path, header=None)
        data = df.iloc[3:].copy()
        
        cols = {
            0: 'name', 3: 'number', 6: 'apps', 
            11: 'goals', 17: 'assists', 
            21: 'yellow_cards', 22: 'red_cards'
        }
        
        clean = data[list(cols.keys())].rename(columns=cols)
        
        # --- THE FIX ---
        # Remove empty names first
        clean = clean.dropna(subset=['name'])
        
        # Filter out the rows that are actually dates
        clean = clean[clean['name'].apply(is_valid_player_name)]
        
        # Force the Name column to be text (String) just to be safe for JSON
        clean['name'] = clean['name'].astype(str)
        # ---------------
        
        for c in ['apps', 'goals', 'assists', 'yellow_cards', 'red_cards']:
            clean[c] = clean[c].fillna(0).astype(int)
            
        clean['number'] = clean['number'].fillna('-').astype(str).str.replace('.0', '', regex=False)
        
        return clean.to_dict(orient='records')
    except Exception as e:
        print(f"Error processing Current Season: {e}")
        return []

def clean_all_time(file_path):
    try:
        df = pd.read_excel(file_path, header=None)
        data = df.iloc[3:].copy()
        
        cols = {
            0: 'name', 2: 'role', 
            11: 'total_apps', 20: 'total_goals', 29: 'total_assists'
        }
        
        clean = data[list(cols.keys())].rename(columns=cols)
        clean = clean.dropna(subset=['name'])
        
        # Apply the same safety checks here too
        clean = clean[clean['name'].apply(is_valid_player_name)]
        clean['name'] = clean['name'].astype(str)
        
        for c in ['total_apps', 'total_goals', 'total_assists']:
            clean[c] = clean[c].fillna(0).astype(int)
            
        clean['role'] = clean['role'].fillna('Player')
        return clean.to_dict(orient='records')
    except Exception as e:
        print(f"Error processing All Time: {e}")
        return []

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("Reading Excel files...")
    
    # Check if files exist before running
    if not os.path.exists(FILE_CURRENT):
        print(f"WARNING: Could not find {FILE_CURRENT}")
        current_stats = []
    else:
        current_stats = clean_current_season(FILE_CURRENT)

    if not os.path.exists(FILE_TOTAL):
        print(f"WARNING: Could not find {FILE_TOTAL}")
        all_time_stats = []
    else:
        all_time_stats = clean_all_time(FILE_TOTAL)
    
    final_data = {
        "season_24_25": current_stats,
        "all_time": all_time_stats
    }
    
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
        
    print(f"Success! Data saved to {OUTPUT_FILE}")
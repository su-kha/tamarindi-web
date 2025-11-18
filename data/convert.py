import pandas as pd
import json
import os

# --- CONFIGURATION ---
# Make sure these match your actual file names!
FILE_CURRENT = 'STATS 24-25.xlsx'
FILE_TOTAL   = 'STATS TOTALI.xlsx'
OUTPUT_FILE  = 'team_stats.json'

def clean_current_season(file_path):
    try:
        # Read CSV/Excel. If it's really .xlsx, pandas reads it directly.
        # If you saved them as CSV, change read_excel to read_csv.
        df = pd.read_excel(file_path, header=None)
        
        # The data starts at row 3 (index 3) based on your file structure
        data = df.iloc[3:].copy()
        
        # Map the messy columns to clean names
        # Based on your file: 0=Name, 3=Number, 6=Apps, 11=Goals, 17=Assists, 21=Yellow, 22=Red
        cols = {
            0: 'name', 3: 'number', 6: 'apps', 
            11: 'goals', 17: 'assists', 
            21: 'yellow_cards', 22: 'red_cards'
        }
        
        clean = data[list(cols.keys())].rename(columns=cols)
        clean = clean.dropna(subset=['name']) # Remove empty rows
        
        # Fill empty stats with 0
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
        
        # Map columns: 0=Name, 2=Role, 11=Total Apps, 20=Total Goals, 29=Total Assists
        cols = {
            0: 'name', 2: 'role', 
            11: 'total_apps', 20: 'total_goals', 29: 'total_assists'
        }
        
        clean = data[list(cols.keys())].rename(columns=cols)
        clean = clean.dropna(subset=['name'])
        
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
    current_stats = clean_current_season(FILE_CURRENT)
    all_time_stats = clean_all_time(FILE_TOTAL)
    
    final_data = {
        "season_24_25": current_stats,
        "all_time": all_time_stats
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
        
    print(f"Success! Data saved to {OUTPUT_FILE}")
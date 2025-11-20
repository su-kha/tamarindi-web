import pandas as pd
import json
import os
import requests
from thefuzz import fuzz
import datetime
import re
import numpy as np

# --- CONFIGURATION & SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data/')
OUTPUT_FILE = os.path.join(DATA_DIR, 'website_data_cache.json')

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
    path = os.path.join(DATA_DIR, 'STATS TOTALI.xlsx')
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
    
# --- CORE MATCH LOGIC FIX ---
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
            
            # --- HOME/AWAY LOGIC ---
            tamarindi_is_home = False
            opponent = 'Unknown'
            
            if season_key == 'season_19_20':
                # 19/20 Format: Date (0) | Team A (2) | Score A (4) | - (5) | Score B (6) | Team B (7)
                
                # Check Col 2 for Tamarindi (Home)
                if str(row[2]).strip().startswith('Tamarindi F.C.') or str(row[2]).strip().startswith('Tamarindi FC'):
                    tamarindi_is_home = True
                    opponent = str(row[7]).strip() if not pd.isna(row[7]) else 'Unknown'
                # Check Col 7 for Tamarindi (Away)
                elif str(row[7]).strip().startswith('Tamarindi F.C.') or str(row[7]).strip().startswith('Tamarindi FC'):
                    tamarindi_is_home = False
                    opponent = str(row[2]).strip() if not pd.isna(row[2]) else 'Unknown'
                
                # Score is always Col 4 - Col 6
                score = f"{str(row[4]).strip()}-{str(row[6]).strip()}" if not pd.isna(row[4]) and not pd.isna(row[6]) else '?-?'
                
            else:
                # Other Seasons Format: Date (0) | Team A (2) | Score (4) | Opponent (5)
                
                # Check Col 2 for Tamarindi (Home)
                if str(row[2]).strip().startswith('Tamarindi F.C.') or str(row[2]).strip().startswith('Tamarindi FC'):
                    tamarindi_is_home = True
                    opponent = str(row[5]).strip() if not pd.isna(row[5]) else 'Unknown'
                # Check Col 5 for Tamarindi (Away)
                elif str(row[5]).strip().startswith('Tamarindi F.C.') or str(row[5]).strip().startswith('Tamarindi FC'):
                    tamarindi_is_home = False
                    opponent = str(row[2]).strip() if not pd.isna(row[2]) else 'Unknown'
                else: # Fallback - Assume Away
                    tamarindi_is_home = False
                    opponent = str(row[2]).strip() if not pd.isna(row[2]) else 'Unknown'
                    
                score = str(row[4]).strip() if not pd.isna(row[4]) else '?-?'
            
            # --- RESULT CALCULATION (Based on Score) ---
            result = '?'
            shootout_score = None 
            score_parts = score.split('-')
            
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
                "saved_penalty_goalkeepers": [], # <-- NEW LIST
                "shootout_score": shootout_score,
                "season": season_key,
                "home_status": "Home" if tamarindi_is_home else "Away"
            }
        
        elif current_match:
            # --- PENALTY SHOOTOUT DETECTION ---
            if pd.notna(row[4]) and 'dcr' in str(row[4]).lower():
                # Shootout logic remains the same (Correctly checks next row)
                current_match['shootout_score'] = str(row[4]).strip()
                shootout_parts = str(row[4]).split('+')[-1].strip().split('-')
                
                if len(shootout_parts) == 2 and shootout_parts[0].strip().isdigit() and shootout_parts[1].strip().isdigit():
                    home_so_score = int(shootout_parts[0].strip())
                    away_so_score = int(shootout_parts[1].strip())

                    if tamarindi_is_home:
                        tamarindi_so_score = home_so_score
                    else:
                        tamarindi_so_score = away_so_score

                    if tamarindi_so_score > int(shootout_parts[1-int(tamarindi_is_home)]):
                        current_match['result'] = 'W(SO)'
                    else: 
                        current_match['result'] = 'L(SO)'
                
                continue 
            
            # --- Normal Card/Goal Parsing ---
            # 19/20 format places all player events (scorers/cards) in Col 4 (Home) or Col 6 (Away)
            if season_key == 'season_19_20':
                potential_scorer_home = str(row[4]).strip() if not pd.isna(row[4]) else ''
                potential_scorer_away = str(row[6]).strip() if not pd.isna(row[6]) else ''
                scorer_col_value = potential_scorer_home if current_match['home_status'] == 'Home' else potential_scorer_away
            else:
                # Other seasons use Col 2 (Home) or Col 5 (Away)
                potential_scorer_home = str(row[2]).strip() if not pd.isna(row[2]) else ''
                potential_scorer_away = str(row[5]).strip() if not pd.isna(row[5]) else ''
                scorer_col_value = potential_scorer_home if current_match['home_status'] == 'Home' else potential_scorer_away
            
            if scorer_col_value and not pd.isna(scorer_col_value):
                scorer_col_value = scorer_col_value.replace('  ', ' ').strip()
                
                if not any(word in scorer_col_value for word in ['Tamarindi', 'FC', 'Club', 'Torneo']):
                    
                    original_value = scorer_col_value.title()
                    name_only = scorer_col_value.upper()
                    
                    # 1. Check for SAVED Penalty [R parato] (NEW LOGIC)
                    if 'R PARATO' in name_only:
                        name_to_add = name_only.replace('[R PARATO]', '').strip().title()
                        if name_to_add:
                             current_match['saved_penalty_goalkeepers'].append(name_to_add)

                    # 2. Check for Red Card [R]
                    elif '[R]' in name_only or '(R)' in name_only:
                         name_to_add = name_only.replace('[R]', '').replace('(R)', '').strip().title()
                         if name_to_add:
                              current_match['red_cards_recipients'].append(name_to_add)
                    
                    # 3. Check for Yellow Card [Y]
                    elif '[Y]' in name_only or '(Y)' in name_only:
                         name_to_add = name_only.replace('[Y]', '').replace('(Y)', '').strip().title()
                         if name_to_add:
                              current_match['yellow_cards_recipients'].append(name_to_add)
                    
                    # 4. Check for Penalty Goal [P]
                    elif '[P]' in name_only or '(P)' in name_only:
                         name_to_add = name_only.replace('[P]', '').replace('(P)', '').strip().title()
                         if name_to_add:
                              current_match['scorers'].append(name_to_add + ' (Pen)')

                    # 5. Normal Goal (Any name with or without numbers, not stripped by a card marker)
                    elif re.search(r'\(\d+\)', original_value) or re.match(r'[A-Za-z]', original_value):
                         current_match['scorers'].append(original_value)
            

    if current_match: matches.append(current_match)
    return [m for m in matches if m['opponent'] not in ('Unknown', '') and m['score'] != '?']

# --- NEW: STRICT YOUTUBE MATCHER (No Fuzzy) ---
def fetch_youtube_videos_and_link(all_matches, api_key, channel_id):
    """Fetches videos and links them using strict Date + Score + Name filtering."""
    
    # 1. Get Uploads Playlist ID
    # (This part assumes you have the CHANNEL_ID_VAR and requests imported)
    if not channel_id:
        print("Error: YOUTUBE_CHANNEL_ID not set.")
        return all_matches

    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching channel details: {response.text}")
        return all_matches
    
    channel_data = response.json()
    if not channel_data.get('items'):
        return all_matches

    uploads_playlist_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # 2. Fetch Videos (Only from 23/24 season onwards)
    all_videos = []
    next_page_token = None
    start_date = datetime.datetime(2023, 8, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)

    while True:
        playlist_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={uploads_playlist_id}&key={api_key}"
        if next_page_token:
            playlist_url += f"&pageToken={next_page_token}"
            
        response = requests.get(playlist_url)
        if response.status_code != 200:
            break
            
        playlist_data = response.json()
        
        for item in playlist_data.get('items', []):
            pub_str = item['snippet']['publishedAt'].replace('Z', '+00:00')
            published_at = datetime.datetime.fromisoformat(pub_str)
            
            if published_at >= start_date:
                all_videos.append({
                    'title': item['snippet']['title'],
                    'videoId': item['snippet']['resourceId']['videoId'],
                    'publishedAt': published_at
                })
            elif published_at < start_date:
                next_page_token = None 
                break
        
        next_page_token = playlist_data.get('nextPageToken')
        if not next_page_token:
            break

    print(f"Found {len(all_videos)} potential videos. Linking to matches...")

    # 3. Link Videos to Matches (Strict Filtering)
    for match in all_matches:
        
        try:
            match_date = datetime.datetime.strptime(match['date'], '%Y-%m-%d').date()
        except:
            continue 

        for video in all_videos:

            if match['opponent'] == 'Atletico Madrid':
                video_date = video['publishedAt'].date()
                
                print(delta, video_date, match_date)
                # FILTER 1: Date Window (Previous, Same day or Next day only)
                delta = abs(video_date - match_date).days
                if delta > 1:
                    continue 
                
                video_title_clean = video['title'].lower().replace(' ', '')
                
                print(video_title_clean)
                if ('tamarindi' or 'palermo') in video_title_clean:
                    match['videoId'] = video['videoId']
                    break # Found the exact match, stop checking other videos
        
    return all_matches

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("Starting conversion...")
    final_data = {}
    all_matches = []
    
    for config in FILES_CONFIG:
        path = os.path.join(DATA_DIR, config['filename'])
        if not os.path.exists(path): continue
        
        try:
            df = pd.read_excel(path, header=None)
            final_data[config['key']] = process_player_stats(df, config)
            season_matches = extract_matches(df, config['key'])
            all_matches.extend(season_matches)
            
        except Exception as e:
            print(f"Error processing {config['key']}: {e}")
    
    final_data['all_time'] = process_all_time()
    
    # --- YouTube API Integration (Build-Time Fetch) ---
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY')
    youtube_channel_id = os.environ.get('TORNEICONTI_CHANNEL_ID')
    
    if youtube_api_key and youtube_channel_id:
        print("API keys found. Fetching YouTube video list...")
        all_matches = fetch_youtube_videos_and_link(all_matches, youtube_api_key, youtube_channel_id)
    else:
        print("WARNING: YOUTUBE_API_KEY or CHANNEL_ID not found in environment variables. Skipping video fetch.")
        
    # Finalize Matches (Sorts and saves all_matches, now with video IDs)
    all_matches.sort(key=lambda x: x['date'], reverse=True)
    final_data['matches'] = all_matches
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
        
    print("Done! Data conversion complete.")
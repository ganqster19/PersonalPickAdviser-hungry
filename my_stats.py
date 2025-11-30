import time
import pandas as pd
from riotwatcher import LolWatcher, RiotWatcher, ApiError

# --- AYARLAR ---
API_KEY = 'YOUR_API_KEY_HERE'
MY_GAME_NAME = 'original mermi' 
MY_TAG_LINE = 'lzbyn'           
ROUTING = 'europe'
MY_FILENAME = 'My_Personal_Stats.csv'

lol_watcher = LolWatcher(API_KEY)
riot_watcher = RiotWatcher(API_KEY)

def get_personal_history():
    print(f"--- {MY_GAME_NAME} Kişisel Veri Analizi ---")
    all_games = []
    
    try:
        user = riot_watcher.account.by_riot_id(ROUTING, MY_GAME_NAME, MY_TAG_LINE)
        puuid = user['puuid']
        
        # Son 100 maçı tarasın
        match_ids = lol_watcher.match.matchlist_by_puuid(ROUTING, puuid, count=100, queue=420)
        print(f"Son {len(match_ids)} maç taranıyor...")
        
        for i, match_id in enumerate(match_ids):
            try:
                det = lol_watcher.match.by_id(ROUTING, match_id)
                if det['info']['gameDuration'] < 300: continue
                
                parts = det['info']['participants']
                
                # Ben kimim?
                me = next((p for p in parts if p['puuid'] == puuid), None)
                if not me: continue
                
                # Rakibim kim?
                enemy_champ = "Unknown"
                for p in parts:
                    if p['teamId'] != me['teamId'] and p['teamPosition'] == me['teamPosition']:
                        enemy_champ = p['championName']
                        break
                
                all_games.append({
                    'My_Champion': me['championName'],
                    'Enemy_Champion': enemy_champ,
                    'Win': 1 if me['win'] else 0,
                    'Role': me['teamPosition']
                })
                print(f"[{i+1}] {me['championName']} vs {enemy_champ} işlendi.")
                time.sleep(0.1)
                
            except: continue
            
        if all_games:
            pd.DataFrame(all_games).to_csv(MY_FILENAME, index=False)
            print(f"\n✅ Veriler '{MY_FILENAME}' dosyasına kaydedildi.")
            
    except Exception as e: print(f"Hata: {e}")

if __name__ == "__main__":
    get_personal_history()
import time
import pandas as pd
import os
from riotwatcher import LolWatcher, ApiError

# --- AYARLAR ---
# GitHub'a yüklerken burayı gizlemeyi unutma!
API_KEY = 'YOUR_API_KEY_HERE' 
REGION = 'tr1'
ROUTING = 'europe'

# Verilerin kaydedileceği tek ana dosya
FILENAME = 'Global_Meta_Data.csv' 

# Hangi ligleri tarasın?
TARGET_TIERS = ['CHALLENGER', 'GRANDMASTER', 'EMERALD'] 
PLAYER_LIMIT_PER_TIER = 30  
MATCH_LIMIT = 20            

watcher = LolWatcher(API_KEY)

def load_existing_ids():
    if not os.path.exists(FILENAME): return set()
    try:
        df = pd.read_csv(FILENAME, usecols=['Match_ID'])
        return set(df['Match_ID'].unique())
    except: return set()

def run_miner():
    recorded_matches = load_existing_ids()
    print(f"--- KÜRESEL VERİ MADENCİSİ BAŞLATILDI ---")
    print(f"Hedef Dosya: {FILENAME}")
    print(f"Mevcut Kayıt Sayısı: {len(recorded_matches)}")
    
    for tier in TARGET_TIERS:
        print(f"\n>> {tier} Ligi Taranıyor...")
        try:
            # Oyuncu listesini al
            if tier in ['CHALLENGER', 'GRANDMASTER', 'MASTER']:
                if tier == 'CHALLENGER': func = watcher.league.challenger_by_queue
                elif tier == 'GRANDMASTER': func = watcher.league.grandmaster_by_queue
                else: func = watcher.league.masters_by_queue
                entries = func(REGION, 'RANKED_SOLO_5x5')['entries']
            else:
                entries = watcher.league.entries(REGION, 'RANKED_SOLO_5x5', tier, 'I', page=1)

            # Limit kadar oyuncu seç
            players = entries[:PLAYER_LIMIT_PER_TIER]
            
            for i, p in enumerate(players):
                try:
                    # PUUID Çöz
                    if 'puuid' in p: puuid = p['puuid']
                    else: 
                        summ = watcher.summoner.by_id(REGION, p['summonerId'])
                        puuid = summ['puuid']
                    
                    print(f"[{tier}] Oyuncu {i+1}/{len(players)} işleniyor...")
                    
                    # Maçları Çek
                    match_ids = watcher.match.matchlist_by_puuid(ROUTING, puuid, count=MATCH_LIMIT, queue=420)
                    player_batch = []
                    
                    for match_id in match_ids:
                        if match_id in recorded_matches: continue
                        
                        try:
                            match_detail = watcher.match.by_id(ROUTING, match_id)
                            if match_detail['info']['gameDuration'] < 300: continue
                            
                            participants = match_detail['info']['participants']
                            row = {'Match_ID': match_id, 'Tier': tier}
                            
                            for part in participants:
                                team = 'Blue' if part['teamId'] == 100 else 'Red'
                                role = part['teamPosition']
                                if not role or role == 'UTILITY': 
                                    if role == 'UTILITY': role = 'SUPPORT'
                                
                                row[f"{team}_{role}"] = part['championName']
                                row[f"{team}_Win"] = 1 if part['win'] else 0
                            
                            if len(row) > 9:
                                player_batch.append(row)
                                recorded_matches.add(match_id)
                            
                            time.sleep(0.1)
                        except: continue

                    # Kaydet
                    if player_batch:
                        df_batch = pd.DataFrame(player_batch)
                        header = not os.path.exists(FILENAME)
                        df_batch.to_csv(FILENAME, mode='a', header=header, index=False)
                        print(f"   + {len(player_batch)} yeni maç eklendi.")
                        
                except: time.sleep(1)
                
        except Exception as e: print(f"Lig hatası: {e}")

if __name__ == "__main__":
    run_miner()
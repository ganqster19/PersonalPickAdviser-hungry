import pandas as pd
import os

# --- AYARLAR ---
# Okunacak Meta Dosyaları (Eski klasöründen buraya taşıdıklarını buraya ekle)
META_FILES = [
    'Global_Meta_Data.csv',       # Yeni oluşturacağın
    'HighElo_Dataset.csv',        # Eski dosyan (Varsa)
    'BigData_Challenger.csv',     # Eski dosyan (Varsa)
    'League_Data_Range.csv'       # Eski dosyan (Varsa)
]
PERSONAL_FILE = 'My_Personal_Stats.csv'

class DraftSystem:
    def __init__(self):
        print("--- DRAFT MOTORU BAŞLATILIYOR ---")
        self.meta_df = self.combine_meta()
        self.personal_df = self.load_csv(PERSONAL_FILE)
        self.stats = self.process_personal()

    def load_csv(self, path):
        if os.path.exists(path): return pd.read_csv(path)
        return pd.DataFrame()

    def combine_meta(self):
        combined = pd.DataFrame()
        for f in META_FILES:
            if os.path.exists(f):
                try:
                    df = pd.read_csv(f)
                    combined = pd.concat([combined, df], ignore_index=True)
                    print(f"✅ Yüklendi: {f}")
                except: pass
        
        if not combined.empty and 'Match_ID' in combined.columns:
            combined.drop_duplicates(subset=['Match_ID'], inplace=True)
            print(f"📊 TOPLAM VERİ: {len(combined)} Eşsiz Maç")
        return combined

    def process_personal(self):
        if self.personal_df.empty: return {}, {}
        gen, vs = {}, {}
        
        # Genel İstatistikler
        col = 'My_Champion' if 'My_Champion' in self.personal_df.columns else 'Champion'
        for n, g in self.personal_df.groupby(col):
            gen[n] = {'WR': (g['Win'].mean())*100, 'Games': len(g)}
            
        # Rakibe Özel İstatistikler
        if 'Enemy_Champion' in self.personal_df.columns:
            for (enemy, me), g in self.personal_df.groupby(['Enemy_Champion', col]):
                if enemy not in vs: vs[enemy] = {}
                vs[enemy][me] = {'WR': (g['Win'].mean())*100, 'Games': len(g)}
                
        return gen, vs

    def suggest(self, enemy, role):
        print(f"\n⚔️ ANALİZ: {enemy} ({role}) rakibine karşı...")
        enemy = enemy.capitalize()
        pool = {}

        # 1. Meta Analizi
        if not self.meta_df.empty:
            for _, r in self.meta_df.iterrows():
                # Mavi vs Kırmızı veya Kırmızı vs Mavi
                win = None
                my_pick = None
                
                if r.get(f'Blue_{role}') == enemy:
                    my_pick = r.get(f'Red_{role}')
                    win = 1 - r['Blue_Win']
                elif r.get(f'Red_{role}') == enemy:
                    my_pick = r.get(f'Blue_{role}')
                    win = r['Blue_Win']
                
                if my_pick and pd.notna(my_pick):
                    if my_pick not in pool: pool[my_pick] = {'W':0, 'G':0}
                    pool[my_pick]['G'] += 1
                    pool[my_pick]['W'] += win

        # 2. Puanlama
        results = []
        gen_stats, vs_stats = self.stats
        
        for ch, data in pool.items():
            if data['G'] < 3: continue
            meta_wr = (data['W']/data['G']) * 100
            
            # Kişisel Veriler
            my_g = gen_stats.get(ch, {'WR':0, 'Games':0})
            my_vs = vs_stats.get(enemy, {}).get(ch, {'WR': my_g['WR'], 'Games':0})
            
            # FORMÜL: %30 Meta + %40 Genel Ustalık + %30 Vs Geçmişi
            score = (meta_wr * 0.3) + (my_g['WR'] * 0.4) + (my_vs['WR'] * 0.3)
            
            # Bonuslar
            if my_g['Games'] > 10: score += 5
            if my_vs['Games'] > 0 and my_vs['WR'] > 50: score += 10
            if my_g['Games'] == 0: score -= 15 # Bilmediğin hero cezası

            status = "⭐ GÜÇLÜ" if my_g['Games'] > 0 else "⚠️ META"
            if my_vs['Games'] > 0: status = "⚔️ DENENDİ"

            results.append({
                'Şampiyon': ch,
                'Puan': round(score, 1),
                'Durum': status,
                'Meta WR': f"%{int(meta_wr)}",
                'Genel WR': f"%{int(my_g['WR'])}",
                'Vs Rakip': f"%{int(my_vs['WR'])} ({my_vs['Games']})"
            })

        df = pd.DataFrame(results).sort_values('Puan', ascending=False)
        return df.head(15)

if __name__ == "__main__":
    eng = DraftSystem()
    while True:
        enemy = input("\nRakip Şampiyon (Çıkış 'q'): ")
        if enemy == 'q': break
        role = input("Rol (TOP, MIDDLE...): ").upper()
        print(eng.suggest(enemy, role).to_string(index=False))
import json, os
from settings import SAVE_FILE, RANKING_FILE

class SaveManager:
    def __init__(self, save_file=SAVE_FILE, ranking_file=RANKING_FILE):
        self.save_file = save_file
        self.ranking_file = ranking_file

    def save(self, data):
        with open(self.save_file, 'w', encoding='utf-8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(self.save_file): 
            return None
        with open(self.save_file, 'r', encoding='utf-8') as f: 
            return json.load(f)
        
    def has_save(self): 
        return os.path.exists(self.save_file)
    
    def delete(self):
        if os.path.exists(self.save_file): 
            os.remove(self.save_file)

    def load_rankings(self, stage_id=1):
        if not os.path.exists(self.ranking_file): 
            return []
        
        try:
            with open(self.ranking_file, 'r', encoding='utf-8') as f: 
                all_data = json.load(f)
                
            if isinstance(all_data, dict):
                res = all_data.get(str(stage_id), [])
                if isinstance(res, list):
                    return res
            return []
        except Exception as e:
            print(f"랭킹 로드 중 예외 발생: {e}") 
            return []

    def add_ranking(self, name, score, stage_id=1):
        all_data = {}
        if os.path.exists(self.ranking_file):
            try:
                with open(self.ranking_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        all_data = loaded
            except Exception:
                all_data = {}

        stage_key = str(stage_id)
        if stage_key not in all_data:
            all_data[stage_key] = []
            
        stage_rankings = all_data[stage_key]
        
        stage_rankings.append({'name': name or 'PLAYER', 'score': int(score)})
        stage_rankings = sorted(stage_rankings, key=lambda x: x['score'], reverse=True)[:20]
        
        all_data[stage_key] = stage_rankings
        
        with open(self.ranking_file, 'w', encoding='utf-8') as f: 
            json.dump(all_data, f, ensure_ascii=False, indent=2)
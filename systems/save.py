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

    def load_rankings(self):
        if not os.path.exists(self.ranking_file): 
            return []
        
        with open(self.ranking_file, 'r', encoding='utf-8') as f: 
            return json.load(f)
        
    def add_ranking(self, name, score):
        data = self.load_rankings()
        data.append({'name': name or 'PLAYER', 'score': int(score)})
        data = sorted(data, key=lambda x: x['score'], reverse=True)[:20] #상위 20명만 유지
        with open(self.ranking_file, 'w', encoding='utf-8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=2)

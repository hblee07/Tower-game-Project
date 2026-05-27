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
        """특정 스테이지의 랭킹 목록을 불러옵니다."""
        if not os.path.exists(self.ranking_file): 
            return []
        
        try:
            with open(self.ranking_file, 'r', encoding='utf-8') as f: 
                all_data = json.load(f)
                
            if isinstance(all_data, dict):
                # 💡 [가장 중요] str(stage_id)를 해서 "1" 같은 문자열 키로 꺼내야 합니다!
                # 그리고 꺼낸 데이터가 리스트가 맞는지 확실하게 검증합니다.
                res = all_data.get(str(stage_id), [])
                if isinstance(res, list):
                    return res
            return []
        except Exception as e:
            # 혹시 에러가 나서 빈 배열이 리턴되는지 콘솔에서 확인용
            print(f"랭킹 로드 중 예외 발생: {e}") 
            return []
        
    # 🔍 save_manager.py 내부의 add_ranking 메서드를 아래와 같이 수정해야 합니다!

    def add_ranking(self, name, score, stage_id=1): # 👈 여기에 stage_id=1이 반드시 있어야 합니다!
        """특정 스테이지에 새로운 랭킹 기록을 추가하고 상위 20명만 유지합니다."""
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
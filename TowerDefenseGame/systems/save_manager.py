import json
import os
from settings import SAVE_FILE, RANK_FILE

class SaveManager:
    @staticmethod
    def has_save():
        return os.path.exists(SAVE_FILE)

    @staticmethod
    def save(data):
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load():
        if not os.path.exists(SAVE_FILE):
            return None
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def delete_save():
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

    @staticmethod
    def rankings():
        if not os.path.exists(RANK_FILE):
            return []
        with open(RANK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def add_ranking(name, score, stage, wave):
        data = SaveManager.rankings()
        data.append({"name": name or "PLAYER", "score": int(score), "stage": stage, "wave": wave})
        data.sort(key=lambda x: x["score"], reverse=True)
        data = data[:20]
        with open(RANK_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

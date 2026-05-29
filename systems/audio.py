import os
from settings import BGM_PATH

class AudioManager:
    def __init__(self):
        self.enabled = False
        self.current = None
        try:
            import pygame
            if not pygame.mixer.get_init(): 
                pygame.mixer.init()
            self.pygame = pygame
            self.enabled = True
        except Exception:
            self.pygame = None
            self.enabled = False

    def play_bgm(self, name):
        if not self.enabled: 
            return
            
        self.pygame.mixer.music.stop()
        
        # 💡 아직 음악이 안 켜진 상태라면 title_music.mp3를 로드합니다.
        filename = BGM_PATH[name]
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', filename)
        
        try:
            self.pygame.mixer.music.load(path)
            self.pygame.mixer.music.set_volume(0.7)
            self.pygame.mixer.music.play(-1)  # 무한 반복
            self.current = "title_music"      # 현재 재생 상태 등록
        except Exception as e: 
            print(f"Audio Play Error (Title Music): {e}")
            pass

    def stop(self):
        if self.enabled:
            try: 
                self.pygame.mixer.music.stop()
                self.current = None
            except Exception:
                pass
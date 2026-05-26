import os

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
        """
        [개발용 임시 모드] 
        어떤 name이 들어오든 무조건 'title_music.mp3' 하나만 찾아 재생합니다.
        씬이 바뀔 때 음악이 끊기지 않고 계속 이어지도록 처리했습니다.
        """
        if not self.enabled: 
            return
            
        # 💡 하나의 파일만 재생할 것이므로, 이미 음악이 나오고 있다면 
        # 중복으로 다시 재생(처음부터 리스타트)하지 않고 그대로 이어서 들려줍니다.
        if self.current is not None:
            return
        
        # 💡 아직 음악이 안 켜진 상태라면 title_music.mp3를 로드합니다.
        filename = "title_music.mp3"
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', filename)
        
        try:
            self.pygame.mixer.music.load(path)
            self.pygame.mixer.music.set_volume(0.25)
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
import os

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
        name: 'title', 'game', 'end', 'ranking' 등의 문자열을 받아 
              해당 이름의 음악 파일을 재생합니다.
        """
        if not self.enabled or self.current == name: 
            return
        
        # 💡 인자로 받은 name을 활용해 파일명을 동적으로 결정합니다.
        filename = f"{name}.wav"
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', filename)
        
        try:
            self.pygame.mixer.music.load(path)
            self.pygame.mixer.music.set_volume(0.25)
            self.pygame.mixer.music.play(-1)  # -1은 무한 반복 재생
            self.current = name
        except Exception as e: 
            print(f"Audio Play Error ({name}): {e}")
            pass

    def stop(self):
        if self.enabled:
            try: 
                self.pygame.mixer.music.stop()
                self.current = None
            except Exception:
                pass
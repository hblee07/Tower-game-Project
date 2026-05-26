import os

class AudioManager:
    def __init__(self):
        self.enabled=False
        self.current=None
        try:
            import pygame
            if not pygame.mixer.get_init(): 
                pygame.mixer.init()
            self.pygame=pygame
            self.enabled=True
        except Exception:
            self.pygame=None
            self.enabled=False
    def play_bgm(self, name='bgm'):
        if not self.enabled or self.current==name: 
            return
        path=os.path.join(os.path.dirname(os.path.dirname(__file__)),'assets','bgm.wav')
        try:
            self.pygame.mixer.music.load(path)
            self.pygame.mixer.music.set_volume(0.25)
            self.pygame.mixer.music.play(-1)
            self.current=name
        except Exception: 
            pass
    def stop(self):
        if self.enabled:
            try: 
                self.pygame.mixer.music.stop()
            except Exception:
                pass

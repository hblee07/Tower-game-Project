import pygame
from settings import SCREEN_W, SCREEN_H, COLOR_TEXT

class PauseOverlay:
    def __init__(self): 
        self.font=pygame.font.SysFont(None,54)
        self.small=pygame.font.SysFont(None,26)
    def handle_event(self,event):
        if event.type==pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p): 
            return 'resume'
        return None
    def draw(self,surface):
        overlay=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        surface.blit(overlay,(0,0))
        title=self.font.render('PAUSED',True,COLOR_TEXT)
        surface.blit(title,title.get_rect(center=(SCREEN_W//2,SCREEN_H//2-20)))
        msg=self.small.render('Press ESC or P to resume',True,COLOR_TEXT)
        surface.blit(msg,msg.get_rect(center=(SCREEN_W//2,SCREEN_H//2+30)))

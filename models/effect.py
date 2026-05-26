import pygame, math
from settings import CELL_SIZE

class CircleEffect:
    def __init__(self, x, y, radius, color, duration=0.35):
        self.x=x
        self.y=y
        self.radius=radius
        self.color=color
        self.duration=duration
        self.age=0
        self.alive=True
    def update(self, dt):
        self.age += dt
        if self.age >= self.duration: 
            self.alive=False
    def draw(self, surface):
        a = max(0, int(180*(1-self.age/self.duration)))
        r = max(2, int(self.radius*(0.4+0.6*self.age/self.duration)))
        s = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a), (r+2,r+2), r, 3)
        surface.blit(s,(self.x-r-2,self.y-r-2))

class ExplosionEffect(CircleEffect):
    def __init__(self, grid_pos, radius):
        x=grid_pos[0]*CELL_SIZE+CELL_SIZE//2
        y=grid_pos[1]*CELL_SIZE+CELL_SIZE//2
        super().__init__(x,y,radius,(255,140,40),0.45)

class EffectManager:
    def __init__(self): 
        self.effects=[]
    def spawn(self, effect): 
        self.effects.append(effect)
    def update(self, dt):
        for e in self.effects:
            e.update(dt)
        self.effects=[e for e in self.effects if e.alive]
    def draw(self, surface):
        for e in self.effects: e.draw(surface)

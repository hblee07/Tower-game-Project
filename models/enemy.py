import pygame, math
from settings import CELL_SIZE, ENEMY_STATS

class Enemy:
    def __init__(self, kind, path, wave_scale=1.0):
        s=ENEMY_STATS[kind]
        self.kind=kind
        self.max_hp=int(s['hp']*wave_scale)
        self.hp=self.max_hp
        self.speed=s['speed']
        self.base_speed=s['speed']
        self.gold=s['gold']
        self.castle_damage=s['damage']
        self.color=s['color']
        self.path=path[:]
        self.path_index=0
        self.pixel_pos=list(self._center(path[0] if path else (0,0)))
        self.alive=True
        self.reached_end=False
        self.slow_timer=0
        self.slow_factor=1
        self.stun_timer=0
        self.path_progress=0
        self.regen_timer=0 if kind=='boss' else None

    def _center(self, cell): 
        return (cell[0]*CELL_SIZE+CELL_SIZE/2, cell[1]*CELL_SIZE+CELL_SIZE/2)
    
    def set_path(self, path):
        if path: self.path=path
        self.path_index=min(self.path_index, len(path)-1)

    def move(self, dt):
        if not self.alive or self.reached_end or not self.path: 
            return
        if self.stun_timer>0: 
            self.stun_timer-=dt
            return
        if self.slow_timer>0: 
            self.slow_timer-=dt
        else: 
            self.slow_factor=1
        if self.kind=='boss':
            self.regen_timer += dt
            if self.regen_timer >= 1.0: 
                self.hp=min(self.max_hp, self.hp+3)
                self.regen_timer=0
        speed=self.base_speed*self.slow_factor
        remain=speed*dt
        while remain>0 and self.path_index < len(self.path)-1:
            tx,ty=self._center(self.path[self.path_index+1])
            dx=tx-self.pixel_pos[0]
            dy=ty-self.pixel_pos[1]
            dist=math.hypot(dx,dy)
            if dist <= remain:
                self.pixel_pos=[tx,ty]
                self.path_index+=1
                self.path_progress=self.path_index
                remain-=dist
            elif dist>0:
                self.pixel_pos[0]+=dx/dist*remain
                self.pixel_pos[1]+=dy/dist*remain
                remain=0
        if self.path_index >= len(self.path)-1: 
            self.reached_end=True

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0: 
            self.alive=False

    def apply_slow(self, factor, duration): 
        self.slow_factor=min(self.slow_factor, factor)
        self.slow_timer=max(self.slow_timer, duration)

    def apply_stun(self, duration): 
        self.stun_timer=max(self.stun_timer, duration)
        
    def draw(self, surface):
        x, y = map(int, self.pixel_pos)
        radius = 8 if self.kind != 'boss' else 12
        
        # 1. 몬스터 본체 그리기
        pygame.draw.circle(surface, self.color, (x, y), radius)
        
        # 💡 체력이 만땅(최대 체력)이 아닐 때만 머리 위에 체력바를 그립니다.
        if self.hp < self.max_hp:
            # 체력바 검은색 배경 뒷부분 (24 픽셀 너비)
            pygame.draw.rect(surface, (20, 20, 20), (x - 12, y - radius - 8, 24, 4))
            
            # 남은 체력 비율 계산
            pct = max(0.0, self.hp) / self.max_hp
            # 초록색 남은 체력 바 그리기
            pygame.draw.rect(surface, (70, 220, 80), (x - 12, y - radius - 8, int(24 * pct), 4))
import pygame, math
from settings import CELL_SIZE

class BasicProjectile:
    def __init__(self, start_grid, target, damage, speed=260):
        self.x=start_grid[0]*CELL_SIZE+CELL_SIZE//2
        self.y=start_grid[1]*CELL_SIZE+CELL_SIZE//2
        self.target=target; self.damage=damage
        self.speed=speed
        self.alive=True
        self.color=(230,230,90)
    def update(self, dt):
        if not self.target.alive: 
            self.alive=False; return
        tx,ty=self.target.pixel_pos
        dx=tx-self.x
        dy=ty-self.y
        dist=math.hypot(dx,dy)
        if dist < max(6,self.speed*dt): 
            self.target.take_damage(self.damage)
            self.alive=False; return
        self.x += dx/dist*self.speed*dt
        self.y += dy/dist*self.speed*dt
    def draw(self, surface): 
        pygame.draw.circle(surface,self.color,(int(self.x),int(self.y)),4)

class BombProjectile(BasicProjectile):
    def __init__(self, start_grid, target, damage, radius): 
        super().__init__(start_grid,target,damage,220)
        self.radius=radius
        self.enemies=[]
        self.color=(255,120,40)
    def set_enemies(self,enemies): 
        self.enemies=enemies
    def update(self, dt):
        if not self.target.alive: 
            self.alive=False; return
        tx,ty=self.target.pixel_pos
        dx=tx-self.x
        dy=ty-self.y
        dist=math.hypot(dx,dy)
        if dist < max(6,self.speed*dt):
            for e in self.enemies:
                if e.alive and math.hypot(e.pixel_pos[0]-tx,e.pixel_pos[1]-ty)<=self.radius: 
                    e.take_damage(self.damage)
            self.alive=False
            return
        self.x += dx/dist*self.speed*dt
        self.y += dy/dist*self.speed*dt
    def draw(self,surface): 
        pygame.draw.circle(surface,self.color,(int(self.x),int(self.y)),6)

class LightningProjectile:
    def __init__(self, start_grid, target, damage, chain_count):
        self.start=(start_grid[0]*CELL_SIZE+CELL_SIZE//2,start_grid[1]*CELL_SIZE+CELL_SIZE//2)
        self.target=target
        self.damage=damage
        self.chain_count=chain_count
        self.age=0
        self.duration=0.12
        self.alive=True
        self.enemies=[]
        self.points=[]
    def set_enemies(self,enemies): 
        self.enemies=enemies
    def update(self, dt):
        if self.age==0: 
            self._hit_chain()
        self.age += dt
        if self.age>=self.duration: 
            self.alive=False
    def _hit_chain(self):
        current=self.target
        hit=[]
        self.points=[self.start]
        for _ in range(self.chain_count+1):
            if not current or not current.alive: 
                break
            current.take_damage(self.damage)
            current.apply_stun(0.18)
            hit.append(current)
            self.points.append(tuple(current.pixel_pos))
            candidates=[e for e in self.enemies if e.alive and e not in hit and math.hypot(e.pixel_pos[0]-current.pixel_pos[0],e.pixel_pos[1]-current.pixel_pos[1])<=55]
            current=min(candidates,key=lambda e: math.hypot(e.pixel_pos[0]-current.pixel_pos[0],e.pixel_pos[1]-current.pixel_pos[1]), default=None)
    def draw(self,surface):
        if len(self.points)>=2: 
            pygame.draw.lines(surface,(140,210,255),False,[(int(x),int(y)) for x,y in self.points],3)

class ThornProjectile(BasicProjectile):
    def __init__(self, start_grid, target, damage, slow_factor):
        super().__init__(start_grid, target, damage, speed=280)
        self.slow_factor = slow_factor
        self.color = (160, 110, 70)
        
    def update(self, dt):
        if not self.target.alive: 
            self.alive = False
            return
            
        tx, ty = self.target.pixel_pos
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        
        #부모의 충돌 로직을 가져와서 명중 시 슬로우 디버프를 함께 적용
        if dist < max(6, self.speed * dt): 
            self.target.take_damage(self.damage)
            self.target.apply_slow(self.slow_factor, 0.6) # 🐢 명중할 때 슬로우 발동!
            self.alive = False
            return
            
        self.x += dx / dist * self.speed * dt
        self.y += dy / dist * self.speed * dt

    def draw(self, surface):
        if not self.alive: return
        x, y = int(self.x), int(self.y)
        points = [(x, y - 7), (x - 6, y + 5), (x + 6, y + 5)]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (60, 40, 20), points, 1)
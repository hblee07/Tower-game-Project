import pygame, math
from settings import CELL_SIZE

class BasicProjectile:
    def __init__(self, start_grid, target, damage, speed=260, owner_tower=None):
        self.x=start_grid[0]*CELL_SIZE+CELL_SIZE//2
        self.y=start_grid[1]*CELL_SIZE+CELL_SIZE//2
        self.target=target; self.damage=damage
        self.speed=speed
        self.alive=True
        self.color=(230,230,90)
        self.owner_tower = owner_tower

    def update(self, dt):
        if not self.target.alive: 
            self.alive=False
            return
        tx,ty=self.target.pixel_pos
        dx=tx-self.x
        dy=ty-self.y
        dist=math.hypot(dx,dy)
        if dist < max(6,self.speed*dt): 
            self.target.take_damage(self.damage)
            if self.owner_tower:
                self.owner_tower.add_skill_gauge(self.damage)
                
            self.alive=False; return
        self.x += dx/dist*self.speed*dt
        self.y += dy/dist*self.speed*dt
    def draw(self, surface): 
        pygame.draw.circle(surface,self.color,(int(self.x),int(self.y)),4)

class BombProjectile(BasicProjectile):
    def __init__(self, start_grid, target, damage, radius, owner_tower): 
        super().__init__(start_grid, target, damage, 220, owner_tower)
        self.radius = radius
        self.enemies = []
        self.color = (255, 120, 40)
        
        self.state = 'moving'
        self.wait_timer = 0.2
        self.explode_duration = 0.2
        self.explode_timer = 0
        self.damage_dealt = False

    def set_enemies(self, enemies): 
        self.enemies = enemies

    def update(self, dt):
        tx, ty = self.target.pixel_pos
        
        if self.state == 'moving':
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            
            if dist < max(6, self.speed * dt):
                self.x, self.y = tx, ty
                self.state = 'waiting'
            else:
                self.x += dx / dist * self.speed * dt
                self.y += dy / dist * self.speed * dt
                
        elif self.state == 'waiting':
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.state = 'exploding'
                
        elif self.state == 'exploding':

            if not self.damage_dealt:
                total_damage = 0 
                for e in self.enemies:
                    if e.alive and math.hypot(e.pixel_pos[0] - self.x, e.pixel_pos[1] - self.y) <= self.radius: 
                        e.take_damage(self.damage)
                        total_damage += self.damage
                if self.owner_tower and total_damage > 0:
                    self.owner_tower.add_skill_gauge(total_damage)
                    
                self.damage_dealt = True
            

            self.explode_timer += dt
            if self.explode_timer >= self.explode_duration:
                self.alive = False

    def draw(self, surface):
        if self.state in ['moving', 'waiting']:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 6)
            
        elif self.state == 'exploding':
            progress = min(1.0, self.explode_timer / self.explode_duration)
            current_radius = self.radius * progress
            cx, cy = int(self.x), int(self.y)
            max_r = int(self.radius) + 2
            
            s = pygame.Surface((max_r * 2, max_r * 2), pygame.SRCALPHA)
            center = (max_r, max_r)
            
            pygame.draw.circle(s, (255, 120, 40, 100), center, int(current_radius))
            pygame.draw.circle(s, (255, 80, 20, 255), center, int(current_radius), max(1, int(3 * (1 - progress))))
            
            surface.blit(s, (cx - max_r, cy - max_r))

class LightningProjectile:
    def __init__(self, start_grid, target, damage, chain_count, owner_tower):
        self.start=(start_grid[0]*CELL_SIZE+CELL_SIZE//2,start_grid[1]*CELL_SIZE+CELL_SIZE//2)
        self.target=target
        self.damage=damage
        self.chain_count=chain_count
        self.owner_tower = owner_tower
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
        total_damage = 0
        
        for _ in range(self.chain_count+1):
            if not current or not current.alive: 
                break

            current.take_damage(self.damage)
            current.apply_stun(0.18)
            
            total_damage += self.damage 
            hit.append(current)
            self.points.append(tuple(current.pixel_pos))
            
            candidates=[e for e in self.enemies if e.alive and e not in hit and math.hypot(e.pixel_pos[0]-current.pixel_pos[0],e.pixel_pos[1]-current.pixel_pos[1])<=55]
            current=min(candidates,key=lambda e: math.hypot(e.pixel_pos[0]-current.pixel_pos[0],e.pixel_pos[1]-current.pixel_pos[1]), default=None)
            
        if self.owner_tower and total_damage > 0:
            self.owner_tower.add_skill_gauge(total_damage)

    def draw(self,surface):
        if len(self.points)>=2: 
            pygame.draw.lines(surface,(140,210,255),False,[(int(x),int(y)) for x,y in self.points],3)

class ThornProjectile(BasicProjectile):
    def __init__(self, start_grid, target, damage, slow_factor, owner_tower):
        super().__init__(start_grid, target, damage, speed=280, owner_tower=owner_tower)
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
        
        if dist < max(6, self.speed * dt): 
            self.target.take_damage(self.damage)
            self.target.apply_slow(self.slow_factor, 0.6) 
            if self.owner_tower:
                self.owner_tower.add_skill_gauge(self.damage)
                
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
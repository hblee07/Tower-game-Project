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
        super().__init__(start_grid, target, damage, 220)
        self.radius = radius
        self.enemies = []
        self.color = (255, 120, 40)
        
        # 상태 제어를 위한 변수들 추가
        self.state = 'moving'         # 현재 상태: 'moving', 'waiting', 'exploding'
        self.wait_timer = 0.2         # 목표 도달 후 머무는 시간 (0.2초)
        self.explode_duration = 0.2   # 폭발 이펙트가 퍼지는 시간
        self.explode_timer = 0        # 폭발 진행 시간 추적용
        self.damage_dealt = False     # 데미지 중복 적용 방지

    def set_enemies(self, enemies): 
        self.enemies = enemies

    def update(self, dt):
        tx, ty = self.target.pixel_pos
        
        if self.state == 'moving':
            # 1. 목표 위치로 이동
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            
            if dist < max(6, self.speed * dt):
                self.x, self.y = tx, ty
                self.state = 'waiting' # 목표 지점 도달 시 대기 상태로 전환
            else:
                self.x += dx / dist * self.speed * dt
                self.y += dy / dist * self.speed * dt
                
        elif self.state == 'waiting':
            # 2. 0.2초 동안 제자리에 머무름
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.state = 'exploding'
                
        elif self.state == 'exploding':
            # 3. 폭발 및 데미지 판정 (1회만 적용)
            if not self.damage_dealt:
                for e in self.enemies:
                    if e.alive and math.hypot(e.pixel_pos[0] - self.x, e.pixel_pos[1] - self.y) <= self.radius: 
                        e.take_damage(self.damage)
                self.damage_dealt = True
            
            # 폭발 이펙트 지속시간 체크
            self.explode_timer += dt
            if self.explode_timer >= self.explode_duration:
                self.alive = False # 이펙트 끝나면 투사체 삭제

    def draw(self, surface):
        if self.state in ['moving', 'waiting']:
            # 이동 중이거나 대기 중일 때는 원래 투사체 모습 유지
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 6)
            
        elif self.state == 'exploding':
            # 폭발 진행률 (0.0 ~ 1.0)
            progress = min(1.0, self.explode_timer / self.explode_duration)
            current_radius = self.radius * progress
            
            # 궁극기처럼 퍼지는 폭발 이펙트 그리기
            cx, cy = int(self.x), int(self.y)
            max_r = int(self.radius) + 2
            
            # 투명도가 있는 원을 그리기 위해 별도 Surface 사용
            s = pygame.Surface((max_r * 2, max_r * 2), pygame.SRCALPHA)
            center = (max_r, max_r)
            
            # 반투명하게 칠해진 안쪽 원
            pygame.draw.circle(s, (255, 120, 40, 100), center, int(current_radius))
            # 뚜렷한 바깥쪽 테두리 선
            pygame.draw.circle(s, (255, 80, 20, 255), center, int(current_radius), max(1, int(3 * (1 - progress))))
            
            surface.blit(s, (cx - max_r, cy - max_r))

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
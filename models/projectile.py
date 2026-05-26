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
        self.owner_tower = owner_tower # 부모 클래스에도 owner_tower 기본값 추가

    def update(self, dt):
        if not self.target.alive: 
            self.alive=False; return
        tx,ty=self.target.pixel_pos
        dx=tx-self.x
        dy=ty-self.y
        dist=math.hypot(dx,dy)
        if dist < max(6,self.speed*dt): 
            # 🎯 [Hit 시점] 단일 적 명중
            self.target.take_damage(self.damage)
            
            # 주인 타워가 있다면 게이지 상승
            if self.owner_tower:
                self.owner_tower.add_skill_gauge(self.damage)
                
            self.alive=False; return
        self.x += dx/dist*self.speed*dt
        self.y += dy/dist*self.speed*dt
    def draw(self, surface): 
        pygame.draw.circle(surface,self.color,(int(self.x),int(self.y)),4)

class BombProjectile(BasicProjectile):
    def __init__(self, start_grid, target, damage, radius, owner_tower): 
        # 부모 생성자에 owner_tower를 전달하도록 수정 (마지막 인자)
        super().__init__(start_grid, target, damage, 220, owner_tower)
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
            # 3. 💥 [Hit 시점] 폭발 및 데미지 판정 (1회만 적용)
            if not self.damage_dealt:
                total_damage = 0 # 이번 폭발로 준 총 데미지 계산용
                for e in self.enemies:
                    if e.alive and math.hypot(e.pixel_pos[0] - self.x, e.pixel_pos[1] - self.y) <= self.radius: 
                        e.take_damage(self.damage)
                        total_damage += self.damage # 광역 데미지 누적
                        
                # 펑 터지면서 맞춘 모든 적의 데미지 합산을 타워 게이지로!
                if self.owner_tower and total_damage > 0:
                    self.owner_tower.add_skill_gauge(total_damage)
                    
                self.damage_dealt = True
            
            # 폭발 이펙트 지속시간 체크
            self.explode_timer += dt
            if self.explode_timer >= self.explode_duration:
                self.alive = False # 이펙트 끝나면 투사체 삭제

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
        total_damage = 0 # ⚡ 전기가 튕기면서 준 총 데미지 계산용
        
        for _ in range(self.chain_count+1):
            if not current or not current.alive: 
                break
            # 🎯 [Hit 시점] 체인 라이트닝 명중
            current.take_damage(self.damage)
            current.apply_stun(0.18)
            
            total_damage += self.damage # 튕길 때마다 데미지 누적
            hit.append(current)
            self.points.append(tuple(current.pixel_pos))
            
            candidates=[e for e in self.enemies if e.alive and e not in hit and math.hypot(e.pixel_pos[0]-current.pixel_pos[0],e.pixel_pos[1]-current.pixel_pos[1])<=55]
            current=min(candidates,key=lambda e: math.hypot(e.pixel_pos[0]-current.pixel_pos[0],e.pixel_pos[1]-current.pixel_pos[1]), default=None)
            
        # 전기가 다 튕긴 후, 주인 타워의 게이지 상승
        if self.owner_tower and total_damage > 0:
            self.owner_tower.add_skill_gauge(total_damage)

    def draw(self,surface):
        if len(self.points)>=2: 
            pygame.draw.lines(surface,(140,210,255),False,[(int(x),int(y)) for x,y in self.points],3)

class ThornProjectile(BasicProjectile):
    def __init__(self, start_grid, target, damage, slow_factor, owner_tower):
        # 부모 생성자에 owner_tower를 올바르게 전달하도록 수정
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
            # 🎯 [Hit 시점] 가시 투사체 명중
            self.target.take_damage(self.damage)
            self.target.apply_slow(self.slow_factor, 0.6) 
            
            # 주인 타워가 있다면 게이지 상승
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
import pygame, math, random
from abc import ABCMeta, abstractmethod
from settings import TOWER_STATS, CELL_SIZE, MAX_MERGE_LEVEL, MAX_UPGRADE_LEVEL

class Tower(metaclass=ABCMeta):
    def __init__(self, tower_type, grid_pos, merge_level=1, upgrade_level=0):
        self.tower_type=tower_type
        self.grid_pos=tuple(grid_pos)
        self.merge_level=merge_level
        self.upgrade_level=upgrade_level
        s=TOWER_STATS[tower_type]
        self.base_damage=s['damage'][merge_level-1]
        self.damage=self.base_damage
        self.attack_range=s['attack_range']
        self.attack_speed=s['attack_speed']
        self.skill_cooldown_max=s['skill_cooldown']
        self.attack_timer=0
        self.skill_gauge=0
        for _ in range(upgrade_level): 
            self._apply_upgrade()
    
    def update(self,dt,enemies):
        if self.attack_speed<=0:
            return []
        self.attack_timer += dt
        if self.attack_timer >= 1/self.attack_speed:
            self.attack_timer=0
            target=self._find_target(enemies)
            if target: 
                return self._fire(target)
        return []
    
    def add_skill_gauge(self, damage_deal):
        self.skill_gauge = min(self.skill_cooldown_max, self.skill_gauge + damage_deal)
    
    def _find_target(self,enemies):
        in_range=[e for e in enemies if e.alive and self._distance_to(e)<=self.attack_range*CELL_SIZE]
        return max(in_range,key=lambda e:e.path_progress, default=None)
    
    def _distance_to(self,e):
        cx=self.grid_pos[0]*CELL_SIZE+CELL_SIZE//2
        cy=self.grid_pos[1]*CELL_SIZE+CELL_SIZE//2
        return math.hypot(e.pixel_pos[0]-cx,e.pixel_pos[1]-cy)
    
    @abstractmethod
    def _fire(self,target):
        pass
    
    @abstractmethod
    def use_skill(self,enemies,grid):
        pass
    
    def skill_ready(self): 
        return self.skill_gauge>=self.skill_cooldown_max
    
    def skill_cooldown_ratio(self): 
        return 1 if self.skill_cooldown_max==0 else self.skill_gauge/self.skill_cooldown_max
    
    def upgrade_cost(self): 
        return TOWER_STATS[self.tower_type]['upgrade_base']*(self.upgrade_level+1)
    
    def can_upgrade(self): 
        return self.upgrade_level < MAX_UPGRADE_LEVEL
    
    def upgrade(self,economy):
        if not self.can_upgrade(): 
            return False
        cost=self.upgrade_cost()
        if not economy.spend(cost): 
            return False
        self.upgrade_level += 1
        self._apply_upgrade()
        return True
    
    def _apply_upgrade(self): 
        self.damage=int(self.damage*1.1+3)
        self.attack_range*=1.04
    
    def sell_value(self): 
        return int(TOWER_STATS[self.tower_type]['cost'][self.merge_level-1]*TOWER_STATS[self.tower_type]['sell_ratio'] + self.upgrade_level*25)
    
    def sell(self,economy): 
        economy.earn(self.sell_value())

    def draw(self,surface):
        px=self.grid_pos[0]*CELL_SIZE
        py=self.grid_pos[1]*CELL_SIZE
        self._draw_body(surface,px,py)
        font=pygame.font.SysFont(None,14)
        surface.blit(font.render(str(self.merge_level),True,(255,255,255)),(px+CELL_SIZE-10,py+1))
        if self.upgrade_level: 
            surface.blit(font.render('+'+str(self.upgrade_level),True,(255,240,80)),(px+1,py+1))

    def draw_range(self,surface):
        cx=self.grid_pos[0]*CELL_SIZE+CELL_SIZE//2
        cy=self.grid_pos[1]*CELL_SIZE+CELL_SIZE//2
        r=int(self.attack_range*CELL_SIZE)
        s=pygame.Surface((r*2+2,r*2+2),pygame.SRCALPHA)
        pygame.draw.circle(s,(255,255,255,45),(r+1,r+1),r)
        pygame.draw.circle(s,(255,255,255,130),(r+1,r+1),r,1)
        surface.blit(s,(cx-r-1,cy-r-1))

    def to_dict(self): 
        return {'type':self.tower_type,'grid_pos':list(self.grid_pos),'merge_level':self.merge_level,'upgrade_level':self.upgrade_level}
    @staticmethod
    def from_dict(data):
        return {'bomb':BombTower,'lightning':LightningTower,'thorn':ThornTower,'random':RandomTower}[data['type']](tuple(data['grid_pos']),data['merge_level'],data.get('upgrade_level',0))

# 투사체(Projectile)가 목표물의 좌표(pixel_pos)를 정상적으로 읽을 수 있도록 돕는 더미 클래스
class DummyTarget:
    def __init__(self, pos):
        self.pixel_pos = pos
        self.alive = True
        self.path_progress = 0

class BombTower(Tower):
    def __init__(self, grid_pos, merge_level=1, upgrade_level=0): 
        super().__init__('bomb', grid_pos, merge_level, upgrade_level)
        self.bomb_radius = (1.2 + 0.35 * merge_level) * CELL_SIZE

    def _draw_body(self, s, px, py): 
        pygame.draw.circle(s, (215, 95, 45), (px + CELL_SIZE // 2, py + CELL_SIZE // 2), CELL_SIZE // 2 - 3)

    def _fire(self, target):
        from models.projectile import BombProjectile
        
        # 1. 타워 중심 좌표 계산
        cx = self.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
        cy = self.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        
        # 2. 공격 범위(attack_range) 내의 랜덤한 각도와 거리 산출
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, self.attack_range * CELL_SIZE)
        
        random_px = cx + math.cos(angle) * dist
        random_py = cy + math.sin(angle) * dist
        
        # 3. 가짜 타겟(DummyTarget) 생성 후 랜덤 좌표 부여
        # 적의 위치가 아닌 범위 내 엉뚱한(랜덤) 곳으로 폭탄을 던집니다.
        dummy_target = DummyTarget((random_px, random_py))
        
        return [BombProjectile(self.grid_pos, dummy_target, self.damage, self.bomb_radius, self)]
    
    def use_skill(self, enemies, grid):
        if not self.skill_ready() or not grid.path: 
            return False
            
        from models.effect import ExplosionEffect
        
        # 1. 타워 중심 좌표
        my_cx = self.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
        my_cy = self.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        
        # 2. 공격 범위 내에 존재하는 적의 이동 경로(path)만 필터링
        valid_path_cells = []
        for cell in grid.path:
            cell_cx, cell_cy = grid.grid_to_pixel_center(*cell)
            if math.hypot(cell_cx - my_cx, cell_cy - my_cy) <= self.attack_range * CELL_SIZE:
                valid_path_cells.append(cell)
        
        # 만약 사거리 내에 경로가 하나도 없다면 스킬 발동을 취소 (쿨타임 보존)
        if not valid_path_cells:
            return False
            
        # 3. 사거리 내 경로 중 랜덤한 한 칸을 지정하여 초거대 폭탄 투하
        target_cell = random.choice(valid_path_cells)
        cx, cy = grid.grid_to_pixel_center(*target_cell)
        
        # 초거대 폭탄 스펙 (기본 반경의 5배, 데미지 10배 - 밸런스에 맞게 조절 가능)
        massive_radius = self.bomb_radius * 5.0
        massive_damage = self.damage * 10
        
        for e in enemies:
            if e.alive and math.hypot(e.pixel_pos[0] - cx, e.pixel_pos[1] - cy) <= massive_radius: 
                e.take_damage(massive_damage)
                
        if grid.effect_manager: 
            grid.effect_manager.spawn(ExplosionEffect(target_cell, massive_radius))
            
        self.skill_gauge = 0
        return True

class LightningTower(Tower):
    def __init__(self,grid_pos,merge_level=1,upgrade_level=0): 
        super().__init__('lightning',grid_pos,merge_level,upgrade_level)
        self.chain_count=TOWER_STATS['lightning']['chain_count'][merge_level-1]

    def _draw_body(self,s,px,py): 
        pygame.draw.polygon(s,(80,180,255),[(px+10,py+2),(px+5,py+12),(px+13,py+12),(px+8,py+19),(px+18,py+8),(px+11,py+8)])
    
    def _fire(self,target):
        from models.projectile import LightningProjectile
        return [LightningProjectile(self.grid_pos,target,self.damage,self.chain_count, self)]
    
    def use_skill(self,enemies,grid):
        if not self.skill_ready(): 
            return False
        for e in enemies:
            if e.alive and self._distance_to(e)<=self.attack_range*CELL_SIZE*1.6: 
                e.take_damage(self.damage*2)
                e.apply_stun(0.8)
        self.skill_gauge=0
        return True

class ThornTower(Tower):
    def __init__(self, grid_pos, merge_level=1, upgrade_level=0): 
        # 부모 생성자를 호출하면서 settings.py의 공속(1.5 등)을 정상적으로 주입받습니다.
        super().__init__('thorn', grid_pos, merge_level, upgrade_level)
        self.slow_factor = TOWER_STATS['thorn']['slow_factor'][merge_level-1]

    def _draw_body(self, s, px, py): 
        pygame.draw.rect(s, (75, 155, 65), (px + 3, py + 3, CELL_SIZE - 6, CELL_SIZE - 6))
        pygame.draw.line(s, (210, 255, 120), (px + 4, py + 16), (px + 16, py + 4), 2)

    def _fire(self, target): 
        # 순환 참조 방지 내부 임포트
        from models.projectile import ThornProjectile
        
        # 🎯 발사할 때 즉시 데미지를 주지 않고, 투사체 오브젝트만 담아서 보냅니다.
        # slow_factor 정보도 투사체에 함께 넘겨주어 명중 시점에 슬로우가 걸리도록 만듭니다.
        return [ThornProjectile(self.grid_pos, target, self.damage, self.slow_factor, self)]
    
    def use_skill(self, enemies, grid):
        if not self.skill_ready(): 
            return False
        grid.activate_thorn_overlay(self.grid_pos, self.attack_range, 5.0)
        self.skill_gauge = 0
        return True
        
        # 💥 [궁극기] 기존에 짜두신 가시밭길 오버레이 활성화 기능을 그대로 수행합니다.
        # 이전에 해결한 Enemy 소수점 데미지 패치 덕분에 이제 이 가시밭길 위에서 몬스터 피가 정상적으로 깎입니다!

class RandomTower(Tower):
    def __init__(self,grid_pos,merge_level=1,upgrade_level=0): 
        super().__init__('random',grid_pos,merge_level,upgrade_level)
        self.burst_timer=0

    def _draw_body(self,s,px,py): 
        pygame.draw.rect(s,(170,120,220),(px+3,py+3,CELL_SIZE-6,CELL_SIZE-6))
        pygame.draw.circle(s,(250,230,120),(px+10,py+10),4)

    def _fire(self,target):
        from models.projectile import BasicProjectile
        return [BasicProjectile(self.grid_pos,target,self.damage*(3 if self.burst_timer>0 else 1))]
    
    def update(self,dt,enemies): 
        self.burst_timer=max(0,self.burst_timer-dt)
        return super().update(dt,enemies)
    
    def use_skill(self,enemies,grid):
        if not self.skill_ready(): 
            return False
        self.burst_timer=3.0
        self.skill_gauge=0
        return True
    
    def transform(self): 
        return random.choice([BombTower,LightningTower,ThornTower])(self.grid_pos,3,self.upgrade_level)

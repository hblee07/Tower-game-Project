import pygame, math, random
from abc import ABCMeta, abstractmethod
from settings import TOWER_STATS, CELL_SIZE, MAX_MERGE_LEVEL, MAX_UPGRADE_LEVEL

class Tower(metaclass=ABCMeta):
    def __init__(self, tower_type, grid_pos, merge_level=1, upgrade_level=0):
        self.tower_type=tower_type
        self.grid_pos=tuple(grid_pos)
        self.alive = True
        self.merge_level=merge_level
        self.upgrade_level=upgrade_level
        s=TOWER_STATS[tower_type]
        self.base_damage=s['damage'][merge_level - 1]
        self.damage=self.base_damage
        self.attack_range=s['attack_range'][merge_level - 1]
        self.attack_speed=s['attack_speed'][merge_level - 1]
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
    
    def _find_target(self, enemies):
        in_range = [e for e in enemies if e.alive and self._distance_to(e) <= self.attack_range * CELL_SIZE]
        return max(in_range, key=lambda e: e.path_index, default=None)
    
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
        return int(TOWER_STATS[self.tower_type]['upgrade_base']*(0.2*self.upgrade_level+1))
    
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
        self.damage=int(self.damage*1.05)
    
    def sell_value(self): 
        return int(TOWER_STATS[self.tower_type]['cost'][self.merge_level-1]*TOWER_STATS[self.tower_type]['sell_ratio'] + self.upgrade_level*25)
    
    def sell(self,economy): 
        economy.earn(self.sell_value())

    def draw(self, surface):
        px = self.grid_pos[0] * CELL_SIZE
        py = self.grid_pos[1] * CELL_SIZE
        
        self._draw_body(surface, px, py)
        font = pygame.font.SysFont(None, 14)
        surface.blit(font.render(str(self.merge_level), True, (255, 255, 255)), (px + CELL_SIZE - 18, py + 1))
        if self.upgrade_level: 
            surface.blit(font.render('+' + str(self.upgrade_level), True, (255, 240, 80)), (px + CELL_SIZE -10, py + 1))

        ratio = self.skill_cooldown_ratio()
        
        if ratio >= 1.0:
            bar_color = (50, 150, 255)
        elif ratio >= 0.7:
            bar_color = (70, 220, 80)
        elif ratio >= 0.2:
            bar_color = (250, 210, 60)
        else:
            bar_color = (235, 60, 60)

        bar_width = CELL_SIZE - 6
        bar_height = 4
        bar_x = px + 3
        bar_y = py - 7

        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        
        fill_width = int(bar_width * ratio)
        if fill_width > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_width, bar_height))

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

class DummyTarget:
    def __init__(self, pos):
        self.pixel_pos = pos
        self.alive = True
        self.path_index = 0 

class BombTower(Tower):
    def __init__(self, grid_pos, merge_level=1, upgrade_level=0): 
        super().__init__('bomb', grid_pos, merge_level, upgrade_level)
        self.bomb_radius = (1.4 + 0.35 * merge_level) * CELL_SIZE

    def _draw_body(self, s, px, py): 
        pygame.draw.circle(s, (215, 95, 45), (px + CELL_SIZE // 2, py + CELL_SIZE // 2), CELL_SIZE // 2 - 3)

    def _fire(self, target):
        from models.projectile import BombProjectile
        
        cx = self.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
        cy = self.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, self.attack_range * CELL_SIZE)
        
        random_px = cx + math.cos(angle) * dist
        random_py = cy + math.sin(angle) * dist
        dummy_target = DummyTarget((random_px, random_py))
        
        return [BombProjectile(self.grid_pos, dummy_target, self.damage, self.bomb_radius, self)]
    
    def use_skill(self, enemies, grid):
        if not self.skill_ready() or not grid.path: 
            return False
            
        from models.effect import ExplosionEffect
        
        my_cx = self.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
        my_cy = self.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        
        valid_path_cells = []
        for cell in grid.path:
            cell_cx, cell_cy = grid.grid_to_pixel_center(*cell)
            if math.hypot(cell_cx - my_cx, cell_cy - my_cy) <= self.attack_range * CELL_SIZE:
                valid_path_cells.append(cell)

        if not valid_path_cells:
            return False
            
        
        target_cell = random.choice(valid_path_cells)
        cx, cy = grid.grid_to_pixel_center(*target_cell)
        
        
        massive_radius = self.bomb_radius * 5.0
        massive_damage = self.damage * 7
        
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
        super().__init__('thorn', grid_pos, merge_level, upgrade_level)
        self.slow_factor = TOWER_STATS['thorn']['slow_factor'][merge_level-1]

    def _draw_body(self, s, px, py): 
        pygame.draw.rect(s, (75, 155, 65), (px + 3, py + 3, CELL_SIZE - 6, CELL_SIZE - 6))
        pygame.draw.line(s, (210, 255, 120), (px + 4, py + 16), (px + 16, py + 4), 2)

    def _fire(self, target): 
        from models.projectile import ThornProjectile
        return [ThornProjectile(self.grid_pos, target, self.damage, self.slow_factor, self)]
    
    def use_skill(self, enemies, grid):
        if not self.skill_ready(): 
            return False
        grid.activate_thorn_overlay(self.grid_pos, self.attack_range, 5.0)
        self.skill_gauge = 0
        return True
class RandomTower(Tower):
    def __init__(self,grid_pos,merge_level=1,upgrade_level=0): 
        super().__init__('random',grid_pos,merge_level,upgrade_level)
        self.burst_timer=0

    def _draw_body(self,s,px,py): 
        pygame.draw.rect(s,(170,120,220),(px+3,py+3,CELL_SIZE-6,CELL_SIZE-6))
        pygame.draw.circle(s,(250,230,120),(px+10,py+10),4)

    def _fire(self,target):
        from models.projectile import BasicProjectile
        return [BasicProjectile(self.grid_pos,target,self.damage*(3 if self.burst_timer>0 else 1),260,self)]
    
    def update(self,dt,enemies): 
        self.burst_timer=max(0,self.burst_timer-dt)
        return super().update(dt,enemies)
    
    def use_skill(self,enemies,grid):
        if not self.skill_ready(): 
            return False
        self.burst_timer=3.0
        self.skill_gauge=0
        return True
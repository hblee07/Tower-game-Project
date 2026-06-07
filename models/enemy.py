import pygame, math
from settings import *


_IMAGE_CACHE = {}

def get_image(path):
    global _IMAGE_CACHE
    if path not in _IMAGE_CACHE:
        try:
            full_path = f"assets/{path}"
            _IMAGE_CACHE[path] = pygame.image.load(full_path).convert_alpha()
        except pygame.error:

            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255, 0, 255), (0, 0, CELL_SIZE, CELL_SIZE))
            _IMAGE_CACHE[path] = surf
    return _IMAGE_CACHE[path]


#enemy의 베이스클래스
class BaseEnemy:
    def __init__(self, kind, path, wave_scale=1.0):
        s = ENEMY_STATS.get(kind, ENEMY_STATS['ghost_normal'])
        self.kind = kind
        self.is_boss = s['is_boss']
        
        self.max_hp = int(s['hp'] * wave_scale)
        self.hp = self.max_hp
        self.base_speed = s['speed']
        self.speed = self.base_speed
        self.gold = s['gold']
        self.castle_damage = s['damage']
        self.color = s['color']
        
        self.path = path[:]
        self.path_index = 0
        self.pixel_pos = list(self._center(path[0] if path else (0,0)))
        
        self.alive = True
        self.reached_end = False
        self.slow_timer = 0
        self.slow_factor = 1
        self.stun_timer = 0
        self.current_angle = 0

    def _center(self, cell): 
        return (cell[0]*CELL_SIZE+CELL_SIZE/2, cell[1]*CELL_SIZE+CELL_SIZE/2)

    def set_path(self, path):
        if not path: return
        if not self.path:
            self.path = path; self.path_index = 0
            self.pixel_pos = list(self._center(path[0]))
            return
            
        old_len = len(self.path)
        progress = self.path_index / old_len
        self.path = path
        new_len = len(self.path)
        new_idx = int(progress * new_len)
        self.path_index = max(0, min(new_idx, new_len - 1))
        self.pixel_pos = list(self._center(self.path[self.path_index]))

    def move(self, dt):
        if not self.alive or self.reached_end or not self.path: return
        if self.stun_timer > 0: 
            self.stun_timer -= dt
            return
        if self.slow_timer > 0: self.slow_timer -= dt
        else: self.slow_factor = 1

        speed = self.speed * self.slow_factor
        remain = speed * dt

        while remain > 0 and self.path_index < len(self.path)-1:
            tx, ty = self._center(self.path[self.path_index+1])
            dx = tx - self.pixel_pos[0]
            dy = ty - self.pixel_pos[1]
            dist = math.hypot(dx, dy)
            
            if dist > 0:
                self.current_angle = math.degrees(math.atan2(-dy, dx))

            if dist <= remain:
                self.pixel_pos = [tx, ty]
                self.path_index += 1
                remain -= dist
            elif dist > 0:
                self.pixel_pos[0] += dx/dist*remain
                self.pixel_pos[1] += dy/dist*remain
                remain = 0
                
        if self.path_index >= len(self.path)-1: 
            self.reached_end = True

    def take_damage(self, amount):
        if not self.alive: return
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def apply_slow(self, factor, duration): 
        self.slow_factor = min(self.slow_factor, factor)
        self.slow_timer = max(self.slow_timer, duration)

    def apply_stun(self, duration): 
        self.stun_timer = max(self.stun_timer, duration)

    def draw_health_bar(self, surface, x, y):
        if self.hp < self.max_hp and self.hp > 0:
            bar_w = CELL_SIZE // 2
            bar_x = x - bar_w // 2
            bar_y = y - (CELL_SIZE // 2) - 5
            pygame.draw.rect(surface, (20, 20, 20), (bar_x, bar_y, bar_w, 4))
            pct = max(0.0, self.hp) / self.max_hp
            color = (170, 80, 220) if self.is_boss else (70, 220, 80)
            pygame.draw.rect(surface, color, (bar_x, bar_y, int(bar_w * pct), 4))

    def draw(self, surface):
        x, y = map(int, self.pixel_pos)
        pygame.draw.circle(surface, self.color, (x, y), CELL_SIZE // 4)
        self.draw_health_bar(surface, x, y)



#유령Enemy
class GhostEnemy(BaseEnemy):
    def __init__(self, kind, path, wave_scale=1.0, ghost_color=None):
        super().__init__(kind, path, wave_scale)
        
        if ghost_color:
            self.color = ghost_color
        if self.is_boss:
            
            if ghost_color == COLOR_GHOST_RED:
                img = get_image('ghost_boss_red.png')  
                self.base_speed = GHOST_BOSS_SPEED[0]
            elif ghost_color == COLOR_GHOST_PINK:
                img = get_image('ghost_boss_pink.png')
                self.base_speed = GHOST_BOSS_SPEED[1]
            elif ghost_color == COLOR_GHOST_CYAN:  
                img = get_image('ghost_boss_cyan.png')
                self.base_speed = GHOST_BOSS_SPEED[2]
            else:
                img = get_image('ghost_boss_orange.png')
                self.base_speed = GHOST_BOSS_SPEED[3]
            self.speed = self.base_speed
            self.image = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))

    def draw(self, surface):
        if not self.alive: return
        
        if self.is_boss:
            x, y = map(int, self.pixel_pos)
            img_to_draw = self.image.copy()
            rect = img_to_draw.get_rect(center=(x, y))
            surface.blit(img_to_draw, rect)
            self.draw_health_bar(surface, x, y)
        else:
            super().draw(surface)


#로켓 Enemy

class RocketEnemy(BaseEnemy):
    def __init__(self, kind, path, wave_scale=1.0):
        super().__init__(kind, path, wave_scale)

        if self.is_boss:
            import os 
            full_path = os.path.join("assets", "rocket_boss.png")
            
            try:
                img = pygame.image.load(full_path).convert_alpha()
                self.image = pygame.transform.scale(img, (CELL_SIZE * img.get_width() // img.get_height(), CELL_SIZE))
                
            except pygame.error as e:
                print(f"Error loading rocket_boss.png : {e}")
                self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
                self.image.fill((255, 0, 255))

    def draw(self, surface):
        if not self.alive: return
        if self.is_boss:
            x, y = map(int, self.pixel_pos)

            rotated_img = pygame.transform.rotate(self.image, self.current_angle)
            rect = rotated_img.get_rect(center=(x, y))
            surface.blit(rotated_img, rect)
            self.draw_health_bar(surface, x, y)
        else:
            super().draw(surface)



#팩맨모양 enemy
class PacmanEnemy(BaseEnemy):
    def __init__(self, kind, path, wave_scale=1.0):
        super().__init__(kind, path, wave_scale)
        self.mouth_open_angle = 45 
        self.original_size = CELL_SIZE // 2

        self.is_dying = False
        self.death_effect_timer = 0
        self.death_effect_duration = 1.0
        self.target_tower = None
        
        self.current_size = self.original_size
        self.current_mouth_angle = self.mouth_open_angle
        self.death_angle = 0

    def take_damage(self, amount):
        if not self.alive or self.is_dying: return
        self.hp -= amount
        
        if self.hp <= 0:
            if self.is_boss:
                self.hp = 0
                self.is_dying = True
            else:
                self.alive = False

    def start_death_effect(self, target_tower):
        self.target_tower = target_tower
        if self.target_tower:
            tx, ty = self._center(self.target_tower.grid_pos)
            
            dx = tx - self.pixel_pos[0]
            dy = ty - self.pixel_pos[1]
            self.death_angle = math.degrees(math.atan2(-dy, dx))

    def move(self, dt):
        if self.is_dying:
            self._update_death_effect(dt)
            return
            
        super().move(dt)

    def _update_death_effect(self, dt):
        if not self.target_tower or not self.target_tower.alive:
            self.alive = False
            return

        self.death_effect_timer += dt
        progress = min(1.0, self.death_effect_timer / self.death_effect_duration)
        tx, ty = self._center(self.target_tower.grid_pos)
        
        dx = tx - self.pixel_pos[0]
        dy = ty - self.pixel_pos[1]
        dist = math.hypot(dx, dy)

        if progress < 0.8:
            eat_progress = progress / 0.8
            self.current_size = self.original_size + (dist * eat_progress)
            self.current_mouth_angle = self.mouth_open_angle + (180 - self.mouth_open_angle) * eat_progress
        else:
            close_progress = (progress - 0.8) / 0.2
            self.current_size = self.original_size + dist
            self.current_mouth_angle = 180 * (1.0 - close_progress)

        if progress >= 1.0:
            self.target_tower.alive = False
            self.alive = False

    def draw(self, surface):
        if not self.alive: return
        if not self.is_boss:
            super().draw(surface)
            return
        x, y = map(int, self.pixel_pos)

        angle = self.death_angle if self.is_dying else self.current_angle
        mouth = self.current_mouth_angle if self.is_dying else self.mouth_open_angle
        size = self.current_size if self.is_dying else self.original_size

        radius = int(size)
        start_angle = mouth / 2 + angle
        end_angle = 360 - (mouth / 2) + angle
        
        points = [(x, y)]
        num_points = 20
        for i in range(num_points + 1):
            ang = start_angle + (end_angle - start_angle) * (i / num_points)
            px = x + math.cos(math.radians(-ang)) * radius
            py = y + math.sin(math.radians(-ang)) * radius
            points.append((px, py))
            
        if len(points) > 2:
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, (0,0,0), points, 2)

        if not self.is_dying:
            self.draw_health_bar(surface, x, y)


def create_enemy(kind, path, wave_scale=1.0, ghost_color=None):
    if 'ghost' in kind:
        return GhostEnemy(kind, path, wave_scale, ghost_color)
    elif 'rocket' in kind:
        return RocketEnemy(kind, path, wave_scale)
    elif 'pacman' in kind:
        return PacmanEnemy(kind, path, wave_scale)
    else:
        return BaseEnemy(kind, path, wave_scale)
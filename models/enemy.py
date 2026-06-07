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
        """기본 그리기 (일반 도형). 자식 클래스에서 오버라이드 됨"""
        x, y = map(int, self.pixel_pos)
        pygame.draw.circle(surface, self.color, (x, y), CELL_SIZE // 4)
        self.draw_health_bar(surface, x, y)


# ==========================================
# 2. 유령 Enemy
# ==========================================
class GhostEnemy(BaseEnemy):
    def __init__(self, kind, path, wave_scale=1.0, ghost_color=None):
        super().__init__(kind, path, wave_scale)
        
        if ghost_color:
            self.color = ghost_color

        # 💡 보스일 때만 이미지 로드
        if self.is_boss:
            # 문자열('red')이 아니라 settings의 실제 색상 변수(튜플)와 비교해야 합니다!
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

            # 가져온 이미지를 CELL_SIZE(20x20) 크기로 강제 셋팅!
            self.image = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))

    def draw(self, surface):
        if not self.alive: return
        
        if self.is_boss:
            x, y = map(int, self.pixel_pos)
            img_to_draw = self.image.copy()
            
            # 이미 색상이 완벽히 칠해진 개별 이미지를 쓰므로 
            # 원본을 해치지 않으려면 아래 fill(BLEND_MULT) 라인은 주석 처리하거나 지우는 것을 추천합니다.
            # img_to_draw.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
                
            rect = img_to_draw.get_rect(center=(x, y))
            surface.blit(img_to_draw, rect)
            self.draw_health_bar(surface, x, y)
        else:
            super().draw(surface)

# ==========================================
# 3. 로켓 Enemy
# ==========================================
class RocketEnemy(BaseEnemy):
    def __init__(self, kind, path, wave_scale=1.0):
        super().__init__(kind, path, wave_scale)
        # 보스일 때만 이미지 로드
        if self.is_boss:
            # 💡 [핵심] 그냥 가져오는 것이 아니라 크기 조절 로직이 포함된 get_image를 써야 합니다.
            # 하지만 현재 get_image는 크기 조절을 안 하므로, 여기서 직접 조절합니다.
            
            # get_image 대신 여기서 직접 로드하고 스케일링하는 방법 A 적용:
            import os # 상단에 import os 추가 필요
            full_path = os.path.join("assets", "rocket_boss.png")
            
            try:
                # 1. 이미지 로드
                img = pygame.image.load(full_path).convert_alpha()
                
                # 💡 2. [크기 재설정] 원본 크기 상관없이 게임 셀 크기로 강제 축소/확대!
                # settings.py에 CELL_SIZE = 20 으로 되어 있으므로 20x20 크기가 됩니다.
                self.image = pygame.transform.scale(img, (CELL_SIZE * img.get_width() // img.get_height(), CELL_SIZE))
                
            except pygame.error as e:
                print(f"Error loading rocket_boss.png : {e}")
                # 파일 없을 때 핑크색 사각형 폴백 (이전 get_image 내부 로직 활용)
                self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
                self.image.fill((255, 0, 255))

    def draw(self, surface):
        if not self.alive: return
        
        # 보스면 회전하는 이미지를, 아니면 기본 도형을 그립니다.
        if self.is_boss:
            x, y = map(int, self.pixel_pos)
            # 💡 회전 시 중앙이 맞도록 rect 계산 필수
            rotated_img = pygame.transform.rotate(self.image, self.current_angle)
            rect = rotated_img.get_rect(center=(x, y))
            surface.blit(rotated_img, rect)
            self.draw_health_bar(surface, x, y)
        else:
            # 일반 로켓은 settings.py의 CELL_SIZE // 4 반경의 원으로 그림 (BaseEnemy 로직)
            super().draw(surface)


# ==========================================
# 4. 팩맨 Enemy
# ==========================================
class PacmanEnemy(BaseEnemy):
    def __init__(self, kind, path, wave_scale=1.0):
        super().__init__(kind, path, wave_scale)
        self.mouth_open_angle = 45 # 평소 입 벌린 각도
        self.original_size = CELL_SIZE // 2
        
        # 보스 전용 데스 이펙트 변수
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
                self.is_dying = True # 사망 이펙트 돌입
            else:
                self.alive = False

    def start_death_effect(self, target_tower):
        self.target_tower = target_tower
        if self.target_tower:
            # 💡 [수정] target_tower.pixel_pos 대신 부모의 _center 메서드와 타워의 grid_pos를 사용합니다.
            tx, ty = self._center(self.target_tower.grid_pos)
            
            dx = tx - self.pixel_pos[0]
            dy = ty - self.pixel_pos[1]
            self.death_angle = math.degrees(math.atan2(-dy, dx))

    def move(self, dt):
        # 데스 이펙트 중이면 이동 대신 이펙트 처리
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
        
        # 💡 [수정] 여기도 마찬가지로 픽셀 좌표를 계산하도록 수정합니다.
        tx, ty = self._center(self.target_tower.grid_pos)
        
        dx = tx - self.pixel_pos[0]
        dy = ty - self.pixel_pos[1]
        dist = math.hypot(dx, dy)

        if progress < 0.8: # 커지면서 입 벌림
            eat_progress = progress / 0.8
            self.current_size = self.original_size + (dist * eat_progress)
            self.current_mouth_angle = self.mouth_open_angle + (180 - self.mouth_open_angle) * eat_progress
        else: # 입 닫기
            close_progress = (progress - 0.8) / 0.2
            self.current_size = self.original_size + dist
            self.current_mouth_angle = 180 * (1.0 - close_progress)

        if progress >= 1.0:
            self.target_tower.alive = False # 타워 소멸
            self.alive = False # 팩맨 소멸

    def draw(self, surface):
        if not self.alive: return
        
        # 💡 [추가된 핵심 로직] 보스가 아닌 일반 팩맨은 기본 원으로 그리고 종료!
        if not self.is_boss:
            super().draw(surface)
            return
            
        # --- 아래는 보스 팩맨(is_boss == True)일 때만 실행됩니다 ---
        x, y = map(int, self.pixel_pos)
        
        # 상태에 따라 각도 및 크기 결정
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
            pygame.draw.polygon(surface, (0,0,0), points, 2) # 테두리

        if not self.is_dying:
            self.draw_health_bar(surface, x, y)


# ==========================================
# 5. Enemy 팩토리 함수 (WaveManager가 사용할 함수)
# ==========================================
def create_enemy(kind, path, wave_scale=1.0, ghost_color=None):
    """문자열 kind를 받아 알맞은 클래스의 인스턴스를 반환합니다."""
    if 'ghost' in kind:
        return GhostEnemy(kind, path, wave_scale, ghost_color)
    elif 'rocket' in kind:
        return RocketEnemy(kind, path, wave_scale)
    elif 'pacman' in kind:
        return PacmanEnemy(kind, path, wave_scale)
    else:
        # 기본 폴백
        return BaseEnemy(kind, path, wave_scale)
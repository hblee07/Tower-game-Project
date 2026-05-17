import math
import pygame
from settings import TILE_SIZE, ENEMY_DATA, WHITE, RED

class Enemy:
    def __init__(self, enemy_type, path, wave_multiplier=1.0):
        self.enemy_type = enemy_type
        data = ENEMY_DATA[enemy_type]
        self.max_hp = int(data["hp"] * wave_multiplier)
        self.hp = self.max_hp
        self.base_speed = data["speed"] * (0.92 + 0.035 * wave_multiplier)
        self.speed = self.base_speed
        self.reward = int(data["reward"] * wave_multiplier)
        self.castle_damage = data["damage"]
        self.color = data["color"]
        self.path = path[:]
        self.path_index = 0
        self.x, self.y = self.cell_center(path[0])
        self.dead = False
        self.reached_end = False
        self.slow_timer = 0
        self.slow_factor = 1.0
        self.boss_aura_timer = 0

    @staticmethod
    def cell_center(cell):
        r, c = cell
        return c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2

    @property
    def is_boss(self):
        return self.enemy_type.startswith("boss")

    def set_path(self, new_path):
        current = (int(self.y // TILE_SIZE), int(self.x // TILE_SIZE))
        if current in new_path:
            idx = new_path.index(current)
            self.path = new_path[idx:]
            self.path_index = 0

    def apply_slow(self, factor, seconds):
        if self.enemy_type == "boss_troll":
            factor = max(factor, 0.72)
        self.slow_factor = min(self.slow_factor, factor)
        self.slow_timer = max(self.slow_timer, seconds)

    def take_damage(self, amount):
        if self.enemy_type == "boss_orc":
            amount *= 0.82
        self.hp -= amount
        if self.hp <= 0:
            self.dead = True

    def update(self, dt):
        if self.dead or self.reached_end:
            return
        if self.slow_timer > 0:
            self.slow_timer -= dt
            self.speed = self.base_speed * self.slow_factor
        else:
            self.slow_factor = 1.0
            self.speed = self.base_speed
        if self.enemy_type == "boss_goblin":
            self.boss_aura_timer += dt
            if self.boss_aura_timer > 2.2:
                self.boss_aura_timer = 0
                self.base_speed *= 1.025
        if self.path_index >= len(self.path) - 1:
            self.reached_end = True
            return
        tx, ty = self.cell_center(self.path[self.path_index + 1])
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        step = self.speed * dt
        if dist <= step:
            self.x, self.y = tx, ty
            self.path_index += 1
            if self.path_index >= len(self.path) - 1:
                self.reached_end = True
        elif dist > 0:
            self.x += dx / dist * step
            self.y += dy / dist * step

    def draw(self, screen):
        radius = 8 if not self.is_boss else 13
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)
        if self.is_boss:
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), radius + 2, 2)
        w = 24 if not self.is_boss else 34
        h = 4
        x = self.x - w / 2
        y = self.y - radius - 10
        pygame.draw.rect(screen, RED, (x, y, w, h))
        pygame.draw.rect(screen, (70, 230, 90), (x, y, w * max(self.hp / self.max_hp, 0), h))

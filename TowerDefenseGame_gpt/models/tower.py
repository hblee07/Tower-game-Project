import math
import pygame
from settings import TILE_SIZE, TOWER_DATA, MAX_MERGE_LEVEL, MAX_UPGRADE_LEVEL, WHITE, YELLOW
from models.projectile import Projectile

class Tower:
    def __init__(self, tower_type, row, col):
        self.tower_type = tower_type
        self.row = row
        self.col = col
        self.merge_level = 1
        self.upgrade_level = 1
        self.cooldown_timer = 0
        self.skill_charge = 0
        self.skill_ready = False
        self.skill_effect_timer = 0

    @property
    def data(self):
        return TOWER_DATA[self.tower_type]

    @property
    def x(self):
        return self.col * TILE_SIZE + TILE_SIZE // 2

    @property
    def y(self):
        return self.row * TILE_SIZE + TILE_SIZE // 2

    @property
    def damage(self):
        return self.data["damage"] * (1 + 0.42 * (self.merge_level - 1)) * (1 + 0.24 * (self.upgrade_level - 1))

    @property
    def range(self):
        return self.data["range"] * (1 + 0.10 * (self.merge_level - 1))

    @property
    def cooldown(self):
        return max(0.12, self.data["cooldown"] * (1 - 0.04 * (self.upgrade_level - 1)))

    def upgrade_cost(self):
        if self.upgrade_level >= MAX_UPGRADE_LEVEL:
            return None
        return int(self.data["cost"] * (0.75 + self.upgrade_level * 0.55))

    def sell_value(self):
        return int(self.data["cost"] * 0.55 + self.upgrade_level * 22 + self.merge_level * 35)

    def can_merge_with(self, other):
        if not other:
            return False
        if self.tower_type != other.tower_type or self.merge_level != other.merge_level:
            return False
        if self.merge_level >= MAX_MERGE_LEVEL:
            return False
        return math.hypot(self.x - other.x, self.y - other.y) <= self.range

    def find_target(self, enemies):
        candidates = [e for e in enemies if not e.dead and not e.reached_end and math.hypot(e.x - self.x, e.y - self.y) <= self.range]
        if not candidates:
            return None
        return max(candidates, key=lambda e: e.path_index)

    def update(self, dt, enemies, projectiles, effects):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
        if self.skill_effect_timer > 0:
            self.skill_effect_timer -= dt
        if self.cooldown_timer <= 0:
            target = self.find_target(enemies)
            if target:
                self.fire(target, projectiles)
                self.cooldown_timer = self.cooldown
                self.skill_charge = min(100, self.skill_charge + 12 + 4 * self.merge_level)
                if self.skill_charge >= 100:
                    self.skill_ready = True

    def fire(self, target, projectiles):
        splash = self.data.get("splash", 0)
        slow = self.data.get("slow", 1.0)
        slow_time = self.data.get("slow_time", 0)
        projectiles.append(Projectile(self.x, self.y, target, self.damage, self.data["projectile_speed"], self.tower_type, splash, slow, slow_time))

    def cast_skill(self, enemies, projectiles, effects):
        if not self.skill_ready:
            return False
        self.skill_ready = False
        self.skill_charge = 0
        self.skill_effect_timer = 0.55
        effects.append({"x": self.x, "y": self.y, "r": self.range * 1.15, "time": 0.55, "color": self.data["color"]})
        if self.tower_type == "bow":
            targets = [e for e in enemies if not e.dead and math.hypot(e.x - self.x, e.y - self.y) <= self.range * 1.25][:8]
            for t in targets:
                projectiles.append(Projectile(self.x, self.y, t, self.damage * 1.15, self.data["projectile_speed"] * 1.35, self.tower_type))
        elif self.tower_type == "cannon":
            for e in enemies:
                if not e.dead and math.hypot(e.x - self.x, e.y - self.y) <= self.range * 1.35:
                    e.take_damage(self.damage * 2.2)
        elif self.tower_type == "ice":
            for e in enemies:
                if not e.dead and math.hypot(e.x - self.x, e.y - self.y) <= self.range * 1.45:
                    e.take_damage(self.damage * 0.8)
                    e.apply_slow(0.28, 3.4)
        return True

    def draw(self, screen, selected=False, placing=False):
        if selected or placing:
            pygame.draw.circle(screen, (*self.data["color"],), (self.x, self.y), int(self.range), 1)
        rect = pygame.Rect(self.col * TILE_SIZE + 3, self.row * TILE_SIZE + 3, TILE_SIZE - 6, TILE_SIZE - 6)
        pygame.draw.rect(screen, self.data["color"], rect, border_radius=4)
        pygame.draw.rect(screen, WHITE, rect, 1, border_radius=4)
        font = pygame.font.SysFont("arial", 11, bold=True)
        text = font.render(str(self.merge_level), True, (10, 10, 10))
        screen.blit(text, (rect.x + 5, rect.y + 2))
        if self.skill_ready:
            pygame.draw.circle(screen, YELLOW, (self.x + 7, self.y - 7), 4)

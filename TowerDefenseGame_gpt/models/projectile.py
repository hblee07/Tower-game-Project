import math
import pygame
from settings import YELLOW, ORANGE, CYAN

class Projectile:
    def __init__(self, x, y, target, damage, speed, kind, splash=0, slow=1.0, slow_time=0):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.kind = kind
        self.splash = splash
        self.slow = slow
        self.slow_time = slow_time
        self.dead = False

    def update(self, dt, enemies):
        if self.target.dead or self.target.reached_end:
            self.dead = True
            return []
        tx, ty = self.target.x, self.target.y
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist < max(7, self.speed * dt):
            self.dead = True
            hit = [self.target]
            if self.splash > 0:
                hit = [e for e in enemies if not e.dead and math.hypot(e.x - tx, e.y - ty) <= self.splash]
            for e in hit:
                e.take_damage(self.damage)
                if self.slow < 1.0:
                    e.apply_slow(self.slow, self.slow_time)
            return hit
        self.x += dx / dist * self.speed * dt
        self.y += dy / dist * self.speed * dt
        return []

    def draw(self, screen):
        color = YELLOW
        radius = 4
        if self.kind == "cannon":
            color = ORANGE
            radius = 6
        elif self.kind == "ice":
            color = CYAN
            radius = 5
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)

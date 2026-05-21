import pygame
import math
from abc import ABCMeta, abstractmethod
from settings import TOWER_STATS, CELL_SIZE

# Tower 추상 클래스
class Tower(metaclass = ABCMeta):
    def __init__(self, tower_type: str, grid_pos: tuple, merge_level: int = 1):
        self.tower_type   = tower_type
        self.grid_pos     = grid_pos          # (col, row)
        self.merge_level  = merge_level       # 1 ~ 3

        stats = TOWER_STATS[tower_type]
        self.damage       = stats["damage"][merge_level - 1]
        self.attack_range = stats["attack_range"]
        self.attack_speed = stats["attack_speed"]  # 초당 공격
        self.skill_cooldown_max = stats["skill_cooldown"]

        self._attack_timer  = 0.0
        self._skill_timer   = 0.0
        self.projectiles    = []              # 이 타워가 생성한 발사체

    # ── 공통 업데이트 ─────────────────────────────────────────
    def update(self, dt: float, enemies: list) -> list:
        """매 프레임 호출. 발사체 리스트 반환."""
        self._attack_timer += dt
        if self._skill_timer < self.skill_cooldown_max:
            self._skill_timer += dt

        new_projectiles = []
        if self._attack_timer >= 1.0 / self.attack_speed:
            self._attack_timer = 0.0
            target = self._find_target(enemies)
            if target:
                new_projectiles = self._fire(target)

        return new_projectiles

    def _find_target(self, enemies: list):
        """공격 범위 내 가장 앞선 적 반환."""
        in_range = [e for e in enemies if self._distance_to(e) <= self.attack_range * CELL_SIZE]
        return max(in_range, key=lambda e: e.path_progress, default=None)

    def _distance_to(self, enemy) -> float:
        px = self.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
        py = self.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        return math.hypot(enemy.pixel_pos[0] - px, enemy.pixel_pos[1] - py)

    @abstractmethod
    def _fire(self, target) -> list:
        """발사체 생성 로직. 서브클래스에서 구현."""

    @abstractmethod
    def use_skill(self, enemies: list, grid) -> None:
        """스킬 발동. 서브클래스에서 구현."""

    def skill_ready(self) -> bool:
        return self._skill_timer >= self.skill_cooldown_max

    def skill_cooldown_ratio(self) -> float:
        """HUD 쿨타임 바용 0.0 ~ 1.0."""
        if self.skill_cooldown_max == 0:
            return 1.0
        return min(self._skill_timer / self.skill_cooldown_max, 1.0)

    def _apply_upgrade(self) -> None:
        """업그레이드 스탯 반영. 기본: 데미지 20%, 범위 10% 증가."""
        self.damage = int(self.damage * 1.2)
        self.attack_range = self.attack_range * 1.1

    def sell(self, economy) -> None:
        from settings import TOWER_STATS
        base_cost = TOWER_STATS[self.tower_type]["cost"][self.merge_level - 1]
        ratio     = TOWER_STATS[self.tower_type]["sell_ratio"]
        economy.earn(int(base_cost * ratio))

    # ── 렌더링 ────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        px = self.grid_pos[0] * CELL_SIZE
        py = self.grid_pos[1] * CELL_SIZE
        self._draw_body(surface, px, py)
        self._draw_merge_badge(surface, px, py)

    def _draw_body(self, surface, px, py) -> None:
        """서브클래스에서 오버라이드 가능."""
        pygame.draw.rect(surface, (80, 80, 200), (px+2, py+2, CELL_SIZE-4, CELL_SIZE-4))

    def _draw_merge_badge(self, surface, px, py) -> None:
        font = pygame.font.SysFont(None, 14)
        surf = font.render(str(self.merge_level), True, (255, 255, 255))
        surface.blit(surf, (px + CELL_SIZE - 10, py + 2))

    def draw_range(self, surface: pygame.Surface) -> None:
        """타워 선택 시 공격 범위 원 표시."""
        cx = self.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
        cy = self.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        r  = int(self.attack_range * CELL_SIZE)
        s  = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 40), (r, r), r)
        pygame.draw.circle(s, (255, 255, 255, 120), (r, r), r, 1)
        surface.blit(s, (cx - r, cy - r))

    def to_dict(self) -> dict:
        """세이브용 직렬화."""
        return {
            "type": self.tower_type,
            "grid_pos": self.grid_pos,
            "merge_level": self.merge_level,
            "upgrade_level": self.upgrade_level,
        }

    @staticmethod
    def from_dict(data: dict) -> "Tower":
        """세이브 로드용 역직렬화."""
        cls_map = {
            "bomb": BombTower, "lightning": LightningTower,
            "thorn": ThornTower, "random": RandomTower,
        }
        t = cls_map[data["type"]](data["grid_pos"], data["merge_level"])
        t.upgrade_level = data["upgrade_level"]
        return t


# ── 서브클래스 ────────────────────────────────────────────────
class BombTower(Tower):
    def __init__(self, grid_pos, merge_level=1):
        super().__init__("bomb", grid_pos, merge_level)
        self.bomb_radius = 1.5 * CELL_SIZE   # 폭발 반경 (픽셀)

    def _fire(self, target) -> list:
        from models.projectile import BombProjectile
        return [BombProjectile(self.grid_pos, target, self.damage, self.bomb_radius)]

    def use_skill(self, enemies: list, grid) -> None:
        """초거대 폭탄: 이동 경로 위 랜덤 위치에 대폭발."""
        if not self.skill_ready() or not grid.path:
            return
        import random
        from models.effect import ExplosionEffect
        pos = random.choice(grid.path)
        radius = self.bomb_radius * 3
        for e in enemies:
            if math.hypot(e.pixel_pos[0] - pos[0]*CELL_SIZE,
                          e.pixel_pos[1] - pos[1]*CELL_SIZE) <= radius:
                e.take_damage(self.damage * 4)
        grid.effect_manager.spawn(ExplosionEffect(pos, radius))
        self._skill_timer = 0.0


class LightningTower(Tower):
    def __init__(self, grid_pos, merge_level=1):
        super().__init__("lightning", grid_pos, merge_level)
        from settings import TOWER_STATS
        self.chain_count = TOWER_STATS["lightning"]["chain_count"][merge_level - 1]
        self.stun_duration = 0.5

    def _fire(self, target) -> list:
        from models.projectile import LightningProjectile
        return [LightningProjectile(self.grid_pos, target, self.damage, self.chain_count)]

    def use_skill(self, enemies: list, grid) -> None:
        """범위 내 모든 적 연쇄 감전."""
        if not self.skill_ready():
            return
        for e in [e for e in enemies if self._distance_to(e) <= self.attack_range * CELL_SIZE * 1.5]:
            e.take_damage(self.damage * 2)
            e.apply_stun(self.stun_duration)
        self._skill_timer = 0.0


class ThornTower(Tower):
    def __init__(self, grid_pos, merge_level=1):
        super().__init__("thorn", grid_pos, merge_level)
        from settings import TOWER_STATS
        self.slow_factor = TOWER_STATS["thorn"]["slow_factor"][merge_level - 1]
        self._affected_cells = set()   # 가시밭길 적용 격자 좌표

    def _fire(self, target) -> list:
        """ThornTower는 발사체 없음. 범위 내 셀을 가시밭길로 전환."""
        self._apply_thorn_field(target)
        return []

    def _apply_thorn_field(self, target) -> None:
        target.take_damage(self.damage)
        target.apply_slow(self.slow_factor, duration=0.5)

    def use_skill(self, enemies: list, grid) -> None:
        """범위 내 모든 픽셀 가시밭길화 (일정 시간)."""
        if not self.skill_ready():
            return
        # grid에 thorn_overlay 등록 → 적 이동 시 적용
        grid.activate_thorn_overlay(self.grid_pos, self.attack_range, duration=5.0)
        self._skill_timer = 0.0


class RandomTower(Tower):
    def __init__(self, grid_pos, merge_level=1):
        super().__init__("random", grid_pos, merge_level)
        self._burst_timer = 0.0

    def _fire(self, target) -> list:
        from models.projectile import BasicProjectile
        return [BasicProjectile(self.grid_pos, target, self.damage)]

    def use_skill(self, enemies: list, grid) -> None:
        """3초간 데미지 3배 버스트."""
        if not self.skill_ready():
            return
        self._burst_timer = 3.0
        self._skill_timer = 0.0

    def update(self, dt, enemies):
        if self._burst_timer > 0:
            self._burst_timer -= dt
        return super().update(dt, enemies)

    def transform(self, grid) -> Tower:
        """merge_level 3 시 랜덤 타워로 변신. GameScene에서 호출."""
        import random
        choices = ["bomb", "lightning", "thorn"]
        new_type = random.choice(choices)
        cls_map = {"bomb": BombTower, "lightning": LightningTower, "thorn": ThornTower}
        return cls_map[new_type](self.grid_pos, merge_level=3)

    def current_damage(self) -> int:
        """버스트 상태면 3배."""
        return self.damage * (3 if self._burst_timer > 0 else 1)
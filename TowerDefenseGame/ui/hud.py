import pygame
from settings import MAP_SIZE, PANEL_WIDTH, SCREEN_WIDTH, SCREEN_HEIGHT, PANEL, WHITE, YELLOW, RED, GREEN, TOWER_DATA, MAX_MERGE_LEVEL, MAX_UPGRADE_LEVEL

class Button:
    def __init__(self, rect, label, action, color=(75, 82, 105)):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action
        self.color = color

    def draw(self, screen, font, selected=False):
        c = (110, 125, 165) if selected else self.color
        pygame.draw.rect(screen, c, self.rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, self.rect, 1, border_radius=6)
        text = font.render(self.label, True, WHITE)
        screen.blit(text, text.get_rect(center=self.rect.center))

    def contains(self, pos):
        return self.rect.collidepoint(pos)

class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("malgungothic", 17)
        self.small = pygame.font.SysFont("malgungothic", 14)
        self.big = pygame.font.SysFont("malgungothic", 22, bold=True)
        self.buttons = []
        x = MAP_SIZE + 18
        y = 126
        self.buttons.append(Button((x, y, 82, 38), "Bow 90", "select_bow")); x += 92
        self.buttons.append(Button((x, y, 100, 38), "Cannon 135", "select_cannon")); x += 110
        self.buttons.append(Button((x, y, 82, 38), "Ice 115", "select_ice"))
        self.action_buttons = [
            Button((MAP_SIZE+18, 438, 80, 34), "Upgrade", "upgrade", (70,100,90)),
            Button((MAP_SIZE+108, 438, 72, 34), "Skill", "skill", (90,85,130)),
            Button((MAP_SIZE+190, 438, 72, 34), "Sell", "sell", (120,75,75)),
            Button((MAP_SIZE+18, 486, 112, 34), "Start Wave", "start_wave", (95,95,65)),
            Button((MAP_SIZE+140, 486, 72, 34), "Save", "save", (70,90,120)),
            Button((MAP_SIZE+222, 486, 54, 34), "Pause", "pause", (80,80,90)),
        ]

    def draw_text(self, screen, text, x, y, font=None, color=WHITE):
        surf = (font or self.font).render(str(text), True, color)
        screen.blit(surf, (x, y))

    def draw(self, screen, game):
        pygame.draw.rect(screen, PANEL, (MAP_SIZE, 0, PANEL_WIDTH, SCREEN_HEIGHT))
        x = MAP_SIZE + 16
        self.draw_text(screen, "Tower Defense", x, 14, self.big, YELLOW)
        self.draw_text(screen, f"Stage: {game.stage_id} - {game.map.stage['name']}", x, 48)
        self.draw_text(screen, f"Gold: {game.economy.gold}", x, 72, color=YELLOW)
        hp_color = GREEN if game.economy.hp > 10 else RED
        self.draw_text(screen, f"Castle HP: {game.economy.hp}", x+120, 72, color=hp_color)
        self.draw_text(screen, f"Wave: {game.wave.current_wave_number()} / {game.wave.total_waves}", x, 96)

        self.draw_text(screen, "Build", x, 108, self.small, WHITE)
        for b in self.buttons:
            selected = game.selected_build and b.action.endswith(game.selected_build)
            b.draw(screen, self.small, selected)

        self.draw_text(screen, "Rules", x, 182, self.big, WHITE)
        rules = [
            "Click: select/build tower",
            "Same type+same merge Lv+in range = Merge",
            f"Max merge Lv {MAX_MERGE_LEVEL}, upgrade Lv {MAX_UPGRADE_LEVEL}",
            "Space: start wave | P: pause | S: save",
            "ESC: cancel / safe state",
        ]
        for i, t in enumerate(rules):
            self.draw_text(screen, t, x, 214+i*20, self.small, (215,215,220))

        self.draw_text(screen, "Selected Tower", x, 334, self.big, WHITE)
        if game.selected_tower:
            t = game.selected_tower
            self.draw_text(screen, f"{TOWER_DATA[t.tower_type]['name']}  Merge Lv.{t.merge_level}  Up Lv.{t.upgrade_level}", x, 365, self.small)
            self.draw_text(screen, f"Damage {int(t.damage)} | Range {int(t.range)} | CD {t.cooldown:.2f}s", x, 386, self.small)
            cost = t.upgrade_cost()
            self.draw_text(screen, f"Upgrade cost: {cost if cost else 'MAX'}", x, 407, self.small, YELLOW)
            self.draw_text(screen, f"Skill: {TOWER_DATA[t.tower_type]['skill_name']} {int(t.skill_charge)}%", x, 426, self.small, GREEN if t.skill_ready else WHITE)
        else:
            self.draw_text(screen, "None", x, 365, self.small)

        for b in self.action_buttons:
            b.draw(screen, self.small)

        if game.message:
            self.draw_text(screen, game.message, x, 548, self.small, RED if game.message_bad else GREEN)

    def handle_click(self, pos):
        for b in self.buttons + self.action_buttons:
            if b.contains(pos):
                return b.action
        return None

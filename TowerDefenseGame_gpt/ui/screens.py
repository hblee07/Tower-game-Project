import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, PANEL, DARK, GREEN, RED

class Screens:
    def __init__(self):
        self.title = pygame.font.SysFont("malgungothic", 42, bold=True)
        self.big = pygame.font.SysFont("malgungothic", 28, bold=True)
        self.font = pygame.font.SysFont("malgungothic", 20)
        self.small = pygame.font.SysFont("malgungothic", 16)

    def center_text(self, screen, text, y, font=None, color=WHITE):
        surf = (font or self.font).render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH//2, y)))

    def button(self, screen, rect, text):
        r = pygame.Rect(rect)
        pygame.draw.rect(screen, PANEL, r, border_radius=10)
        pygame.draw.rect(screen, WHITE, r, 2, border_radius=10)
        surf = self.font.render(text, True, WHITE)
        screen.blit(surf, surf.get_rect(center=r.center))
        return r

    def draw_title(self, screen, has_save):
        screen.fill(DARK)
        self.center_text(screen, "PYTHON TOWER DEFENSE", 96, self.title, YELLOW)
        self.center_text(screen, "Click a stage, build towers, clear 5 waves.", 145, self.font)
        buttons = {
            "stage1": self.button(screen, (SCREEN_WIDTH//2-180, 205, 160, 52), "Stage 1"),
            "stage2": self.button(screen, (SCREEN_WIDTH//2+20, 205, 160, 52), "Stage 2"),
            "continue": self.button(screen, (SCREEN_WIDTH//2-180, 280, 360, 52), "Continue" if has_save else "Continue (no save)"),
            "ranking": self.button(screen, (SCREEN_WIDTH//2-180, 355, 360, 52), "Ranking"),
            "quit": self.button(screen, (SCREEN_WIDTH//2-180, 430, 360, 52), "Quit"),
        }
        self.center_text(screen, "Controls: mouse, Space, P, S, ESC", 530, self.small, (210,210,220))
        return buttons

    def draw_end(self, screen, won, score, name):
        screen.fill(DARK)
        self.center_text(screen, "VICTORY" if won else "DEFEAT", 120, self.title, GREEN if won else RED)
        self.center_text(screen, f"Score: {score}", 185, self.big, YELLOW)
        self.center_text(screen, "Type your name and press Enter", 245, self.font)
        self.center_text(screen, name + "_", 290, self.big, WHITE)
        self.center_text(screen, "ESC: title without saving ranking", 370, self.small, (220,220,220))

    def draw_ranking(self, screen, rankings):
        screen.fill(DARK)
        self.center_text(screen, "TOP 20 RANKING", 58, self.title, YELLOW)
        y = 110
        if not rankings:
            self.center_text(screen, "No records yet", 180, self.font)
        for i, row in enumerate(rankings[:20], 1):
            text = f"{i:02d}. {row['name']:<12}  Score {row['score']:>5}  Stage {row['stage']}  Wave {row['wave']}"
            self.center_text(screen, text, y, self.small, WHITE)
            y += 23
        self.center_text(screen, "ESC or click: back to title", 560, self.small, (220,220,220))

    def draw_pause(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,145))
        screen.blit(overlay, (0,0))
        self.center_text(screen, "PAUSED", SCREEN_HEIGHT//2-30, self.title, YELLOW)
        self.center_text(screen, "Press P to resume", SCREEN_HEIGHT//2+20, self.font, WHITE)

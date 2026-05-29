import pygame
from settings import BOARD_W, SCREEN_W, SCREEN_H, TOWER_STATS, COLOR_TEXT, MAX_UPGRADE_LEVEL, MAX_MERGE_LEVEL
class HUDButton:
    def __init__(self, rect, label, action, color=(70, 82, 96)):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action
        self.color = color



    def draw(self, surf, font, enabled=True, selected=False):
        if selected:
            bg_color = (110, 125, 165)
        elif not enabled:
            bg_color = (45, 48, 55)
        else:
            bg_color = self.color
        pygame.draw.rect(surf, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surf, (170, 180, 190), self.rect, 1, border_radius=5)
        text_color = COLOR_TEXT if enabled else (130, 130, 130)
        img = font.render(self.label, True, text_color)
        surf.blit(img, img.get_rect(center=self.rect.center))
    def contains(self, pos):
        return self.rect.collidepoint(pos)
class HUD:
    def __init__(self):
        # 폰트 크기를 조금 더 컴팩트하게 다듬어 가독성과 공간을 모두 잡습니다.
        self.font = pygame.font.SysFont(None, 19)      
        self.small = pygame.font.SysFont(None, 15)    
        self.big = pygame.font.SysFont(None, 21, bold=True)
        self.invalid_timer = 0
        self.message = ''
        self.build_buttons = []
        self.action_buttons = {}

        bx = BOARD_W + 50

        by = 80

        for t in ['bomb', 'lightning', 'thorn', 'random']:

            st = TOWER_STATS[t]

            self.build_buttons.append(HUDButton((bx, by, 200, 28), f"{st['name']} {st['cost'][0]}G", f"build_{t}"))

            by += 32



        # 2. 기능성 액션 버튼 고정 배치 (절대 겹치지 않는 황금 Y 좌표 할당)

        # 스킬/업그레이드는 y=380, 판매는 y=412로 고정하여 스킬바(y=348)와 완벽히 분리됩니다.

        self.action_buttons['skill'] = HUDButton((BOARD_W + 50, 380, 92, 28), "Skill", "skill", (90, 85, 130))

        self.action_buttons['upgrade'] = HUDButton((BOARD_W + 158, 380, 92, 28), "Upgrade", "upgrade", (70, 100, 90))

        self.action_buttons['sell'] = HUDButton((BOARD_W + 50, 412, 200, 28), "Sell", "sell", (120, 75, 75))

       

        # 시스템 제어 버튼 고정 (알림창 바로 위 안착)

        self.action_buttons['save'] = HUDButton((BOARD_W + 50, 444, 200, 28), "Save", "save", (70, 90, 120))

        self.action_buttons['title'] = HUDButton((BOARD_W + 50, 476, 200, 28), "Title", "title", (80, 80, 90))



    def update(self, dt):

        if hasattr(self, 'invalid_timer'):

            self.invalid_timer = max(0, self.invalid_timer - dt)



    def flash_invalid(self, msg='Invalid action'):

        self.invalid_timer = 1.2

        self.message = msg



    def draw_text(self, surf, text, x, y, font=None, color=COLOR_TEXT):

        img = (font or self.font).render(str(text), True, color)

        surf.blit(img, (x, y))



    def draw(self, surface, game):

        # 배경 패널 그리기

        panel = pygame.Rect(BOARD_W, 0, SCREEN_W - BOARD_W, SCREEN_H)

        pygame.draw.rect(surface, (28, 31, 40), panel)

       

        x = BOARD_W + 50

       

        # 상단 기본 정보 출력

        self.draw_text(surface, f"Gold: {game.economy.gold}", x, 12, color=(255, 235, 130))
        
        # =================🔥 [Castle HP 및 HP Bar 출력] =================
        hp_x = x + 105
        hp_y = 12
        self.draw_text(surface, f"Castle HP: {game.castle_hp.hp}", hp_x, hp_y)
        
        # HP Bar 위치 및 크기 설정 (숫자 텍스트 바로 아래 배치)
        hp_bar_x = hp_x
        hp_bar_y = hp_y + 16
        hp_bar_w = 95
        hp_bar_h = 8
        
        # HP 비율 계산 (예시로 최대 체력을 10으로 가정, game.castle_hp.max_hp 가 있다면 교체 가능)
        max_hp = getattr(game.castle_hp, 'max_hp', 10) 
        hp_ratio = min(1.0, max(0.0, game.castle_hp.hp / max_hp))
        current_hp_bar_w = int(hp_bar_w * hp_ratio)
        
        # 비율에 따른 4단계 색상 구분 (스킬 게이지와 유사한 규칙)
        if hp_ratio >= 0.9:       # 90% 이상: 안전/풀피 (파랑 계열)
            hp_bar_color = (45, 140, 215)
        elif hp_ratio >= 0.5:     # 50% 이상: 양호 (초록 계열)
            hp_bar_color = (70, 210, 120)
        elif hp_ratio >= 0.25:    # 25% 이상: 경고 (노랑 계열)
            hp_bar_color = (245, 200, 65)
        else:                     # 25% 미만: 위기 (빨강 계열)
            hp_bar_color = (235, 75, 75)
            
        # HP Bar 그리기 (배경 -> 잔량 -> 테두리)
        pygame.draw.rect(surface, (40, 45, 55), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=2)
        if current_hp_bar_w > 0:
            pygame.draw.rect(surface, hp_bar_color, (hp_bar_x, hp_bar_y, current_hp_bar_w, hp_bar_h), border_radius=2)
        pygame.draw.rect(surface, (80, 85, 95), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), 1, border_radius=2)
        # ===============================================================

        # Wave 및 Stage 출력 (HP Bar 영역 침범 방지를 위해 y축을 +2씩 아래로 미세 조정)
        self.draw_text(surface, f"Wave: {game.wave_manager.current_wave}/5", x, 36)
        self.draw_text(surface, f"Stage: {game.stage_id}", x + 105, 36)
        
        # 빌드 섹션 타이틀 및 버튼들

        self.draw_text(surface, "Towers (Build)", x, 58, self.big, (255, 235, 130))

        for b in self.build_buttons:

            tower_type = b.action.replace("build_", "")

            cost = TOWER_STATS[tower_type]['cost'][0]

            can_afford = game.economy.can_afford(cost)

           

            is_selected = hasattr(game, 'selected_build') and game.selected_build == tower_type

            b.draw(surface, self.small, enabled=can_afford, selected=is_selected)



        # 💡 조작 가이드 안내 (머지 정보 통합 및 고정 위치 정리)

        self.draw_text(surface, "L-Click: place/select | ESC: cancel", x, 216, self.small, (170, 170, 170))

        self.draw_text(surface, "P: pause | M: merge (same type & Lv)", x, 232, self.small, (170, 170, 170))

       

        # 선택된 타워 상세 정보 섹션

        self.draw_text(surface, "Selected Tower", x, 260, self.big, (255, 235, 130))

        t = game.selected_tower

       

        if t:

            # 타워 정보 출력

            self.draw_text(surface, f"{TOWER_STATS[t.tower_type]['name']} Lv.{t.merge_level} (+{t.upgrade_level})", x, 284, self.font)

            self.draw_text(surface, f"Dmg: {int(t.damage)} | Range: {t.attack_range:.1f}", x, 304, self.small, (200, 200, 210))

           

            cost = t.upgrade_cost()

            cost_text = f"Upgrade cost: {cost}G" if t.upgrade_level < MAX_UPGRADE_LEVEL else "Upgrade cost: MAX"

            self.draw_text(surface, cost_text, x, 322, self.small, (255, 215, 0))

           

            # =================🔥 [스킬 게이지 바 고정 배치] =================

            # 버튼 영역(y=380)에 절대 침범하지 않도록 y=348 선으로 확정 배치합니다.

            skill_y = 348

            self.draw_text(surface, "Skill:", x, skill_y, self.small, (190, 190, 190))

           

            bar_x = x + 38

            bar_y = skill_y + 2

            bar_w = 115

            bar_h = 11  # 높이를 1px 줄여 더욱 정교하게 가둡니다.

           

            ratio = min(1.0, max(0.0, t.skill_cooldown_ratio()))

            current_bar_w = int(bar_w * ratio)

           

            if t.skill_ready():

                fill_color = (45, 140, 215)

                text_color = (100, 200, 255)

            elif ratio >= 0.7:

                fill_color = (70, 210, 120)

                text_color = (140, 255, 180)

            elif ratio >= 0.2:

                fill_color = (245, 200, 65)

                text_color = (255, 235, 140)

            else:

                fill_color = (235, 75, 75)

                text_color = (255, 140, 140)

           

            pygame.draw.rect(surface, (40, 45, 55), (bar_x, bar_y, bar_w, bar_h), border_radius=3)

            if current_bar_w > 0:

                pygame.draw.rect(surface, fill_color, (bar_x, bar_y, current_bar_w, bar_h), border_radius=3)

            pygame.draw.rect(surface, (80, 85, 95), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

           

            percentage_str = f"{int(ratio * 100)}%"

            self.draw_text(surface, percentage_str, bar_x + bar_w + 8, skill_y - 1, self.small, color=text_color)

           

            # 상호작용 버튼 그리기 (활성화 상태)

            self.action_buttons['skill'].draw(surface, self.small, enabled=t.skill_ready())

            self.action_buttons['upgrade'].draw(surface, self.small, enabled=(t.upgrade_level < MAX_UPGRADE_LEVEL and game.economy.can_afford(cost)))

            self.action_buttons['sell'].draw(surface, self.small, enabled=True)

        else:

            # 선택된 타워가 없을 때도 고정된 자리에 비활성화 상태로 버튼 유지

            self.draw_text(surface, "None", x, 284, self.small, (150, 150, 150))

           

            self.action_buttons['skill'].draw(surface, self.small, enabled=False)

            self.action_buttons['upgrade'].draw(surface, self.small, enabled=False)

            self.action_buttons['sell'].draw(surface, self.small, enabled=False)



        # 시스템 제어 버튼 그리기 (고정)

        self.action_buttons['save'].draw(surface, self.small, enabled=True)

        self.action_buttons['title'].draw(surface, self.small, enabled=True)



        # 최하단 알림 메시지창 패널 (y=552 고정)

        if self.invalid_timer > 0 and self.message:

            is_bad = getattr(game, 'message_bad', True)

            msg_color = (220, 50, 50) if is_bad else (20, 140, 60)

           

            rect_x = BOARD_W + 50

            rect_y = 516

            rect_w = 200

            rect_h = 32

           

            alert_rect = pygame.Rect(rect_x, rect_y, rect_w, rect_h)

           

            pygame.draw.rect(surface, (255, 255, 255), alert_rect, border_radius=4)

            pygame.draw.rect(surface, (200, 200, 200), alert_rect, 1, border_radius=4)

           

            img = self.small.render(str(self.message), True, msg_color)

            text_rect = img.get_rect(center=alert_rect.center)

            surface.blit(img, text_rect)



    def handle_click(self, pos):

        for b in self.build_buttons:

            if b.contains(pos):

                return b.action

       

        for b in self.action_buttons.values():

            if b.contains(pos):

                return b.action

               

        return None
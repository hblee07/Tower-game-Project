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
        self.font = pygame.font.SysFont(None, 20)      # 22 -> 20 약간 축소
        self.small = pygame.font.SysFont(None, 16)     # 18 -> 16 약간 축소
        self.big = pygame.font.SysFont(None, 22, bold=True) # 24 -> 22 약간 축소
        
        self.invalid_timer = 0
        self.message = ''
        
        self.build_buttons = []
        self.action_buttons = {}
        
        # 1. 타워 빌드 버튼 배치 (높이 36 -> 28로 축소, 간격 42 -> 32로 압축)
        bx = BOARD_W + 50
        by = 80
        for t in ['bomb', 'lightning', 'thorn', 'random']:
            st = TOWER_STATS[t]
            self.build_buttons.append(HUDButton((bx, by, 200, 28), f"{st['name']} {st['cost'][0]}G", f"build_{t}"))
            by += 32

        # 2. 기능성 액션 버튼 배치 (높이 34 -> 28로 축소, y축 위치 위로 바짝 당김)
        #HUDButton(( x 좌표,  y 좌표,  가로 너비,  세로 높이 ))
        self.action_buttons['skill'] = HUDButton((BOARD_W + 50, 410, 92, 28), "Skill", "skill", (90, 85, 130))
        self.action_buttons['upgrade'] = HUDButton((BOARD_W + 158, 410, 92, 28), "Upgrade", "upgrade", (70, 100, 90)) # 126 -> 158 수정
        self.action_buttons['sell'] = HUDButton((BOARD_W + 50, 444, 200, 28), "Sell", "sell", (120, 75, 75))
        self.action_buttons['save'] = HUDButton((BOARD_W + 50, 478, 200, 28), "Save", "save", (70, 90, 120))
        self.action_buttons['title'] = HUDButton((BOARD_W + 50, 512, 200, 28), "Title", "title", (80, 80, 90))
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
        
        # 상단 기본 정보 출력 (y축 마진 미세 조정)
        self.draw_text(surface, f"Gold: {game.economy.gold}", x, 12, color=(255, 235, 130))
        
        hp_color = (100, 230, 100) if game.castle_hp.hp > 5 else (255, 90, 90)
        self.draw_text(surface, f"Castle HP: {game.castle_hp.hp}", x + 105, 12, color=hp_color)
        self.draw_text(surface, f"Wave: {game.wave_manager.current_wave}/5", x, 34)
        self.draw_text(surface, f"Stage: {game.stage_id}", x + 105, 34)
        
        # 빌드 섹션 타이틀 및 버튼들
        self.draw_text(surface, "Towers (Build)", x, 58, self.big, (255, 235, 130))
        for b in self.build_buttons:
            tower_type = b.action.replace("build_", "")
            cost = TOWER_STATS[tower_type]['cost'][0]
            can_afford = game.economy.can_afford(cost)
            
            is_selected = hasattr(game, 'selected_build') and game.selected_build == tower_type
            b.draw(surface, self.small, enabled=can_afford, selected=is_selected)

        # 규칙 및 조작법 안내 텍스트 (위치 당김)
        self.draw_text(surface, "Left: place/select, M: merge, U: upgrade", x, 220, self.small, (190, 190, 190))
        self.draw_text(surface, "P: pause | ESC: cancel", x, 236, self.small, (190, 190, 190))
        
        # 선택된 타워 상세 정보 섹션 (위치 당김)
        self.draw_text(surface, "Selected Tower", x, 264, self.big, (255, 235, 130))
        t = game.selected_tower
        
        if t:
            self.draw_text(surface, f"{TOWER_STATS[t.tower_type]['name']} Lv.{t.merge_level} (+{t.upgrade_level})", x, 288, self.font)
            self.draw_text(surface, f"Dmg: {int(t.damage)} | Range: {t.attack_range:.1f}", x, 310, self.small, (200, 200, 210))
            
            cost = t.upgrade_cost()
            cost_text = f"Upgrade cost: {cost}G" if t.upgrade_level < MAX_UPGRADE_LEVEL else "Upgrade cost: MAX"
            self.draw_text(surface, cost_text, x, 328, self.small, (255, 215, 0))
            
            # =================🔥 [스킬 게이지 바 + % 디자인 추가] =================
            self.draw_text(surface, "Skill:", x, 398, self.small, (190, 190, 190))
            
            # 게이지 바 레이아웃 설정
            bar_x = x + 38          # 스킬 텍스트 오른쪽에 배치
            bar_y = 398 + 2         # 텍스트와 세로 중앙 맞춤 정렬
            bar_w = 115             # 게이지 바 전체 너비
            bar_h = 12              # 게이지 바 높이
            
            # 게이지 비율 계산 (0.0 ~ 1.0 제한)
            ratio = min(1.0, max(0.0, t.skill_cooldown_ratio()))
            current_bar_w = int(bar_w * ratio)
            
            # 상태에 따른 색상 정의
            if t.skill_ready():
                fill_color = (45, 140, 215)     # 1. 스킬 준비 완료 (Ready) : 파란색
                text_color = (100, 200, 255)
            elif ratio >= 0.7:
                fill_color = (70, 210, 120)     # 2. 70% 이상 : 초록색
                text_color = (140, 255, 180)
            elif ratio >= 0.2:
                fill_color = (245, 200, 65)     # 3. 20% 이상 : 노란색
                text_color = (255, 235, 140)
            else:
                fill_color = (235, 75, 75)      # 4. 20% 미만 : 빨간색
                text_color = (255, 140, 140)
            
            # 1. 게이지 바 어두운 배경 그리기
            pygame.draw.rect(surface, (40, 45, 55), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
            
            # 2. 실제로 게이지가 차오른 만큼 안쪽 바 그리기 (비율이 0보다 클 때만)
            if current_bar_w > 0:
                pygame.draw.rect(surface, fill_color, (bar_x, bar_y, current_bar_w, bar_h), border_radius=3)
            
            # 3. 깔끔함을 더해줄 슬림한 외각 테두리 선
            pygame.draw.rect(surface, (80, 85, 95), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
            
            # 4. 바 오른쪽에 100% 텍스트 표기
            percentage_str = f"{int(ratio * 100)}%"
            self.draw_text(surface, percentage_str, bar_x + bar_w + 8, 398, self.small, color=text_color)
            # ===================================================================
            
            self.draw_text(surface, f"Merge: same type & level in range + 'M'", x, 414, self.small, (160, 160, 160))

            self.action_buttons['skill'].draw(surface, self.small, enabled=t.skill_ready())
            self.action_buttons['upgrade'].draw(surface, self.small, enabled=(t.upgrade_level < MAX_UPGRADE_LEVEL and game.economy.can_afford(cost)))
            self.action_buttons['sell'].draw(surface, self.small, enabled=True)
        else:
            self.draw_text(surface, "None", x, 288, self.small, (150, 150, 150))
            self.action_buttons['skill'].draw(surface, self.small, enabled=False)
            self.action_buttons['upgrade'].draw(surface, self.small, enabled=False)
            self.action_buttons['sell'].draw(surface, self.small, enabled=False)

        # 제어 버튼 그리기
        self.action_buttons['save'].draw(surface, self.small, enabled=True)
        self.action_buttons['title'].draw(surface, self.small, enabled=True)

        # 💡 [공간 확보 완료] 타이트해진 UI 덕분에 600 해상도 안에서도 y=560 위치에 알림창이 완벽하게 들어옵니다!
        # 💡 [변경] 알림 타이머가 작동 중일 때 메시지 뒤에 흰색 네모 패널을 먼저 그려줍니다.
        if self.invalid_timer > 0 and self.message:
            is_bad = getattr(game, 'message_bad', True)
            msg_color = (220, 50, 50) if is_bad else (20, 140, 60) # 텍스트 색상을 흰색 배경에 잘 보이게 조금 더 진하게 조정
            
            # 1. 흰색 네모 패널 크기 및 위치 설정
            # 버튼들과 가로 정렬을 맞추기 위해 x=BOARD_W+50, 너비=200으로 설정합니다.
            rect_x = BOARD_W + 50
            rect_y = 552
            rect_w = 200
            rect_h = 32
            
            alert_rect = pygame.Rect(rect_x, rect_y, rect_w, rect_h)
            
            # 2. 배경 사각형 그리기 (RGB 255,255,255 = 완전히 깨끗한 흰색)
            # border_radius=4를 주어 모서리를 살짝 부드럽게 만듭니다.
            pygame.draw.rect(surface, (255, 255, 255), alert_rect, border_radius=4)
            
            # 3. (선택) 테두리 선 그리기 - 살짝 회색빛 도는 테두리를 주어 고급스럽게 처리
            pygame.draw.rect(surface, (200, 200, 200), alert_rect, 1, border_radius=4)
            
            # 4. 글씨 그리기 (말풍선 네모의 정가운데에 오도록 계산)
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
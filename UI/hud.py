import pygame
from settings import BOARD_W, SCREEN_W, SCREEN_H, TOWER_STATS, COLOR_TEXT, MAX_UPGRADE_LEVEL, MAX_MERGE_LEVEL

class HUDButton:
    def __init__(self, rect, label, action, color=(70, 82, 96)):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action  # 'build_bomb', 'upgrade', 'start_wave' 등
        self.color = color

    def draw(self, surf, font, enabled=True, selected=False):
        # 선택되었을 때는 밝은 청회색, 비활성화는 어두운 색, 기본은 설정된 색
        if selected:
            bg_color = (110, 125, 165)
        elif not enabled:
            bg_color = (45, 48, 55)
        else:
            bg_color = self.color

        pygame.draw.rect(surf, bg_color, self.rect, border_radius=6)
        pygame.draw.rect(surf, (170, 180, 190), self.rect, 1, border_radius=6)
        
        text_color = COLOR_TEXT if enabled else (130, 130, 130)
        img = font.render(self.label, True, text_color)
        surf.blit(img, img.get_rect(center=self.rect.center))

    def contains(self, pos):
        return self.rect.collidepoint(pos)


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 22)
        self.small = pygame.font.SysFont(None, 18)
        self.big = pygame.font.SysFont(None, 24, bold=True)
        
        self.invalid_timer = 0
        self.message = ''
        
        self.build_buttons = []
        self.action_buttons = {}
        
        # 1. 타워 빌드 버튼 배치
        bx = BOARD_W + 18
        by = 92
        for t in ['bomb', 'lightning', 'thorn', 'random']:
            st = TOWER_STATS[t]
            self.build_buttons.append(HUDButton((bx, by, 200, 36), f"{st['name']} {st['cost'][0]}G", f"build_{t}"))
            by += 42

        # 2. 기능성 액션 버튼 배치
        self.action_buttons['skill'] = HUDButton((BOARD_W + 18, 438, 92, 34), "Skill", "skill", (90, 85, 130))
        self.action_buttons['upgrade'] = HUDButton((BOARD_W + 126, 438, 92, 34), "Upgrade", "upgrade", (70, 100, 90))
        self.action_buttons['sell'] = HUDButton((BOARD_W + 18, 480, 200, 34), "Sell", "sell", (120, 75, 75))
        
        # ⚠️ 'start_wave' 버튼을 삭제하고, Save와 Title 버튼 위치를 위로 정렬했습니다.
        self.action_buttons['save'] = HUDButton((BOARD_W + 18, 524, 92, 34), "Save", "save", (70, 90, 120))
        self.action_buttons['title'] = HUDButton((BOARD_W + 126, 524, 92, 34), "Title", "title", (80, 80, 90))
    def update(self, dt):
        if hasattr(self, 'invalid_timer'):
            self.invalid_timer = max(0, self.invalid_timer - dt)

    def flash_invalid(self, msg='Invalid action'):
        self.invalid_timer = 1.2
        self.message = msg
        # 1. 타워 빌드 버튼 배치 (가로 배치 스타일로 최적화)
        bx = BOARD_W + 18
        by = 92
        for t in ['bomb', 'lightning', 'thorn', 'random']:
            st = TOWER_STATS[t]
            # 버튼에 이름과 가격을 동적으로 바인딩하기 위해 action에 타워 type을 기록
            self.build_buttons.append(HUDButton((bx, by, 200, 36), f"{st['name']} {st['cost'][0]}G", f"build_{t}"))
            by += 42

        # 2. 기능성 액션 버튼 배치
        # 플레이어가 마우스로도 웨이브 시작, 일시정지를 누를 수 있도록 추가
        self.action_buttons['skill'] = HUDButton((BOARD_W + 18, 438, 92, 34), "Skill", "skill", (90, 85, 130))
        self.action_buttons['upgrade'] = HUDButton((BOARD_W + 126, 438, 92, 34), "Upgrade", "upgrade", (70, 100, 90))
        self.action_buttons['sell'] = HUDButton((BOARD_W + 18, 480, 200, 34), "Sell", "sell", (120, 75, 75))
        
        self.action_buttons['start_wave'] = HUDButton((BOARD_W + 18, 524, 92, 34), "Start", "start_wave", (95, 95, 65))
        self.action_buttons['save'] = HUDButton((BOARD_W + 126, 524, 92, 34), "Save", "save", (70, 90, 120))
        self.action_buttons['title'] = HUDButton((BOARD_W + 18, 566, 200, 34), "Title", "title", (80, 80, 90))

    def draw_text(self, surf, text, x, y, font=None, color=COLOR_TEXT):
        img = (font or self.font).render(str(text), True, color)
        surf.blit(img, (x, y))

    def draw(self, surface, game):
        # 배경 패널 그리기
        panel = pygame.Rect(BOARD_W, 0, SCREEN_W - BOARD_W, SCREEN_H)
        pygame.draw.rect(surface, (28, 31, 40), panel)
        
        x = BOARD_W + 18
        
        # 상단 기본 정보 출력
        self.draw_text(surface, f"Gold: {game.economy.gold}", x, 14, color=(255, 235, 130))
        
        hp_color = (100, 230, 100) if game.castle_hp.hp > 5 else (255, 90, 90)
        self.draw_text(surface, f"Castle HP: {game.castle_hp.hp}", x + 110, 14, color=hp_color)
        self.draw_text(surface, f"Wave: {game.wave_manager.current_wave}/5", x, 38)
        self.draw_text(surface, f"Stage: {game.stage_id}", x + 110, 38)
        
        # 빌드 섹션 타이틀 및 버튼들
        self.draw_text(surface, "Towers (Build)", x, 68, self.big, (255, 235, 130))
        for b in self.build_buttons:
            tower_type = b.action.replace("build_", "")
            cost = TOWER_STATS[tower_type]['cost'][0]
            can_afford = game.economy.can_afford(cost)
            
            # [좋은 기능 1] 현재 유저가 빌드하려고 선택한 타워라면 하이라이트(selected=True)
            is_selected = hasattr(game, 'selected_build') and game.selected_build == tower_type
            b.draw(surface, self.small, enabled=can_afford, selected=is_selected)

        # 규칙 및 조작법 안내 텍스트
        self.draw_text(surface, "Left: place/select, M: merge, U: upgrade", x, 266, self.small, (190, 190, 190))
        self.draw_text(surface, "Space: start wave | P: pause | ESC: cancel", x, 284, self.small, (190, 190, 190))
        
        # 선택된 타워 상세 정보 섹션
        self.draw_text(surface, "Selected Tower", x, 312, self.big, (255, 235, 130))
        t = game.selected_tower
        
        if t:
            # 타워 정보 표시
            self.draw_text(surface, f"{TOWER_STATS[t.tower_type]['name']} Lv.{t.merge_level} (+{t.upgrade_level})", x, 338, self.font)
            self.draw_text(surface, f"Dmg: {int(t.damage)} | Range: {t.attack_range:.1f}", x, 360, self.small, (200, 200, 210))
            
            # [좋은 기능 4] 만렙 업그레이드 예외 처리 문자열화
            cost = t.upgrade_cost()
            cost_text = f"Upgrade cost: {cost}G" if t.upgrade_level < MAX_UPGRADE_LEVEL else "Upgrade cost: MAX"
            self.draw_text(surface, cost_text, x, 378, self.small, (255, 215, 0))
            
            self.draw_text(surface, f"Skill: {int(t.skill_cooldown_ratio()*100)}%", x, 396, self.small, (100, 230, 100) if t.skill_ready() else COLOR_TEXT)
            self.draw_text(surface, f"Merge: same type & level in range + 'M'", x, 414, self.small, (160, 160, 160))

            # 액션 버튼 활성화 여부 판단 후 그리기
            self.action_buttons['skill'].draw(surface, self.small, enabled=t.skill_ready())
            self.action_buttons['upgrade'].draw(surface, self.small, enabled=(t.upgrade_level < MAX_UPGRADE_LEVEL and game.economy.can_afford(cost)))
            self.action_buttons['sell'].draw(surface, self.small, enabled=True)
        else:
            # [좋은 기능 4-2] 선택된 타워가 없을 때 깔끔하게 "None" 처리
            self.draw_text(surface, "None", x, 338, self.small, (150, 150, 150))
            
            # 타워가 없으므로 스킬, 강화, 판매 버튼은 비활성화 상태로 그리기
            self.action_buttons['skill'].draw(surface, self.small, enabled=False)
            self.action_buttons['upgrade'].draw(surface, self.small, enabled=False)
            self.action_buttons['sell'].draw(surface, self.small, enabled=False)

        # 시스템 제어 버튼 그리기 (웨이브 시작, 저장, 타이틀)
        # wave_active 대신 기존 코드가 사용하던 active로 변경합니다.
        self.action_buttons['save'].draw(surface, self.small, enabled=True)
        self.action_buttons['title'].draw(surface, self.small, enabled=True)

        # [좋은 기능 3] 알림 메시지 상태 세분화 (bad 면 빨강, 좋은 알림이면 초록)
        if hasattr(game, 'message') and game.message:
            is_bad = getattr(game, 'message_bad', True)  # 기본값은 True(위험) 처리
            msg_color = (255, 90, 90) if is_bad else (100, 230, 100)
            self.draw_text(surface, game.message, x, 610, self.small, color=msg_color)

    # [좋은 기능 5] 하나의 클릭 핸들러로 타워 건설 버튼과 시스템 버튼 처리를 일원화
    def handle_click(self, pos):
        # 빌드 버튼 클릭 확인
        for b in self.build_buttons:
            if b.contains(pos):
                return b.action  # 예: 'build_bomb' 반환
        
        # 일반 액션 버튼 클릭 확인
        for b in self.action_buttons.values():
            if b.contains(pos):
                return b.action  # 예: 'upgrade', 'start_wave' 반환
                
        return None
import pygame
import math
from settings import SCREEN_W, SCREEN_H, BOARD_W, CELL_SIZE, COLOR_BG, COLOR_TEXT, TOWER_STATS, MAX_UPGRADE_LEVEL, MAX_MERGE_LEVEL
from systems.map import Grid, Pathfinder, StageLoader
from systems.wave import WaveManager
from systems.economy import Economy, CastleHP, ScoreSystem
from models.effect import EffectManager
from systems.audio import AudioManager
from models.tower import BombTower, LightningTower, ThornTower, RandomTower, Tower
from UI.hud import HUD
from UI.screens import PauseOverlay

class SceneManager:
    def __init__(self, screen, save_manager): 
        self.screen=screen
        self.save_manager=save_manager
        self.scene=None
        self.audio=AudioManager()

    def replace(self, scene_name, **kwargs):
        self.scene=self._build(scene_name, **kwargs)

    def _build(self,name,**kwargs):
        if name=='title': 
            return TitleScene(self)
        if name=='game': 
            return GameScene(self, kwargs.get('stage_id',1), kwargs.get('save_data'))
        if name=='ranking': 
            return RankingScene(self)
        if name=='end': 
            return EndScene(self, kwargs.get('result','lose'), kwargs.get('score',0))
        raise ValueError(name)
    
    def handle_event(self,event):
        if self.scene: 
            self.scene.handle_event(event)

    def update(self,dt):
        if self.scene: 
            self.scene.update(dt)

    def draw(self):
        if self.scene: 
            self.scene.draw(self.screen)

class BaseScene:
    def __init__(self, manager): 
        self.manager=manager
    def handle_event(self,event): 
        pass
    def update(self,dt): 
        pass
    def draw(self,surface): 
        pass

class TitleScene(BaseScene):
    def __init__(self,manager):
        super().__init__(manager)
        self.manager.audio.play_bgm('title')
        self.font=pygame.font.SysFont(None,56)
        self.small=pygame.font.SysFont(None,28)
        cx=SCREEN_W//2
        self.buttons=[('Stage 1',pygame.Rect(cx-120,180,240,44),'stage1'),
                      ('Stage 2',pygame.Rect(cx-120,236,240,44),'stage2'),
                      ('Continue',pygame.Rect(cx-120,292,240,44),'continue'),
                      ('Ranking',pygame.Rect(cx-120,348,240,44),'ranking'),
                      ('Quit',pygame.Rect(cx-120,404,240,44),'quit')]
    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for _,rect,act in self.buttons:
                if rect.collidepoint(event.pos):
                    if act=='stage1': 
                        self.manager.replace('game',stage_id=1)
                    elif act=='stage2': 
                        self.manager.replace('game',stage_id=2)
                    elif act=='continue':
                        data=self.manager.save_manager.load()
                        if data: 
                            self.manager.replace('game',stage_id=data.get('stage_id',1),save_data=data)
                    elif act=='ranking': 
                        self.manager.replace('ranking')
                    elif act=='quit': 
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
    def draw(self,surface):
        surface.fill((20,24,34))
        title=self.font.render('Tower Defense',True,(255,235,130))
        surface.blit(title,title.get_rect(center=(SCREEN_W//2,100)))
        for text,rect,act in self.buttons:
            enabled = act!='continue' or self.manager.save_manager.has_save()
            pygame.draw.rect(surface,(70,82,96) if enabled else (45,48,55),rect,border_radius=8)
            pygame.draw.rect(surface,(185,190,200),rect,2,border_radius=8)
            img=self.small.render(text,True,COLOR_TEXT if enabled else (130,130,130))
            surface.blit(img,img.get_rect(center=rect.center))

import pygame
from settings import BOARD_W, COLOR_BG, TOWER_STATS
# 필요한 타워 클래스들이 정의되어 있다고 가정합니다.
# from towers import BombTower, LightningTower, ThornTower, RandomTower

class GameScene(BaseScene):
    def __init__(self, manager, stage_id, save_data=None):
        super().__init__(manager)
        self.manager.audio.play_bgm('game')
        self.stage_id = stage_id
        self.grid = Grid()
        self.pathfinder = Pathfinder()
        self.effect_manager = EffectManager()
        self.grid.effect_manager = self.effect_manager
        
        data = StageLoader().load(stage_id)
        self.grid.load_layout(data['layout'], data['start'], data['end'])
        self.recalc_path()
        
        self.economy = Economy()
        self.castle_hp = CastleHP()
        self.score_system = ScoreSystem()
        self.wave_manager = WaveManager(self.economy, stage_id)
        
        self.towers = []
        self.enemies = []
        self.projectiles = []
        
        self.selected_build = None  
        self.selected_tower = None
        self.merge_source = None
        self.paused = False
        
        self.message = ""
        self.message_bad = True
        
        self.hud = HUD()
        self.pause_overlay = PauseOverlay()
        
        if save_data: 
            self.restore(save_data)
            self.wave_manager.load_current_wave(self.grid.path, self.effect_manager)
        else:
            # 🔄 [자동 시작 원상 복구] 게임 시작 시 첫 웨이브를 자동으로 바로 실행합니다.
            if not self.wave_manager.all_clear and not self.wave_manager.active and not self.wave_manager.waiting_for_clear: 
                self.wave_manager.start_next_wave(self.grid.path, self.effect_manager)

    def recalc_path(self): 
        self.grid.path = self.pathfinder.find_path(self.grid)
    
    def flash_hud_msg(self, text, is_bad=True):
        """HUD에 녹색/빨간색 메시지를 보낼 수 있도록 매핑하는 헬퍼 메서드"""
        self.message = text
        self.message_bad = is_bad
        self.hud.flash_invalid(text)  # 지속시간 타이머 가동

    def handle_event(self, event):
        # 1. 키보드 단축키 처리
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.paused = not self.paused
                return
            if event.key == pygame.K_s: 
                self.save()
                return
                
            if not self.paused and self.selected_tower:
                if event.key == pygame.K_SPACE: 
                    self.selected_tower.use_skill(self.enemies, self.grid)
                elif event.key == pygame.K_u: 
                    self.upgrade_selected()
                elif event.key == pygame.K_DELETE:
                    self.sell_selected()
                elif event.key == pygame.K_m: 
                    self.merge_source = self.selected_tower
                    self.flash_hud_msg('Select same tower to merge', is_bad=False)
                    
        if self.paused:
            if self.pause_overlay.handle_event(event) == 'resume': 
                self.paused = False
            return

        # 2. 마우스 우클릭 처리 (명령 취소/초기화 상태)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.selected_build = None
            self.selected_tower = None
            self.merge_source = None
            return

        # 3. 마우스 좌클릭 처리
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            
            # [개선 핵심] 클릭이 HUD 패널 영역(오른쪽)에서 일어난 경우
            if pos[0] >= BOARD_W:
                action = self.hud.handle_click(pos)
                if action:
                    self.process_hud_action(action)
                return
            
            # 클릭이 게임 보드 영역(왼쪽)에서 일어난 경우
            c, r = self.grid.pixel_to_grid(*pos)
            self.on_grid_click(c, r)

    def process_hud_action(self, action):
        if action.startswith("build_"):
            tower_type = action.replace("build_", "")
            self.selected_build = tower_type
            self.selected_tower = None
            self.merge_source = None
        elif action == 'skill' and self.selected_tower:
            self.selected_tower.use_skill(self.enemies, self.grid)
        elif action == 'upgrade':
            self.upgrade_selected()
        elif action == 'sell':
            self.sell_selected()
        # ⚠️ elif action == 'start_wave': 이 파트가 삭제되었습니다.
        elif action == 'save':
            self.save()
        elif action == 'title':
            self.manager.replace('title')

    def on_grid_click(self, c, r):
        target = self.tower_at(c, r)
        
        # 머지 대상 소스가 있는 상태에서 다른 타워를 클릭했을 때 머지 시도
        if self.merge_source and target:
            self.try_merge(self.merge_source, target)
            return
            
        # 클릭한 곳에 타wer가 있다면 해당 타워 선택
        if target:
            self.selected_tower = target
            self.selected_build = None
            return
            
        # 클릭한 곳이 빈칸이고 타워 구매/설정이 활성화된 상태라면 배치 시도
        if self.selected_build: 
            self.place_tower(self.selected_build, c, r)

    def tower_at(self, c, r): 
        return next((t for t in self.towers if t.grid_pos == (c, r)), None)

    def place_tower(self, tower_type, c, r):
        if not self.grid.is_placeable(c, r): 
            self.flash_hud_msg('Use an empty tile')
            return
            
        cost = TOWER_STATS[tower_type]['cost'][0]
        if not self.economy.can_afford(cost):
            self.flash_hud_msg('Not enough gold')
            return
            
        self.grid.place_tower(c, r)
        new_path = self.pathfinder.find_path(self.grid)
        
        if not new_path: 
            self.grid.remove_tower(c, r)
            self.flash_hud_msg('Cannot block path')
            return
            
        if not self.economy.spend(cost): 
            self.flash_hud_msg('Not enough gold')
            return
            
        cls = {'bomb': BombTower, 'lightning': LightningTower, 'thorn': ThornTower, 'random': RandomTower}[tower_type]
        tower = cls((c, r))
        self.towers.append(tower)
        self.grid.path = new_path
        self.selected_tower = tower
        self.selected_build = None  # 건설 성공 후 하이라이트 해제
        
        for e in self.enemies: 
            e.set_path(self.grid.path)

    def try_merge(self, a, b):
        # 0. 두 타워가 각각 merge 가능 타워인지 확인
        if a.upgrade_level != MAX_UPGRADE_LEVEL or b.upgrade_level != MAX_UPGRADE_LEVEL:
            self.flash_hud_msg('Both Tower need to be level 5 for merge')
            self.merge_source = None
            return
        
        # 1. [기본 조건 검사] 종류와 합체 레벨이 같은지 확인
        if a is b or a.tower_type != b.tower_type or a.merge_level != b.merge_level or a.merge_level >= 3:
            self.flash_hud_msg('Merge needs same type and merge level(under 3)')
            self.merge_source = None
            return
            
        # 2. [사정거리 조건 추가] 두 타워가 서로의 사정거리 내에 있는지 계산
        # 각 타워의 중심점 픽셀 좌표 구하기
        cx1 = a.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
        cy1 = a.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        cx2 = b.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
        cy2 = b.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        
        # 두 타워 사이의 실제 픽셀 거리 계산
        distance = math.hypot(cx2 - cx1, cy2 - cy1)
        
        # 각 타워의 실제 픽셀 사정거리 구하기 (Tower 클래스 내부 연산 규칙 적용)
        r1 = a.attack_range * CELL_SIZE
        r2 = b.attack_range * CELL_SIZE
        
        # 판정: 만약 거리가 어느 한쪽의 사정거리라도 벗어난다면 머지 차단!
        if distance > r1 or distance > r2:
            self.flash_hud_msg('Too far to merge! Out of range') # 사정거리 밖 경고 메시지 출력
            self.merge_source = None
            return

        #3. [성공] 모든 조건을 통과했으므로 실제 합체 진행
        pos = b.grid_pos
        new = a.__class__(pos, a.merge_level + 1, 0)
        
        self.towers.remove(a)
        self.towers.remove(b)
        self.grid.remove_tower(*a.grid_pos)
        self.grid.remove_tower(*b.grid_pos)
        self.grid.place_tower(*pos)
        
        if isinstance(new, RandomTower) and new.merge_level == 3: 
            new = new.transform()
            
        self.towers.append(new)
        self.selected_tower = new
        self.merge_source = None
        self.recalc_path()
        self.flash_hud_msg('Merged successfully!', is_bad=False) 

    def upgrade_selected(self):
        if not self.selected_tower: 
            return
        if self.selected_tower.upgrade(self.economy):
            self.flash_hud_msg('Upgrade successful!', is_bad=False)
        else:
            self.flash_hud_msg('Upgrade unavailable / Max Level')

    def sell_selected(self):
        if not self.selected_tower: 
            return
        t = self.selected_tower
        t.sell(self.economy)
        self.towers.remove(t)
        self.grid.remove_tower(*t.grid_pos)
        self.selected_tower = None
        self.recalc_path()
        self.flash_hud_msg('Tower sold', is_bad=False)

    def save(self):
        self.manager.save_manager.save({
            'stage_id': self.stage_id,
            'gold': self.economy.gold,
            'hp': self.castle_hp.hp,
            'wave': self.wave_manager.to_dict(),
            'towers': [t.to_dict() for t in self.towers]
        })
        self.flash_hud_msg('Saved completely', is_bad=False)

    def restore(self, data):
        self.economy = Economy(data.get('gold', 450))
        self.castle_hp = CastleHP(data.get('hp', 30))
        self.wave_manager = WaveManager(self.economy, self.stage_id)
        self.wave_manager.restore(data.get('wave', {}))
        self.towers = []
        for td in data.get('towers', []):
            t = Tower.from_dict(td)
            self.towers.append(t)
            self.grid.place_tower(*t.grid_pos)
        self.recalc_path()

    def update(self, dt):
        self.hud.update(dt)
        if self.paused: 
            return
            
        self.grid.update_thorn_overlays(dt)
        self.effect_manager.update(dt)
        self.enemies.extend(self.wave_manager.update(dt, self.grid.path, self.effect_manager))
        
        if getattr(self.wave_manager, 'just_loaded', False) and len(self.enemies) > 0:
            self.wave_manager.just_loaded = False

        for e in self.enemies:
            c, r = self.grid.pixel_to_grid(*e.pixel_pos)
            if self.grid.is_thorn(c, r): 
                e.take_damage(10 * dt)
                e.apply_slow(0.45, 0.2)
            e.move(dt)
            if e.reached_end: 
                self.castle_hp.take_damage(e.castle_damage)
                
        for t in self.towers:
            ps = t.update(dt, self.enemies)
            for p in ps:
                if hasattr(p, 'set_enemies'):
                    p.set_enemies(self.enemies)
            self.projectiles.extend(ps)
            
        for p in self.projectiles: 
            p.update(dt)
            
        self.cleanup()
        self.check_end()

    def cleanup(self):
        for e in [e for e in self.enemies if not e.alive]: 
            self.economy.earn(e.gold)
        self.enemies = [e for e in self.enemies if e.alive and not e.reached_end]
        self.projectiles = [p for p in self.projectiles if p.alive]
        if self.wave_manager.spawner_done and not self.enemies and not self.wave_manager.all_clear: 
            self.wave_manager.on_wave_enemies_cleared()

    def check_end(self):
        if self.castle_hp.is_dead(): 
            self.end('lose')
        elif self.wave_manager.all_clear and not self.enemies: 
            self.end('win')

    def end(self, result):
        score = self.score_system.calc_score(self.wave_manager.current_wave, self.castle_hp.hp, self.economy.gold)
        self.manager.save_manager.delete()
        self.manager.replace('end', result=result, score=score)

    def draw(self, surface):
        surface.fill(COLOR_BG)
        self.grid.draw(surface)
        
        # [연동 반영] selected_tower_type 대신 selected_build 변수로 가이드 서클 드로우 변경
        if self.selected_build:
            mx, my = pygame.mouse.get_pos()
            if mx < BOARD_W:
                c, r = self.grid.pixel_to_grid(mx, my)
                temp = {'bomb': BombTower, 'lightning': LightningTower, 'thorn': ThornTower, 'random': RandomTower}[self.selected_build]((c, r))
                temp.draw_range(surface)
                
        for e in self.enemies: 
            e.draw(surface)
        for t in self.towers: 
            t.draw(surface)
        if self.selected_tower: 
            self.selected_tower.draw_range(surface)
        for p in self.projectiles: 
            p.draw(surface)
            
        self.effect_manager.draw(surface)
        
        # HUD 렌더링 (현재의 GameScene 객체를 그대로 넘겨 최신 상태 추적 가능)
        self.hud.draw(surface, self)
        
        if self.paused: 
            self.pause_overlay.draw(surface)

class EndScene(BaseScene):
    def __init__(self,manager,result,score): 
        super().__init__(manager)
        self.manager.audio.play_bgm('end')
        self.result=result
        self.score=score
        self.name=''
        self.font=pygame.font.SysFont(None,56)
        self.small=pygame.font.SysFont(None,28)
        self.saved=False
    def handle_event(self,event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_RETURN:
                if not self.saved: 
                    self.manager.save_manager.add_ranking(self.name or 'PLAYER',self.score)
                    self.saved=True
                self.manager.replace('title')
            elif event.key==pygame.K_BACKSPACE: 
                self.name=self.name[:-1]
            elif len(self.name)<12 and event.unicode and event.unicode.isprintable(): 
                self.name+=event.unicode
    def draw(self,surface):
        surface.fill((24,20,30))
        title=self.font.render('VICTORY' if self.result=='win' else 'DEFEAT',True,(255,235,130))
        surface.blit(title,title.get_rect(center=(SCREEN_W//2,150)))
        for i,line in enumerate([f'Score: {self.score}','Type name and press ENTER',self.name or '_']):
            img=self.small.render(line,True,COLOR_TEXT)
            surface.blit(img,img.get_rect(center=(SCREEN_W//2,240+i*40)))

class RankingScene(BaseScene):
    def __init__(self,manager): 
        super().__init__(manager)
        self.manager.audio.play_bgm('ranking')
        self.font=pygame.font.SysFont(None,52)
        self.small=pygame.font.SysFont(None,28)

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN or event.type==pygame.MOUSEBUTTONDOWN: self.manager.replace('title')

    def draw(self,surface):
        surface.fill((18,22,32))
        title=self.font.render('Ranking',True,(255,235,130))
        surface.blit(title,title.get_rect(center=(SCREEN_W//2,80)))
        ranks=self.manager.save_manager.load_rankings()
        if not ranks: 
            ranks=[{'name':'No records','score':0}]
        for i,r in enumerate(ranks[:10],1):
            img=self.small.render(f"{i:2}. {r['name']}  {r['score']}",True,COLOR_TEXT)
            surface.blit(img,(SCREEN_W//2-130,130+i*32))
        msg=self.small.render('Press any key to return',True,(180,180,190))
        surface.blit(msg,msg.get_rect(center=(SCREEN_W//2,550)))

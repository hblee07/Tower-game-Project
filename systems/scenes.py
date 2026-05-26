import pygame
import math
from settings import *
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
        
        # 🔒 [스테이지 해금 정보 관리]
        # 랭킹처럼 세이브 매니저를 통해 관리하도록 연동합니다.
        self.unlocked_stages = self.save_manager.load_rankings() # 임시 혹은 기본값 세팅용
        # 만약 세이브매니저에 따로 스테이지 저장 기능이 없다면, 여기 매니저 레벨에서 우선 상태를 전역 관리합니다.
        if not hasattr(self, 'unlocked_stages_dict'):
            self.unlocked_stages_dict = {1: True, 2: False, 3: False} # 1층만 열림, 2/3층 잠김

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
            return EndScene(self, kwargs.get('result','lose'), kwargs.get('score',0), kwargs.get('stage_id', 1))
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
        
        # 🛠️ [Stage 3 버튼 추가 및 레이아웃 재배치] y간격을 균등 조정했습니다.
        self.buttons=[('Stage 1',pygame.Rect(cx-120,160,240,40),'stage1'),
                      ('Stage 2',pygame.Rect(cx-120,210,240,40),'stage2'),
                      ('Stage 3',pygame.Rect(cx-120,260,240,40),'stage3'), # 🆕 Stage 3 추가!
                      ('Continue',pygame.Rect(cx-120,310,240,40),'continue'),
                      ('Ranking',pygame.Rect(cx-120,360,240,40),'ranking'),
                      ('Quit',pygame.Rect(cx-120,410,240,40),'quit')]
                      
    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for _,rect,act in self.buttons:
                if rect.collidepoint(event.pos):
                    # 🔒 [클릭 제어] 잠겨있는 스테이지라면 클릭 무시
                    if act == 'stage1' and self.manager.unlocked_stages_dict.get(1):
                        self.manager.replace('game',stage_id=1)
                    elif act == 'stage2' and self.manager.unlocked_stages_dict.get(2):
                        self.manager.replace('game',stage_id=2)
                    elif act == 'stage3' and self.manager.unlocked_stages_dict.get(3): # 🆕 Stage 3 진입
                        self.manager.replace('game',stage_id=3)
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
        title=self.font.render('Tower Defense Game',True,(255,235,130))
        surface.blit(title,title.get_rect(center=(SCREEN_W//2,90)))
        
        for text,rect,act in self.buttons:
            # 🔒 [잠금 UI 시각화] 스테이지 종류에 따라 해금 상태 파악
            enabled = True
            if act == 'stage1': enabled = self.manager.unlocked_stages_dict.get(1, False)
            elif act == 'stage2': enabled = self.manager.unlocked_stages_dict.get(2, False)
            elif act == 'stage3': enabled = self.manager.unlocked_stages_dict.get(3, False)
            elif act == 'continue': enabled = self.manager.save_manager.has_save()
            
            # 잠겨있으면 어두운 회색색상 (45, 48, 55), 열려있으면 파란빛 회색 (70, 82, 96)
            pygame.draw.rect(surface,(70,82,96) if enabled else (40,42,48),rect,border_radius=8)
            pygame.draw.rect(surface,(185,190,200) if enabled else (90,95,100),rect,2,border_radius=8)
            
            # 잠겨있으면 글씨도 어둡게 렌더링
            display_text = text if enabled or 'Stage' not in text else f"{text} (Locked)"
            img=self.small.render(display_text, True, COLOR_TEXT if enabled else (100,100,100))
            surface.blit(img,img.get_rect(center=rect.center))

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
            if not self.wave_manager.all_clear and not self.wave_manager.active and not self.wave_manager.waiting_for_clear: 
                self.wave_manager.start_next_wave(self.grid.path, self.effect_manager)

    def recalc_path(self): 
        # 1. 맵의 새로운 최단 경로 계산 (타워가 사라진 상태의 지름길)
        self.grid.path = self.pathfinder.find_path(self.grid)
        
        # 2. 게임 씬이 처음 생성될 때(__init__) 아직 enemies 리스트가 없다면 건너뛰도록 방어
        if hasattr(self, 'enemies'):
            for e in self.enemies: 
                e.set_path(self.grid.path)
    
    def flash_hud_msg(self, text, is_bad=True):
        self.message = text
        self.message_bad = is_bad
        self.hud.flash_invalid(text)

    def handle_event(self, event):
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

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.selected_build = None
            self.selected_tower = None
            self.merge_source = None
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if pos[0] >= BOARD_W:
                action = self.hud.handle_click(pos)
                if action:
                    self.process_hud_action(action)
                return
            
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
        elif action == 'save':
            self.save()
        elif action == 'title':
            self.manager.replace('title')

    def on_grid_click(self, c, r):
        target = self.tower_at(c, r)
        if self.merge_source and target:
            self.try_merge(self.merge_source, target)
            return
        if target:
            self.selected_tower = target
            self.selected_build = None
            return
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
            
        # 1. 그리드에 타워를 가상으로 배치하고 새 경로를 계산합니다.
        self.grid.place_tower(c, r)
        new_path = self.pathfinder.find_path(self.grid)
        
        # 길막 방지 검사
        if not new_path: 
            self.grid.remove_tower(c, r)
            self.flash_hud_msg('Cannot block path')
            return
            
        if not self.economy.spend(cost): 
            self.grid.remove_tower(c, r)
            self.flash_hud_msg('Not enough gold')
            return
            
        cls = {'bomb': BombTower, 'lightning': LightningTower, 'thorn': ThornTower, 'random': RandomTower}[tower_type]
        tower = cls((c, r))
        self.towers.append(tower)
        
        # 💡 [여기서부터 핵심 경로 분기 로직]
        tower_pos = (c, r)
        
        self.grid.path = new_path
        
        for e in self.enemies: 
            e.set_path(self.grid.path)

        # 8. UI 선택 상태 초기화
        self.selected_tower = tower
        self.selected_build = None

    def try_merge(self, a, b):
        if a.upgrade_level != MAX_UPGRADE_LEVEL or b.upgrade_level != MAX_UPGRADE_LEVEL:
            self.flash_hud_msg('Both Tower need to be level 5 for merge')
            self.merge_source = None
            return
        if a is b or a.tower_type != b.tower_type or a.merge_level != b.merge_level or a.merge_level >= 3:
            self.flash_hud_msg('Merge needs same type and merge level(under 3)')
            self.merge_source = None
            return
            
        cx1 = a.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
        cy1 = a.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        cx2 = b.grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
        cy2 = b.grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
        distance = math.hypot(cx2 - cx1, cy2 - cy1)
        r1 = a.attack_range * CELL_SIZE
        r2 = b.attack_range * CELL_SIZE
        
        if distance > r1 or distance > r2:
            self.flash_hud_msg('Too far to merge! Out of range')
            self.merge_source = None
            return

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
        
        # 🔒 [해금 로직 연동] 스테이지를 이겼을 때(win) 다음 스테이지 잠금을 풀어줍니다.
        if result == 'win':
            next_stage = self.stage_id + 1
            if next_stage in self.manager.unlocked_stages_dict:
                self.manager.unlocked_stages_dict[next_stage] = True
                
        self.manager.save_manager.delete()
        # EndScene으로 현재 끝난 스테이지 ID도 같이 넘겨줍니다.
        self.manager.replace('end', result=result, score=score, stage_id=self.stage_id)

    def draw(self, surface):
        surface.fill(COLOR_BG)
        self.grid.draw(surface)
        
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
        self.hud.draw(surface, self)
        if self.paused: 
            self.pause_overlay.draw(surface)

class EndScene(BaseScene):
    def __init__(self,manager,result,score, stage_id=1): 
        super().__init__(manager)
        self.manager.audio.play_bgm('end')
        self.result=result
        self.score=score
        self.stage_id = stage_id
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
        
        # 👑 스테이지 클리어 문구 고도화 (예: Stage 1 VICTORY)
        status_text = f'Stage {self.stage_id} VICTORY' if self.result=='win' else 'DEFEAT'
        title=self.font.render(status_text,True,(255,235,130))
        surface.blit(title,title.get_rect(center=(SCREEN_W//2,150)))
        for i,line in enumerate([f'Score: {self.score}','Type name and press ENTER',self.name or '_']):
            img=self.small.render(line,True,COLOR_TEXT)
            surface.blit(img,img.get_rect(center=(SCREEN_W//2,240+i*40)))

# scenes.py 파일 최하단에 그대로 붙여넣으세요

class RankingScene(BaseScene):
    def __init__(self, manager): 
        super().__init__(manager)
        self.manager.audio.play_bgm('ranking')
        self.font = pygame.font.SysFont(None, 48)  
        self.small = pygame.font.SysFont(None, 24) 

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN: 
            self.manager.replace('title')

    def draw(self, surface):
        surface.fill((18, 22, 32))
        
        # 1. 타이틀 그리기
        title = self.font.render('Ranking Table', True, (255, 235, 130))
        surface.blit(title, title.get_rect(center=(SCREEN_W // 2, 60)))
        
        ranks = self.manager.save_manager.load_rankings()
        if not ranks: 
            ranks = [{'name': 'No records', 'score': 0}]
            
        # 최대 20등까지 가져와서 좌우 2열로 배치
        for i, r in enumerate(ranks[:20], 1):
            # 텍스트 포맷팅 (등수와 이름을 예쁘게 결합)
            text_str = f"{i:>2}. {r['name']:<12} {r['score']:,}"
            img = self.small.render(text_str, True, COLOR_TEXT)
            
            if i <= 10:
                # 1~10등: 왼쪽 열 (X 좌표를 화면 중앙 기준 왼쪽으로 배치)
                start_x = SCREEN_W // 2 - 240
                # i가 1일 때 140, 10일 때 464에 그려짐
                start_y = 140 + (i - 1) * 36 
            else:
                # 11~20등: 오른쪽 열 (X 좌표를 화면 중앙 기준 오른쪽으로 배치)
                start_x = SCREEN_W // 2 + 20
                # i가 11일 때 140, 20일 때 464에 그려져서 왼쪽 열과 완벽하게 높이가 맞음!
                start_y = 140 + (i - 11) * 36 
                
            surface.blit(img, (start_x, start_y))
            
        # 2. 하단 안내 메시지
        msg = self.small.render('Press any key to return', True, (180, 180, 190))
        surface.blit(msg, msg.get_rect(center=(SCREEN_W // 2, 540)))
import pygame
import math
import random
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
        
        self.unlocked_stages = self.save_manager.load_rankings() 
        
        # 🔓 [잠금 기능 해제] 모든 스테이지를 처음부터 True(해금)로 설정합니다.
        if not hasattr(self, 'unlocked_stages_dict'):
            self.unlocked_stages_dict = {1: True, 2: True, 3: True} # 2, 3층도 전부 True로 변경!

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
        
        self.buttons=[('Stage 1',pygame.Rect(cx-120,160,240,40),'stage1'),
                      ('Stage 2',pygame.Rect(cx-120,210,240,40),'stage2'),
                      ('Stage 3',pygame.Rect(cx-120,260,240,40),'stage3'), 
                      ('Continue',pygame.Rect(cx-120,310,240,40),'continue'),
                      ('Ranking',pygame.Rect(cx-120,360,240,40),'ranking'),
                      ('Quit',pygame.Rect(cx-120,410,240,40),'quit')]
                      
    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for _,rect,act in self.buttons:
                if rect.collidepoint(event.pos):
                    # 🔓 [클릭 제한 해제] 잠금 검사 없이 누르는 대로 즉시 해당 스테이지로 진입합니다.
                    if act == 'stage1':
                        self.manager.replace('game',stage_id=1)
                    elif act == 'stage2':
                        self.manager.replace('game',stage_id=2)
                    elif act == 'stage3': 
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
            # 🔓 [UI 상시 활성화] 모든 버튼이 항상 활성화된 밝은 스타일로 그려집니다.
            enabled = True
            if act == 'continue': enabled = self.manager.save_manager.has_save()
            
            # 모든 스테이지 버튼은 항상 활성화 색상(70, 82, 96)으로 통일됩니다.
            pygame.draw.rect(surface,(70,82,96) if enabled else (40,42,48),rect,border_radius=8)
            pygame.draw.rect(surface,(185,190,200) if enabled else (90,95,100),rect,2,border_radius=8)
            
            # 더 이상 (Locked) 문구를 붙이지 않고 정직하게 스테이지 이름만 띄웁니다.
            img=self.small.render(text, True, COLOR_TEXT if enabled else (100,100,100))
            surface.blit(img,img.get_rect(center=rect.center))

class GameScene(BaseScene):
    def __init__(self, manager, stage_id, save_data=None):
        super().__init__(manager)
        self.manager.audio.play_bgm('game')
        self.stage_id = stage_id
        self.grid = Grid()
        self.grid.set_theme(stage_id) 
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
        # 1. 기존 경로를 변수에 백업해둡니다.
        old_path = self.grid.path
        
        # 2. 새로운 최단 경로를 계산해서 적용합니다.
        new_path = self.pathfinder.find_path(self.grid)
        self.grid.path = new_path
        
        # 3. ★ [핵심] 기존 경로와 새 경로가 '실제로 다를 때만' 적들에게 통보합니다.
        if old_path != new_path:
            if hasattr(self, 'enemies'):
                for e in self.enemies: 
                    e.set_path(new_path)
    
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
            
        self.grid.place_tower(c, r)
        new_path = self.pathfinder.find_path(self.grid)
        
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
        
        # 1. 기존 경로 백업
        old_path = self.grid.path
        
        # 2. 새 경로 적용
        self.grid.path = new_path

        # 3. ★ 실제로 경로가 변경되었을 때만 적들의 위치를 보정합니다.
        if old_path != new_path:
            for e in self.enemies: 
                e.set_path(new_path)

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

        if isinstance(a, RandomTower) and a.merge_level ==2:
            new = random.choice([BombTower,LightningTower,ThornTower])(pos, 3, 0)
        else:
            new = a.__class__(pos, a.merge_level + 1, 0)
        
        self.towers.remove(a)
        self.towers.remove(b)
        self.grid.remove_tower(*a.grid_pos)
        self.grid.remove_tower(*b.grid_pos)
        self.grid.place_tower(*pos)
            
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
        
        # 💡 [구조 유지] 내부 해금 로직 딕셔너리 업데이트 연동은 남겨두어 에러를 방지하되, 
        # 이미 모두 열려있기 때문에 게임 플레이 및 잠금 유무에 전혀 영향을 주지 않습니다.
        if result == 'win':
            next_stage = self.stage_id + 1
            if next_stage in self.manager.unlocked_stages_dict:
                self.manager.unlocked_stages_dict[next_stage] = True
                
        self.manager.save_manager.delete()
        self.manager.replace('end', result=result, score=score, stage_id=self.stage_id)

    def draw(self, surface):
        surface.fill(self.grid.theme['bg'])

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
        status_text = f'Stage {self.stage_id} VICTORY' if self.result=='win' else 'DEFEAT'
        title=self.font.render(status_text,True,(255,235,130))
        surface.blit(title,title.get_rect(center=(SCREEN_W//2,150)))
        for i,line in enumerate([f'Score: {self.score}','Type name and press ENTER',self.name or '_']):
            img=self.small.render(line,True,COLOR_TEXT)
            surface.blit(img,img.get_rect(center=(SCREEN_W//2,240+i*40)))

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
        
        title = self.font.render('Ranking Table', True, (255, 235, 130))
        surface.blit(title, title.get_rect(center=(SCREEN_W // 2, 60)))
        
        ranks = self.manager.save_manager.load_rankings()
        if not ranks: 
            ranks = [{'name': 'No records', 'score': 0}]
            
        for i, r in enumerate(ranks[:20], 1):
            text_str = f"{i:>2}. {r['name']:<12} {r['score']:,}"
            img = self.small.render(text_str, True, COLOR_TEXT)
            
            if i <= 10:
                start_x = SCREEN_W // 2 - 240
                start_y = 140 + (i - 1) * 36 
            else:
                start_x = SCREEN_W // 2 + 20
                start_y = 140 + (i - 11) * 36 
                
            surface.blit(img, (start_x, start_y))
            
        msg = self.small.render('Press any key to return', True, (180, 180, 190))
        surface.blit(msg, msg.get_rect(center=(SCREEN_W // 2, 540)))
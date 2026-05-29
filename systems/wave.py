from models.enemy import create_enemy
from settings import WAVE_CLEAR_BONUS, COLOR_GHOST_RED, COLOR_GHOST_PINK, COLOR_GHOST_CYAN, COLOR_GHOST_ORANGE

WAVES = [
    [('rocket_normal', 10), ('boss_rocket', 1)],
    [('pacman_normal', 15), ('boss_pacman', 1)],
    [('ghost_normal', 10), ('boss_ghost_sequence', 1)], # 유령 보스 4종류 큐 예약
    [('pacman_normal', 10), ('pacman_normal', 10), ('boss_pacman', 1), ('boss_rocket', 1)],
    [('boss_ghost_sequence', 1), ('boss_pacman', 1)],
]

class WaveManager:
    def __init__(self, economy=None, stage_id=1):
        self.economy = economy
        self.stage_id = stage_id
        self.current_wave = 0
        self.queue = []
        self.spawn_timer = 0
        self.spawn_interval = 0.75
        self.boss_spawn_interval = 0.2 # 유령 보스 연속 스폰 간격
        self.active = False
        self.all_clear = False
        self.waiting_for_clear = False
        self.scale = 1.0

    def start_next_wave(self, path, effect_manager=None):
        if self.current_wave >= len(WAVES): 
            self.all_clear = True
            return []
        
        self.current_wave += 1
        self.scale = 1 + (self.current_wave - 1) * 0.32 + (self.stage_id - 1) * 0.18
        self.queue = []
        
        for kind, count in WAVES[self.current_wave - 1]:
            if kind == 'boss_ghost_sequence':
                # 보스 유령 시퀀스는 4개의 색상을 연속으로 큐에 삽입
                colors = [COLOR_GHOST_RED, COLOR_GHOST_PINK, COLOR_GHOST_CYAN, COLOR_GHOST_ORANGE]
                for c in colors:
                    self.queue.append(('boss_ghost', c))
            else:
                self.queue += [(kind, None)] * count
                
        self.active = True
        self.waiting_for_clear = True
        self.spawn_timer = 0

    def update(self, dt, path, effect_manager=None):
        made = []
        if not self.active: 
            return made
            
        self.spawn_timer -= dt
        
        while self.queue and self.spawn_timer <= 0:
            kind, ghost_color = self.queue.pop(0)
            
            # 💡 팩토리 함수를 통해 알맞은 자식 클래스 인스턴스 생성!
            new_enemy = create_enemy(kind, path, self.scale, ghost_color)
            made.append(new_enemy)
            
            # 다음 적도 유령 보스면 스폰 간격 단축
            if kind == 'boss_ghost' and self.queue and self.queue[0][0] == 'boss_ghost':
                self.spawn_timer += self.boss_spawn_interval
            else:
                self.spawn_timer += self.spawn_interval
                
        if not self.queue: 
            self.active = False
        return made
    @property
    def spawner_done(self): 
        return not self.active and not self.queue
    def on_wave_enemies_cleared(self):
        if getattr(self,'just_loaded',False):
            return
        if self.waiting_for_clear:
            if self.economy: self.economy.earn(WAVE_CLEAR_BONUS + self.current_wave*25)
            self.waiting_for_clear=False
            if self.current_wave >= len(WAVES): 
                self.all_clear=True
            else: self.start_next_wave(None)
    def to_dict(self): 
        return {'current_wave':self.current_wave, 'all_clear':self.all_clear}
    
    def restore(self, data): 
        self.current_wave=data.get('current_wave',0)
        self.all_clear=data.get('all_clear',False)
        self.active=False
        self.queue=[]
        self.waiting_for_clear=False
        self.just_loaded=True

    def load_current_wave(self, path, effect_manager=None):
        if self.current_wave > len(WAVES) or self.current_wave <= 0:
            return
        
        # 짚고 넘어가기: 이미 restore에서 웨이브 번호를 제대로 맞춰왔기 때문에 1을 더하지 않습니다!
        scale = 1 + (self.current_wave - 1) * 0.32 + (self.stage_id - 1) * 0.18
        
        self.queue = []
        # 데이터 리스트(WAVES)의 인덱스는 0부터 시작하므로 -1을 해주는 규칙은 그대로 유지합니다.
        for kind, count in WAVES[self.current_wave - 1]: 
            self.queue += [(kind,None)] * count
            
        self.scale = scale
        self.active = True
        self.waiting_for_clear = True
        self.spawn_timer = 0


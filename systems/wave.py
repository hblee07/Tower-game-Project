from models.enemy import create_enemy
from settings import WAVE_CLEAR_BONUS, COLOR_GHOST_RED, COLOR_GHOST_PINK, COLOR_GHOST_CYAN, COLOR_GHOST_ORANGE, WAVES

GHOST_BOSS_COLORS = [COLOR_GHOST_RED, COLOR_GHOST_PINK, COLOR_GHOST_CYAN, COLOR_GHOST_ORANGE]


class WaveManager:
    def __init__(self, economy=None, stage_id=1):
        self.economy = economy
        self.stage_id = stage_id
        self.current_wave = 0
        self.queue = []
        self.spawn_timer = 0
        self.spawn_interval = 0.75
        self.boss_spawn_interval = 0.2
        self.active = False
        self.all_clear = False
        self.waiting_for_clear = False
        self.scale = 1.0

    def _build_queue(self, wave_number):
        queue = []
        if wave_number <= 0 or wave_number > len(WAVES):
            return queue
        for kind, count in WAVES[wave_number - 1]:
            if kind == 'boss_ghost_sequence':
                for _ in range(count):
                    queue.extend(('boss_ghost', color) for color in GHOST_BOSS_COLORS)
            else:
                queue.extend((kind, None) for _ in range(count))
        return queue

    def start_next_wave(self, path, effect_manager=None):
        if self.current_wave >= len(WAVES): 
            self.all_clear = True
            return []
        
        self.current_wave += 1
        self.scale = 1 + (self.current_wave - 1) * 0.32 + (self.stage_id - 1) * 0.18
        self.queue = self._build_queue(self.current_wave)
                
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
            
            
            new_enemy = create_enemy(kind, path, self.scale, ghost_color)
            made.append(new_enemy)
            
            
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
        if getattr(self, 'just_loaded', False):
            self.just_loaded = False
            return

        if self.waiting_for_clear:
            if self.economy:
                self.economy.earn(WAVE_CLEAR_BONUS + self.current_wave * 25)

            self.waiting_for_clear = False

            if self.current_wave >= len(WAVES):
                self.all_clear = True
            else:
                self.start_next_wave(None)

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
        
        scale = 1 + (self.current_wave - 1) * 0.32 + (self.stage_id - 1) * 0.18
        
        self.queue = self._build_queue(self.current_wave)
            
        self.scale = scale
        self.active = True
        self.waiting_for_clear = True
        self.spawn_timer = 0


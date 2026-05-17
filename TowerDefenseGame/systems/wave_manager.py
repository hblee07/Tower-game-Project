from models.enemy import Enemy

WAVE_DATA = {
    1: [
        [("goblin", 12, 0.65), ("boss_goblin", 1, 0.9)],
        [("goblin", 15, 0.55), ("orc", 4, 0.8), ("boss_goblin", 1, 0.9)],
        [("goblin", 12, 0.45), ("orc", 9, 0.65), ("boss_orc", 1, 0.9)],
        [("orc", 14, 0.48), ("troll", 5, 0.8), ("boss_orc", 1, 0.9)],
        [("goblin", 12, 0.28), ("orc", 12, 0.42), ("troll", 10, 0.58), ("boss_troll", 1, 0.9)],
    ],
    2: [
        [("goblin", 16, 0.48), ("boss_goblin", 1, 0.8)],
        [("goblin", 14, 0.38), ("orc", 10, 0.62), ("boss_orc", 1, 0.8)],
        [("orc", 18, 0.42), ("troll", 6, 0.62), ("boss_orc", 1, 0.8)],
        [("goblin", 16, 0.25), ("troll", 13, 0.52), ("boss_troll", 1, 0.8)],
        [("orc", 18, 0.30), ("troll", 18, 0.42), ("boss_goblin", 1, 0.5), ("boss_troll", 1, 0.8)],
    ],
}

class WaveManager:
    def __init__(self, stage_id=1, wave_index=0):
        self.stage_id = stage_id
        self.wave_index = wave_index
        self.active = False
        self.spawn_queue = []
        self.spawn_timer = 0
        self.finished_spawning = False

    @property
    def total_waves(self):
        return len(WAVE_DATA[self.stage_id])

    def current_wave_number(self):
        return min(self.wave_index + 1, self.total_waves)

    def start_wave(self):
        if self.active or self.wave_index >= self.total_waves:
            return False
        self.spawn_queue = []
        for enemy_type, count, interval in WAVE_DATA[self.stage_id][self.wave_index]:
            for _ in range(count):
                self.spawn_queue.append((enemy_type, interval))
        self.active = True
        self.finished_spawning = False
        self.spawn_timer = 0.15
        return True

    def update(self, dt, path):
        spawned = []
        if not self.active:
            return spawned
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and self.spawn_queue:
            enemy_type, interval = self.spawn_queue.pop(0)
            multiplier = 1.0 + self.wave_index * 0.22 + (self.stage_id - 1) * 0.18
            spawned.append(Enemy(enemy_type, path, multiplier))
            self.spawn_timer = interval
        if not self.spawn_queue:
            self.finished_spawning = True
        return spawned

    def check_complete(self, enemies):
        if self.active and self.finished_spawning and not enemies:
            self.active = False
            self.wave_index += 1
            return True
        return False

    def all_clear(self):
        return self.wave_index >= self.total_waves and not self.active

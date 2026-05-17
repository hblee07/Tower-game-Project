import os
import math
import wave
import struct
import pygame
from settings import *
from systems.map_manager import MapManager
from systems.wave_manager import WaveManager
from systems.economy import Economy
from systems.save_manager import SaveManager
from models.tower import Tower
from ui.hud import HUD
from ui.screens import Screens

class Game:
    def __init__(self, stage_id=1, data=None):
        if data:
            stage_id = data.get("stage_id", 1)
        self.stage_id = stage_id
        self.map = MapManager(stage_id)
        self.economy = Economy()
        self.wave = WaveManager(stage_id)
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.effects = []
        self.selected_build = None
        self.selected_tower = None
        self.message = "Build towers, then Start Wave."
        self.message_timer = 3
        self.message_bad = False
        self.paused = False
        self.won = False
        self.lost = False
        if data:
            self.load_data(data)

    def load_data(self, data):
        self.economy.gold = data.get("gold", START_GOLD)
        self.economy.hp = data.get("hp", START_HP)
        self.economy.kills = data.get("kills", 0)
        self.economy.wave_cleared = data.get("wave_cleared", 0)
        self.wave.wave_index = data.get("wave_index", 0)
        for td in data.get("towers", []):
            t = Tower(td["type"], td["row"], td["col"])
            t.merge_level = td.get("merge", 1)
            t.upgrade_level = td.get("upgrade", 1)
            t.skill_charge = td.get("skill", 0)
            t.skill_ready = t.skill_charge >= 100
            if self.map.place_tower_cell(t.row, t.col):
                self.towers.append(t)

    def serialize(self):
        return {
            "stage_id": self.stage_id,
            "gold": self.economy.gold,
            "hp": self.economy.hp,
            "kills": self.economy.kills,
            "wave_cleared": self.economy.wave_cleared,
            "wave_index": self.wave.wave_index,
            "towers": [{"type": t.tower_type, "row": t.row, "col": t.col, "merge": t.merge_level, "upgrade": t.upgrade_level, "skill": t.skill_charge} for t in self.towers]
        }

    def set_message(self, text, bad=False):
        self.message = text
        self.message_bad = bad
        self.message_timer = 2.5

    def tower_at(self, r, c):
        for t in self.towers:
            if t.row == r and t.col == c:
                return t
        return None

    def handle_action(self, action):
        if action.startswith("select_"):
            self.selected_build = action.split("_", 1)[1]
            self.selected_tower = None
            self.set_message(f"Selected {self.selected_build}. Click empty tile.")
        elif action == "start_wave":
            self.start_wave()
        elif action == "upgrade":
            self.upgrade_selected()
        elif action == "skill":
            self.cast_selected_skill()
        elif action == "sell":
            self.sell_selected()
        elif action == "save":
            SaveManager.save(self.serialize())
            self.set_message("Saved.")
        elif action == "pause":
            self.paused = not self.paused

    def start_wave(self):
        if self.wave.start_wave():
            self.set_message(f"Wave {self.wave.current_wave_number()} started!")
        else:
            self.set_message("Wave already active or finished.", True)

    def on_map_click(self, pos):
        cell = self.map.pixel_to_cell(*pos)
        if not cell:
            return
        r, c = cell
        existing = self.tower_at(r, c)
        if existing:
            if self.selected_tower and self.selected_tower is not existing:
                if self.selected_tower.can_merge_with(existing):
                    self.merge_towers(self.selected_tower, existing)
                else:
                    self.selected_tower = existing
                    self.selected_build = None
                    self.set_message("Tower selected. Merge requires same type/level and range.", True)
            else:
                self.selected_tower = existing
                self.selected_build = None
                self.set_message("Tower selected. Upgrade / Skill / Sell available.")
            return
        if self.selected_build:
            data = TOWER_DATA[self.selected_build]
            if not self.economy.can_afford(data["cost"]):
                self.set_message("Not enough gold.", True)
                return
            if not self.map.place_tower_cell(r, c):
                self.set_message("Cannot build there. Path must remain open.", True)
                return
            self.economy.spend(data["cost"])
            t = Tower(self.selected_build, r, c)
            self.towers.append(t)
            self.selected_tower = t
            self.selected_build = None
            for e in self.enemies:
                e.set_path(self.map.find_path((int(e.y // TILE_SIZE), int(e.x // TILE_SIZE)), self.map.end) or self.map.path)
            self.set_message(f"Built {data['name']} tower.")
        else:
            self.selected_tower = None
            self.set_message("Select a tower type first.", True)

    def merge_towers(self, keep, remove):
        keep.merge_level += 1
        keep.skill_charge = min(100, keep.skill_charge + 35)
        keep.skill_ready = keep.skill_charge >= 100
        self.towers.remove(remove)
        self.map.remove_tower_cell(remove.row, remove.col)
        self.selected_tower = keep
        self.set_message(f"Merged! {keep.tower_type} is now merge Lv.{keep.merge_level}")

    def upgrade_selected(self):
        t = self.selected_tower
        if not t:
            self.set_message("No tower selected.", True)
            return
        cost = t.upgrade_cost()
        if cost is None:
            self.set_message("Already max upgrade level.", True)
            return
        if not self.economy.spend(cost):
            self.set_message("Not enough gold for upgrade.", True)
            return
        before = int(t.damage)
        t.upgrade_level += 1
        self.set_message(f"Upgrade {before} -> {int(t.damage)} damage.")

    def cast_selected_skill(self):
        t = self.selected_tower
        if not t:
            self.set_message("No tower selected.", True)
            return
        if t.cast_skill(self.enemies, self.projectiles, self.effects):
            self.set_message(f"Skill used: {TOWER_DATA[t.tower_type]['skill_name']}")
        else:
            self.set_message("Skill is not ready.", True)

    def sell_selected(self):
        t = self.selected_tower
        if not t:
            self.set_message("No tower selected.", True)
            return
        value = t.sell_value()
        self.economy.earn(value)
        self.towers.remove(t)
        self.map.remove_tower_cell(t.row, t.col)
        self.selected_tower = None
        self.set_message(f"Sold tower for {value} gold.")

    def update(self, dt):
        if self.paused or self.won or self.lost:
            return
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
        self.enemies.extend(self.wave.update(dt, self.map.path))
        for t in self.towers:
            t.update(dt, self.enemies, self.projectiles, self.effects)
        for p in self.projectiles[:]:
            p.update(dt, self.enemies)
            if p.dead:
                self.projectiles.remove(p)
        for e in self.enemies[:]:
            e.update(dt)
            if e.dead:
                self.economy.earn(e.reward)
                self.economy.kills += 1
                self.enemies.remove(e)
            elif e.reached_end:
                self.economy.damage_castle(e.castle_damage)
                self.enemies.remove(e)
        for fx in self.effects[:]:
            fx["time"] -= dt
            if fx["time"] <= 0:
                self.effects.remove(fx)
        if self.wave.check_complete(self.enemies):
            self.economy.wave_cleared = self.wave.wave_index
            self.economy.earn(self.map.stage["bonus"])
            self.set_message(f"Wave cleared! +{self.map.stage['bonus']} gold")
        if self.economy.hp <= 0:
            self.lost = True
            SaveManager.delete_save()
        if self.wave.all_clear() and not self.enemies:
            self.won = True
            SaveManager.delete_save()

    def draw(self, screen, hud):
        self.map.draw(screen)
        for t in self.towers:
            t.draw(screen, selected=(t is self.selected_tower))
        if self.selected_build:
            mx, my = pygame.mouse.get_pos()
            cell = self.map.pixel_to_cell(mx, my)
            if cell:
                ghost = Tower(self.selected_build, cell[0], cell[1])
                ghost.draw(screen, placing=True)
        for e in self.enemies:
            e.draw(screen)
        for p in self.projectiles:
            p.draw(screen)
        for fx in self.effects:
            alpha = max(0, min(120, int(220 * fx["time"])))
            surf = pygame.Surface((MAP_SIZE, MAP_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*fx["color"], alpha), (int(fx["x"]), int(fx["y"])), int(fx["r"]), 3)
            screen.blit(surf, (0,0))
        hud.draw(screen, self)


def ensure_bgm():
    os.makedirs(ASSET_DIR, exist_ok=True)
    path = os.path.join(ASSET_DIR, "bgm.wav")
    if os.path.exists(path):
        return path
    sample_rate = 22050
    seconds = 2.0
    notes = [220, 277, 330, 247]
    frames = []
    for i in range(int(sample_rate * seconds)):
        t = i / sample_rate
        freq = notes[int(t * 4) % len(notes)]
        value = int(1800 * math.sin(2 * math.pi * freq * t))
        frames.append(struct.pack('<h', value))
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
    return path


def main():
    pygame.init()
    pygame.display.set_caption("Python Tower Defense")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    hud = HUD()
    screens = Screens()
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(ensure_bgm())
        pygame.mixer.music.set_volume(0.18)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    state = "title"
    game = None
    title_buttons = {}
    rank_data = []
    end_name = ""
    end_won = False
    end_score = 0
    running = True

    while running:
        dt = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif state == "title":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if title_buttons.get("stage1") and title_buttons["stage1"].collidepoint(pos):
                        game = Game(1); state = "playing"
                    elif title_buttons.get("stage2") and title_buttons["stage2"].collidepoint(pos):
                        game = Game(2); state = "playing"
                    elif title_buttons.get("continue") and title_buttons["continue"].collidepoint(pos):
                        data = SaveManager.load()
                        if data:
                            game = Game(data=data); state = "playing"
                    elif title_buttons.get("ranking") and title_buttons["ranking"].collidepoint(pos):
                        rank_data = SaveManager.rankings(); state = "ranking"
                    elif title_buttons.get("quit") and title_buttons["quit"].collidepoint(pos):
                        running = False
            elif state == "ranking":
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    state = "title"
            elif state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.selected_build = None; game.selected_tower = None; game.set_message("Selection cleared.")
                    elif event.key == pygame.K_SPACE:
                        game.start_wave()
                    elif event.key == pygame.K_p:
                        game.paused = not game.paused
                    elif event.key == pygame.K_s:
                        SaveManager.save(game.serialize()); game.set_message("Saved.")
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = hud.handle_click(event.pos)
                    if action:
                        game.handle_action(action)
                    elif event.pos[0] < MAP_SIZE:
                        game.on_map_click(event.pos)
            elif state == "end":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        SaveManager.add_ranking(end_name, end_score, game.stage_id, game.economy.wave_cleared)
                        state = "title"
                    elif event.key == pygame.K_ESCAPE:
                        state = "title"
                    elif event.key == pygame.K_BACKSPACE:
                        end_name = end_name[:-1]
                    elif len(end_name) < 12 and event.unicode and event.unicode.isprintable():
                        end_name += event.unicode

        if state == "title":
            title_buttons = screens.draw_title(screen, SaveManager.has_save())
        elif state == "ranking":
            screens.draw_ranking(screen, rank_data)
        elif state == "playing":
            game.update(dt)
            game.draw(screen, hud)
            if game.paused:
                screens.draw_pause(screen)
            if game.won or game.lost:
                end_won = game.won
                end_score = game.economy.score()
                end_name = ""
                state = "end"
        elif state == "end":
            screens.draw_end(screen, end_won, end_score, end_name)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()

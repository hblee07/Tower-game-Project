import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
SAVE_FILE = os.path.join(BASE_DIR, "save_data.json")
RANK_FILE = os.path.join(BASE_DIR, "ranking.json")

GRID_SIZE = 30
TILE_SIZE = 20
MAP_SIZE = GRID_SIZE * TILE_SIZE
PANEL_WIDTH = 300
SCREEN_WIDTH = MAP_SIZE + PANEL_WIDTH
SCREEN_HEIGHT = MAP_SIZE
FPS = 60

START_GOLD = 650
START_HP = 30
MAX_MERGE_LEVEL = 3
MAX_UPGRADE_LEVEL = 5

WHITE = (245, 245, 245)
BLACK = (15, 15, 18)
GRAY = (90, 90, 95)
DARK = (28, 30, 38)
PANEL = (35, 38, 48)
GRID = (55, 59, 70)
PATH = (165, 136, 88)
EMPTY = (62, 93, 72)
WALL = (65, 67, 78)
START = (65, 145, 95)
END = (158, 72, 72)
YELLOW = (240, 206, 80)
RED = (230, 82, 82)
BLUE = (80, 160, 230)
CYAN = (105, 220, 235)
PURPLE = (180, 100, 225)
ORANGE = (235, 145, 60)
GREEN = (95, 210, 115)

TOWER_DATA = {
    "bow": {"name": "Bow", "cost": 90, "damage": 13, "range": 92, "cooldown": 0.36, "color": (80, 175, 255), "projectile_speed": 360, "skill_name": "Rapid Rain"},
    "cannon": {"name": "Cannon", "cost": 135, "damage": 32, "range": 82, "cooldown": 0.95, "color": (240, 145, 65), "projectile_speed": 240, "splash": 48, "skill_name": "Bombard"},
    "ice": {"name": "Ice", "cost": 115, "damage": 7, "range": 88, "cooldown": 0.68, "color": (120, 225, 245), "projectile_speed": 300, "slow": 0.45, "slow_time": 2.0, "skill_name": "Frost Nova"},
}

ENEMY_DATA = {
    "goblin": {"hp": 45, "speed": 52, "reward": 14, "damage": 1, "color": (105, 225, 105)},
    "orc": {"hp": 95, "speed": 38, "reward": 24, "damage": 2, "color": (205, 145, 70)},
    "troll": {"hp": 170, "speed": 27, "reward": 38, "damage": 3, "color": (185, 115, 220)},
    "boss_goblin": {"hp": 360, "speed": 43, "reward": 85, "damage": 5, "color": (80, 255, 140)},
    "boss_orc": {"hp": 620, "speed": 31, "reward": 120, "damage": 7, "color": (255, 160, 85)},
    "boss_troll": {"hp": 920, "speed": 24, "reward": 165, "damage": 10, "color": (225, 120, 255)},
}

STAGES = {
    1: {"name": "Green Maze", "start": (0, 2), "end": (29, 27), "bonus": 85},
    2: {"name": "Stone Spiral", "start": (0, 15), "end": (29, 14), "bonus": 110},
}

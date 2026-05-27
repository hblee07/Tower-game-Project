GRID_SIZE = 30
CELL_SIZE = 20
BOARD_W = GRID_SIZE * CELL_SIZE
HUD_W = 300
SCREEN_W = BOARD_W + HUD_W
SCREEN_H = BOARD_W
FPS = 60
SAVE_FILE = 'savegame.json'
RANKING_FILE = 'ranking.json'
COLOR_GRID = (38, 42, 48)
COLOR_PATH = (92, 86, 70)
COLOR_BG = (18, 20, 28)
COLOR_TEXT = (235, 235, 235)
MAX_MERGE_LEVEL = 3
MAX_UPGRADE_LEVEL = 3
START_GOLD = 1000
START_HP = 30
WAVE_CLEAR_BONUS = 80
TOWER_STATS = {
    'bomb': {'name':'Bomb','cost':[110,170,260],'damage':[36,58,95],'attack_range':[4.3, 4.3, 4.3],
             'attack_speed':[1.7, 1.9, 2.5],'skill_cooldown':500,'sell_ratio':0.3,'upgrade_base':15},
             
    'lightning': {'name':'Lightning','cost':[120,190,280],'damage':[20,34,56],'attack_range':[5.0, 5.3, 5.6],
                  'attack_speed':[0.5, 0.55, 0.6],'skill_cooldown':140,'sell_ratio':0.3,'upgrade_base':16,'chain_count':[2,3,5]},

    'thorn': {'name':'Thorn','cost':[100,160,250],'damage':[6,10,16],'attack_range':[3.2, 3.4, 3.6], 
              'attack_speed':[1.5, 1.6, 1.7],'skill_cooldown':80,'sell_ratio':0.3,'upgrade_base':14,'slow_factor':[0.62,0.52,0.42]},

    'random': {'name':'Random','cost':[40,60,80],'damage':[4, 8],'attack_range':[4.0, 4.3],
               'attack_speed':[2.0, 2.1],'skill_cooldown':100,'sell_ratio':0.3,'upgrade_base':13},
}
ENEMY_STATS = {
    'grunt': {'hp':70,'speed':55,'gold':16,'damage':1,'color':(210,80,80)},
    'runner': {'hp':45,'speed':90,'gold':20,'damage':1,'color':(230,170,60)},
    'tank': {'hp':160,'speed':35,'gold':34,'damage':2,'color':(110,190,110)},
    'boss': {'hp':520,'speed':35,'gold':120,'damage':5,'color':(170,80,220)},
}


# settings.py 예시 (이런 형태로 색상을 추가해 주시면 됩니다!)
STAGE_THEMES = {
    1: {
        'bg': (5, 5, 15),          # 기본 전체 배경 (완전 어두운 남색)
        'neon_line': (33, 33, 255),  # 🥇 1스테이지: 클래식 팩맨 네온 블루 선
        'neon_close': (15, 15, 40), # 벽 안쪽 채우기 색상
        'grid': (20, 20, 30), 'path': (255, 255, 255) # 기존 변수 유지용
    },
    2: {
        'bg': (15, 5, 5),           # 🥈 2스테이지: 불타는 사막 테마 배경
        'neon_line': (255, 50, 50),  # 네온 레드 선
        'neon_close': (40, 15, 15),
        'grid': (30, 20, 20), 'path': (255, 255, 255)
    },
    3: {
        'bg': (5, 15, 10),          # 🥉 3스테이지: 독성 물질/숲 테마 배경
        'neon_line': (50, 255, 50),  # 네온 그린 선
        'neon_close': (15, 40, 20),
        'grid': (20, 30, 25), 'path': (255, 255, 255)
    }
}
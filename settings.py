GRID_SIZE = 30
CELL_SIZE = 20
BOARD_W = GRID_SIZE * CELL_SIZE
HUD_W = 300
SCREEN_W = BOARD_W + HUD_W
SCREEN_H = BOARD_W
FPS = 60
SAVE_FILE = 'savegame.json'
RANKING_FILE = 'ranking.json'

#색깔들
COLOR_GRID = (38, 42, 48)
COLOR_PATH = (92, 86, 70)
COLOR_BG = (18, 20, 28)
COLOR_TEXT = (235, 235, 235)
COLOR_PACMAN = (255, 255, 0)
COLOR_GHOST_RED = (255, 0, 0)
COLOR_GHOST_PINK = (255, 184, 255)
COLOR_GHOST_CYAN = (0, 255, 255)
COLOR_GHOST_ORANGE = (255, 184, 82)

#최대 레벨, 시작 조건
MAX_MERGE_LEVEL = 3
MAX_UPGRADE_LEVEL = 3
START_GOLD = 1000
START_HP = 30
WAVE_CLEAR_BONUS = 80

WAVES = [
    [('rocket_normal', 10), ('boss_rocket', 1)],
    [('pacman_normal', 15), ('boss_pacman', 1)],
    [('ghost_normal', 10), ('boss_ghost_sequence', 1)],
    [('pacman_normal', 10), ('pacman_normal', 10), ('boss_pacman', 1), ('boss_rocket', 1)],
    [('rocket_normal',10),('boss_ghost_sequence', 1), ('boss_pacman', 1)],
]

TOWER_STATS = {
    'bomb': {'name':'Bomb','cost':[110,170,260],'damage':[360,580,950],'attack_range':[4.3, 4.3, 4.3],
             'attack_speed':[1.7, 1.9, 2.5],'skill_cooldown':5000,'sell_ratio':0.3,'upgrade_base':15},
             
    'lightning': {'name':'Lightning','cost':[120,190,280],'damage':[200,340,560],'attack_range':[5.0, 5.3, 5.6],
                  'attack_speed':[0.5, 0.55, 0.6],'skill_cooldown':1400,'sell_ratio':0.3,'upgrade_base':16,'chain_count':[2,3,5]},

    'thorn': {'name':'Thorn','cost':[100,160,250],'damage':[60,100,160],'attack_range':[3.2, 3.4, 3.6], 
              'attack_speed':[1.5, 1.6, 1.7],'skill_cooldown':800,'sell_ratio':0.3,'upgrade_base':14,'slow_factor':[0.62,0.52,0.42]},

    'random': {'name':'Random','cost':[40,60,80],'damage':[40, 80, 160],'attack_range':[4.0, 4.3, 4.6],
               'attack_speed':[2.0, 2.1, 2.2],'skill_cooldown':1000,'sell_ratio':0.3,'upgrade_base':13},
}

ENEMY_STATS = {
    #일반
    #유령 일반 - HP 많음
    'ghost_normal': {'hp': 1500, 'speed': 50, 'gold': 20, 'damage': 1, 'color': (200, 200, 0), 'is_boss': False},
    #로켓 일반 - 속도 빠름
    'rocket_normal': {'hp': 600, 'speed': 100, 'gold': 30, 'damage': 1, 'color': (200, 200, 200), 'is_boss': False},
    #팩맨 일반 - 중간
    'pacman_normal': {'hp': 1000, 'speed': 75, 'gold': 25, 'damage': 1, 'color': (50, 255, 180), 'is_boss': False},

    #보스
    #유령 보스 - HP 매우 많음, 다수(4마리)
    'boss_ghost': {'hp': 6000, 'speed': 50, 'gold': 150, 'damage': 5, 'color': COLOR_GHOST_RED, 'is_boss': True},
    #로켓 보스 - 속도 매우 빠름, HP 적음, 성 공격력 셈
    'boss_rocket': {'hp': 1200, 'speed': 110, 'gold': 150, 'damage': 20, 'color': (50, 50, 200), 'is_boss': True},
    #팩맨 보스 - 죽는 순간 타워 먹기
    'boss_pacman': {'hp': 4000, 'speed': 70, 'gold': 200, 'damage': 10, 'color': COLOR_PACMAN, 'is_boss': True},
}

GHOST_BOSS_SPEED = [52, 48, 44, 40] #

STAGE_THEMES = {
    1: {
        'bg': (5, 5, 15),          
        'neon_line': (33, 33, 255),  
        'neon_close': (15, 15, 40), 
        'grid': (20, 20, 30), 'path': (255, 255, 255) 
    },
    2: {
        'bg': (10, 5, 5),           
        'neon_line': (255, 50, 50),  
        'neon_close': (40, 15, 15),
        'grid': (30, 20, 20), 'path': (255, 255, 255)
    },
    3: {
        'bg': (5, 15, 10),          
        'neon_line': (50, 255, 50),  
        'neon_close': (15, 40, 20),
        'grid': (20, 30, 25), 'path': (255, 255, 255)
    }
}
 #bgm은 geometry dash의 음악을 사용함
BGM_PATH = {
    'Title_Screen': 'Title Screen_Daycore - RobTop - Geometry Dash Menu Theme (Slowed Down).mp3',
    'Stage1': 'Stage1_MDK - Fingerbang.mp3',
    'Stage2': 'Stage2_DJVI - Back On Track.mp3',
    'Stage3': 'Stage3_Waterflame_Jumper.mp3',
    'Rank_Screen': 'Rank Screen_MDK - Fingerbang.mp3'
}
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
             'attack_speed':[1.7, 1.9, 2.5],'skill_cooldown':120,'sell_ratio':0.3,'upgrade_base':15},
             
    'lightning': {'name':'Lightning','cost':[120,190,280],'damage':[20,34,56],'attack_range':[5.0, 5.3, 5.6],
                  'attack_speed':[0.5, 0.55, 0.6],'skill_cooldown':140,'sell_ratio':0.3,'upgrade_base':16,'chain_count':[2,3,5]},

    'thorn': {'name':'Thorn','cost':[100,160,250],'damage':[6,10,16],'attack_range':[3.2, 3.4, 3.6], 
              'attack_speed':[1.5, 1.6, 1.7],'skill_cooldown':160,'sell_ratio':0.3,'upgrade_base':14,'slow_factor':[0.62,0.52,0.42]},

    'random': {'name':'Random','cost':[40,60,80],'damage':[4, 8],'attack_range':[4.0, 4.3],
               'attack_speed':[2.0, 2.1],'skill_cooldown':100,'sell_ratio':0.3,'upgrade_base':13},
}
ENEMY_STATS = {
    'grunt': {'hp':70,'speed':55,'gold':16,'damage':1,'color':(210,80,80)},
    'runner': {'hp':45,'speed':90,'gold':20,'damage':1,'color':(230,170,60)},
    'tank': {'hp':160,'speed':35,'gold':34,'damage':2,'color':(110,190,110)},
    'boss': {'hp':520,'speed':30,'gold':120,'damage':5,'color':(170,80,220)},
}

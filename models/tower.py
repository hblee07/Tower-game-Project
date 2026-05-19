from settings import *

class Tower:
    def __init__(self, row, col, level, type_range):
        self.row = row #격자상 위치(행, 열)
        self.col = col 
        self.level = level
        self.type_range = type_range #타워 타입별 범위
        self.x = self.col * GRID_SIZE + GRID_SIZE // 2
        self.y = self.row * GRID_SIZE + GRID_SIZE // 2
        self.attack_range = 100 * self.type_range * (1 + 0.2*(self.level-1)) #공격범위
        self.merge_range = 800 * self.type_range #merge 가능 범위

    def find_target(self, enemies):
        pass

    def fire(self):
        pass


class BombTower(Tower):
    def __init__(self, row, col, level):
        super().__init__(row, col, level, type_range = 100)

class LightningTower(Tower):
    def __init__(self, row, col, level):
        super().__init__(row, col, level, type_range = 50)

class ThornTower(Tower):
    def __init__(self, row, col, level):
        super().__init__(row, col, level, type_range = 150)

class RandomTower(Tower):
    def __init__(self, row, col, level):
        super().__init__(row, col, level, type_range = 200)


def can_merge_with(tower1, tower2): #merge 가능 판별(type 같음, level 같음, merge range 안에 위치)
    if type(tower1) == type(tower2) and tower1.level == tower2.level and ((tower1.x - tower2.x)**2 + (tower1.y - tower2.y)**2)**0.5 <= tower1.merge_range:
        return True
    return False
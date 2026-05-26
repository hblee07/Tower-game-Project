from settings import START_GOLD, START_HP

class Economy:
    def __init__(self, gold=START_GOLD):
        self.gold = gold
    def can_afford(self, amount): 
        return self.gold >= amount
    def spend(self, amount):
        if self.can_afford(amount): 
            self.gold -= amount
            return True
        return False
    def earn(self, amount): 
        self.gold += int(amount)
    def to_dict(self): 
        return {'gold': self.gold}

class CastleHP:
    def __init__(self, hp=START_HP): 
        self.hp = hp; self.max_hp = START_HP
    def take_damage(self, amount): 
        self.hp = max(0, self.hp - int(amount))
    def is_dead(self): 
        return self.hp <= 0
    def to_dict(self): 
        return {'hp': self.hp}

class ScoreSystem:
    def calc_score(self, wave, hp, gold):
        return int(wave * 1000 + max(0, hp) * 50 + gold)

from settings import START_GOLD, START_HP

class Economy:
    def __init__(self, gold=START_GOLD, hp=START_HP):
        self.gold = gold
        self.hp = hp
        self.kills = 0
        self.wave_cleared = 0

    def can_afford(self, amount):
        return self.gold >= amount

    def spend(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def earn(self, amount):
        self.gold += int(amount)

    def damage_castle(self, amount):
        self.hp -= int(amount)

    def score(self):
        return self.wave_cleared * 1000 + self.hp * 80 + self.gold * 2 + self.kills * 25

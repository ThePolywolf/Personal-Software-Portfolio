from .pokemon import Pokemon
from .player import Player

class Ability:
    def __init__(self, ability):
        self.ability = ability

    @staticmethod
    def Blank():
        return Ability(dict())
    
    def is_blank(self) -> bool:
        return len(self.ability) == 0

    def has_trigger(self, trigger: str) -> bool:
        return trigger in self.ability
    
    def func(self, trigger: str):
        return self.ability[trigger]

    def energy_func(self, trigger: str):
        return self.ability[trigger]
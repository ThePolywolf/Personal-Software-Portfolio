from .energy_pool import EnergyPool, EnergySet
from .attack import Attack
from .data import status as status
from ..file_loader import is_nan

from random import choice

class Pokemon:
    def __init__(self, raw: dict[str, any], uid):
        self.name:str = raw['name']
        self.stage:int = raw['stage']
        self.pre_evo:str = Pokemon.none_or_value(raw['from'])
        self.id:str = raw['id']
        self.uid:int = uid
        self.hp:int = raw['hp']
        self.max_hp:int = raw['hp']
        self.type:str = raw['type']
        self.ability:str = Pokemon.none_or_value(raw['ability'])
        self.weakness:str = Pokemon.none_or_value(raw['weakness'])
        self.retreat:int = Pokemon.none_or_value(raw['retreat'])
        self.rarity:str = Pokemon.rarity_string(raw['rarity'])
        self.status:list[str] = []
        self.energy:EnergyPool = EnergyPool(dict())
        self.move1:Attack = Attack.generate(raw, 1)
        self.move2:Attack = Attack.generate(raw, 2)
        self.__defense: int = 0
        self.__pre_evos: list[str] = []

    @staticmethod
    def none_or_value(item) -> any:
        """
        Returns None if the value is np.nan, else the original value
        """
        return None if is_nan(item) else item

    @staticmethod
    def rarity_string(r:str) -> str:
        """
        Converts a shortened rarity string to its full name
        """
        if r == 'crown': return 'Crown Rare'
    
        val = r[0]
        shape = r[1]

        if shape.lower() == 's':
            shape = 'Star'
        else:
            shape = 'Diamond'

        return f"{val}-{shape}"

    @staticmethod
    def flip_heads() -> bool:
            return choice([0, 1]) == 1
    
    def is_basic(self) -> bool:
        """
        Checks if the pokemon is a basic
        """
        return self.stage == 0

    def moves(self) -> list[Attack]:
        """
        Returns a list of moves the pokemon can use
        """
        return [atk for atk in [self.move1, self.move2] if not atk is None]

    def get_energy_set(self) -> EnergySet:
        """
        Returns the energy set required by this pokemon for its moves
        """
        result = EnergySet.empty()
        for atk in self.moves():
            result.merge(atk.cost.as_set())
        return result
    
    def has_status(self, status: (str | list[str])) -> bool:
        """
        Returns if this Pokemon has the given status condition
        """
        if isinstance(status, list):
            for stat in status:
                if stat in self.status: return True
            return False

        return status in self.status

    def add_status(self, s: str):
        """
        Gives the pokemon the new status
        """
        # TODO override status' (ex. paralysis > sleep override)
        self.status += [s]

    def clear_status(self):
        """
        Clears all pokemon's status'
        """
        self.status = []
    
    def damage(self, damage: int):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def is_koed(self):
        return self.hp <= 0

    def heal(self, heal: int):
        self.hp += heal
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def defend(self, damage: int) -> int:
        """
        Defends agaist the given damage, and returns the new damage
        """
        if self.__defense >= damage: return 0
        return damage - self.__defense
    
    def add_defense(self, defense: int):
        self.__defense += defense

    def reset_defense(self):
        self.__defense = 0

    def is_ex(self) -> bool:
        """
        Checks if this pokemon is an EX type
        """
        return self.name[-2:].lower() == 'ex'
    
    def get_card_stack(self) -> list[str]:
        return self.__pre_evos + [self.id]

    def handle_status_turn_start(self):
        """
        Handles all of the start-of-turn status effects
        """
        if self.has_status(status.Sleep):
            if Pokemon.flip_heads():
                self.status.remove(status.Sleep)
        
        if self.has_status(status.Burned):
            self.damage(20)
            if Pokemon.flip_heads():
                self.status.remove(status.Burned)

        if self.has_status(status.Poisoned):
            self.damage(10)

        if self.has_status(status.Invulnerable):
            self.status.remove(status.Invulnerable)
        
        self.reset_defense()

    def handle_status_turn_end(self):
        """
        Handles all of the end-of-turn status effects
        """
        if self.has_status(status.Sleep):
            if Pokemon.flip_heads():
                self.status.remove(status.Sleep)
        
        if self.has_status(status.Burned):
            self.damage(20)
            if Pokemon.flip_heads():
                self.status.remove(status.Burned)

        if self.has_status(status.Poisoned):
            self.damage(10)

        to_cure = [status.Paralysis, status.Smokescreen, status.NoAttack, status.NoSupport]
        for s in to_cure:
            if self.has_status(s):
                self.status.remove(s)

    def evolve(self, evolution):
        """
        Evolves the current pokemon into the given evolution
        """
        if not isinstance(evolution, Pokemon):
            raise Exception('Can only evolve into another pokmeon')

        # check evolution is valid
        if not self.name == evolution.pre_evo:
            note = f'{evolution.name} does not evolve into {self.name}, needs {evolution.pre_evo}'
            raise Exception(note)

        self.__pre_evos += [self.id]

        # new pokemon carries over health from pre-evolution
        health_delta = evolution.max_hp - self.max_hp
        self.hp += health_delta

        # copy traits from evolution
        self.name = evolution.name
        self.stage = evolution.stage
        self.pre_evo = evolution.pre_evo
        self.id = evolution.id
        # keep uid
        # health set already
        self.max_hp = evolution.max_hp
        self.type = evolution.type
        self.ability = evolution.ability
        self.weakness = evolution.weakness
        self.retreat = evolution.retreat
        self.rarity = evolution.rarity
        self.status = []
        # keep current energy set
        self.move1 = evolution.move1
        self.move2 = evolution.move2

    def print_short(self, prefix: str="", indent:int=0):
        """
        Prints pokemon card data in a single line pretty format
        """
        stage = "Basic" if self.stage == 0 else f"Stage {self.stage}"

        print(f"{"":>{indent}}{prefix}{self.name.title()} ({self.id}) #{self.uid} | {self.type.title()}, {stage} | {self.hp}/{self.max_hp}hp")

    def print(self, indent:int=0):
        """
        Prints pokemon card data in a pretty format
        """
        stage = "Basic" if self.stage == 0 else f"Stage {self.stage}"
        pk_from = "" if self.pre_evo is None else f"<- {self.pre_evo.title()}"

        energy = str(self.energy)

        if len(self.status) == 0:
            status = "<empty>"
        else:
            status = ""
            for s in status:
                status += f"{s.title()}, "
            status = status[:-2]

        retreat = "Free" if self.retreat == 0 else f"{self.retreat} Energy"

        print(f"{"":>{indent}}{self.name.title()} ({self.id}) #{self.uid} | {self.type.title()}, {stage} {pk_from} | {self.hp}/{self.max_hp}hp")
        print(f"{"":>{indent+2}}Energy: {energy}")
        if not self.ability is None: print(f"{"":>{indent+2}}Ability: {self.ability.title()}")
        for move in self.moves():
            move.print_short(indent=indent+2)
        print(f"{"":>{indent+2}}Status: {status}")
        print(f"{"":>{indent+2}}Retreat: {retreat}, {Pokemon.rarity_string(self.rarity)} Rarity")
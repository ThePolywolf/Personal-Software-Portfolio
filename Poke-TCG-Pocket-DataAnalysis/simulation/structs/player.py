from .card import Card
from .energy_pool import EnergySet
from .pokemon import Pokemon

from random import choice, shuffle

class Player:
    @staticmethod
    def from_deck(deck:list[Card]):
        """
        Generates a player from a given starter and hand
        """
        # deck must contain basics
        basics = [card.get_pokemon() for card in deck if card.is_pokemon() and card.get_pokemon().is_basic()]
        if len(basics) == 0:
            raise Exception('Deck contains no basic pokemon')
        
        # get energy pool from sets by all pokemon
        energy_set = EnergySet.empty()
        for card in deck:
            if card.is_pokemon():
                energy_set.merge(card.get_pokemon().get_energy_set())

        # normal-only sets default to water
        energy_set.remove('normal')
        if energy_set.size() == 0:
            energy_set.add('water')

        while True:
            shuffle(deck)
            hand = deck[:5]
            deck = deck[5:]

            basic_count = len([1 for card in hand if card.is_pokemon() and card.get_pokemon().is_basic()])
            if basic_count > 0:
                break

        basic_index = 0
        for card in hand:
            if card.is_pokemon() and card.get_pokemon().is_basic():
                break
            basic_index += 1

        starter = hand[basic_index].get_pokemon()
        hand.remove(hand[basic_index])

        return Player({
            'active' : starter,
            'bench' : [None, None, None],
            'energy_pool': energy_set,
            'deck': deck,
            'hand': hand,
        })

    def __init__(self, data:dict[str, any]):
        self.active:Pokemon = data['active']
        self.bench:list[Pokemon] = data['bench']
        self.energy_set:EnergySet = data['energy_pool']
        self.current_energy:str = None
        self.next_energy:str = None
        self.status:list[str] = []

        self.deck:list[Card] = data['deck']
        self.hand:list[Card] = data['hand']

        self.__used_abilities: set[int] = set()
        self.__evolved_uids: set[int] = set()

        self.__points:int = 0

    def give_points(self, pts: int):
        self.__points += pts

    def has_won(self) -> bool:
        """
        Checks if this player has won from points
        """
        return self.__points >= 3
    
    def has_lost(self) -> bool:
        """
        Checks if this player has lost from no-more pokemon
        """
        return self.active is None and self.bench_count() == 0

    def has_status(self, status: (str | list[str])) -> bool:
        """
        Returns if this Player has the given status condition
        """
        if isinstance(status, list):
            for stat in status:
                if stat in self.status: return True
            return False

        return status in self.status
    
    def add_status(self, s: str):
        """
        Gives the Player the new status s
        """
        self.status += [s]

    def clear_status(self):
        """
        Clears all player status'
        """
        self.status = []

    def all_pokemon(self) -> list[Pokemon]:
        """
        Returns all player pokemon as a list of [active] + bench
        """
        pkmn = [self.active]
        pkmn.extend([pkmn for pkmn in self.bench if not pkmn is None])
        return pkmn

    def reset_evolutions(self):
        """
        Resets evolution tracker to allow pokemon to evolve
        """
        self.__evolved_uids = set()

    def track_evolution(self, uid: int):
        """
        Tracks the given uID as having evolved
        """
        self.__evolved_uids.add(uid)

    def already_evolved(self, uid: int) -> bool:
        """
        Checks if the given uID has already evolved
        """
        return uid in self.__evolved_uids
    
    def reset_abilities(self):
        """
        Resets the used ability tracker to allow their re-use
        """
        self.__used_abilities = set()

    def use_ability(self, uid:int):
        """
        Tracks the uID as having used its ability
        """
        self.__used_abilities.add(uid)

    def reset_uid_ability(self, uid:int):
        """
        Resets the uid to allow it to re-use its ability
        """
        if uid in self.__used_abilities:
            self.__used_abilities.remove(uid)

    def ability_used(self, uid: int) -> bool:
        """
        Checks if the given UId has already used its ability
        """
        return uid in self.__used_abilities
    
    def progress_energy(self):
        """
        Progresses the player energy
        Current Energy <-- Next Energy <-- New energy from pool
        """
        self.current_energy = self.next_energy
        self.next_energy = self.energy_set.get_random()

    def current_pokmeon_names(self) -> list[str]:
        """
        Returns a list of all current player pokemon names
        """
        return [self.active.name] + [pkmn.name for pkmn in self.bench if not pkmn is None]
    
    def bench_pokemon(self) -> list[Pokemon]:
        """
        Returns all pokemon from the bench
        """
        return [pkmn for pkmn in self.bench if not pkmn is None]

    def bench_count(self) -> int:
        """
        Returns the number of pokemon on the bench
        """
        return len([1 for pkmn in self.bench if not pkmn is None])

    def bench_is_full(self) -> bool:
        """
        Returns true only if player bench is full.
        """
        return self.bench_count() == 3
    
    def remove_ko_from_bench(self):
        """
        Replaces koed pokemon on the bench with None
        """
        for i in range(3):
            if self.bench[i] is None:
                continue

            if self.bench[i].is_koed():
                self.bench[i] = None
    
    def first_empty_bench_index(self) -> (int | None):
        """
        Returns the index of the first empty bench slot.

        None if bench is full
        """
        index = 0
        for pkmn in self.bench:
            if pkmn is None:
                return index
            index += 1

        return None
    
    def first_filled_bench_index(self) -> (int | None):
        """
        Returns the index of the first empty bench slot.

        None if bench is empty
        """
        index = 0
        for pkmn in self.bench:
            if not pkmn is None:
                return index
            index += 1

        return None
    
    def count_bench_type(self, type: str):
        """
        Returns the count of the number of benched pokemon of the given type
        """
        bench = self.bench_pokemon()
        return sum([1 if pkmn.type == type else 0 for pkmn in bench])

    def count_bench_pkmn(self, name: str) -> int:
        """
        Returns number of pokemon on the player's bench with the given name
        """
        bench = self.bench_pokemon()
        return sum([1 for pkmn in bench if pkmn.name == name])
    
    def draw_card(self):
        """
        Draws one card from the deck
        """
        if len(self.hand) >= 10:
            return

        if len(self.deck) == 0:
            return
        
        self.hand += [self.deck[0]]
        self.deck = self.deck[1:]

    def shuffle_deck(self):
        shuffle(self.deck)

    def print(self, indent=0):
        if len(self.hand) == 0:
            hand = "<Empty>"
        else:
            hand = ""
            for card in self.hand:
                hand += f"{card.card_name()}, "
            hand = hand[:-2]

        energy_pool = str(self.energy_set)

        if len(self.status) == 0:
            status = "<empty>"
        else:
            status = ""
            for s in status:
                status += f"{s.title()}, "
            status = status[:-2]

        if self.active is None:
            print(f"{"":>{indent}}Active: None")
        else:
            self.active.print_short(prefix="Active: ", indent=indent)
            print(f"{"":>{indent}}        {str(self.active.energy)}")
        
        print(f"{"":>{indent}}Bench:")
        for pkmn in self.bench:
            if pkmn is None: print(f"{"":>{indent+4}}<Empty>")
            else: pkmn.print_short(indent=indent+4)

        next_energy = self.next_energy
        print(f"{"":>{indent}}Energy: {"None" if next_energy is None else next_energy.title()} <- [{energy_pool}]")
        print(f"{"":>{indent}}Status: {status}")
        print(f"{"":>{indent}}Hand: {hand}")
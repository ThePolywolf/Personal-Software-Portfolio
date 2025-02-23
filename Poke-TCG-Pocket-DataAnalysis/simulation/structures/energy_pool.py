from random import choice, randint

__energy_short_to_full = {
    'g' : 'grass',
    'r' : 'fire',
    'w' : 'water',
    'e' : 'electric',
    'p' : 'psychic',
    'f' : 'fighting',
    'd' : 'dark',
    'm' : 'metal',
    'x' : 'normal',
    '*' : 'random'
}

energy_names = [__energy_short_to_full[name] for name in __energy_short_to_full]

def full_energy_name(short: str) -> str:
    if not short in __energy_short_to_full:
        note = f"Short energy name {short} does not exist"
        raise Exception(note)

    return __energy_short_to_full[short]

def is_short_energy_name(short: str) -> bool:
    return short in __energy_short_to_full

class EnergySet:
    def __init__(self, data:set):
        self.__energy: set[str] = data

    @staticmethod
    def empty():
        """
        Creates an empty energy set
        """
        return EnergySet({})

    def energy(self) -> set[str]:
        """
        Returns the set of energy
        """
        return self.__energy

    def get_random(self) -> str:
        """
        Returns a random choice from the set
        """
        return choice(list(self.__energy))
    
    def merge(self, join):
        """
        Merges the join set into the current set. join must be an EnergySet
        """
        if not isinstance(join, EnergySet): 
            raise Exception('Energy set can only merge with another energy set')

        if len(self.__energy) == 0:
            self.__energy = join.energy()
        else:
            self.__energy |= join.energy()

    def remove(self, to_remove: str):
        """
        Removes the given index from the set
        """
        if to_remove in self.__energy:
            self.__energy.remove(to_remove)

    def size(self) -> int:
        """
        Returns the size of the set
        """
        return len(self.__energy)
    
    def total(self) -> int:
        """
        Returns the total energy count
        """
        return sum([count for _, count in self.__energy])
    
    def add(self, to_add: str):
        """
        Add the given addition to the set
        """
        if to_add in self.__energy:
            return
        self.__energy.add(to_add)

    def __str__(self):
        if len(self.__energy) == 0:
            return "<empty>"

        energy_pool = ""
        for energy in self.__energy:
            energy_pool += f"{energy.title()}, "
        
        return energy_pool[:-2]

class EnergyPool:
    def __init__(self, data: dict[str, int] = {}):
        if isinstance(data, str):
            self.__all = data
            self.__energy = dict()
        else:
            self.__energy:dict[str, int] = dict() if data is None else data
            self.__all: str = None

    def is_all(self) -> bool:
        return not self.__all is None

    def as_set(self) -> EnergySet:
        if self.is_all():
            return EnergySet(set([self.__all]))
        return EnergySet(set([name for name, _ in self.__energy.items()]))

    def has_energy(self, name: str) -> bool:
        """
        Checks if the pool contains the given energy type
        """
        if self.is_all():
            return self.__all == name
        return name in self.__energy
    
    def count(self, name: str) -> int:
        """
        Returns the count of the given energy type
        """
        if self.is_all():
            return 0 if self.__all != name else 1
        if not self.has_energy(name): return 0
        return self.__energy[name]
    
    def copy(self):
        """
        Returns a copy of the energy pool
        """
        if self.is_all():
            return EnergyPool(self.__all)
        return EnergyPool(self.__energy.copy())
    
    def get_energy(self) -> dict[str, int]:
        if self.is_all():
            return {self.__all: 1}
        return self.__energy.copy()
    
    def add(self, energy: str, count:int=1):
        if self.is_all(): raise Exception("All-type pool can't add")

        if not energy in self.__energy:
            self.__energy[energy] = 0

        self.__energy[energy] += count

    def has_energy(self, energy:str, count:int) -> bool:
        """
        Returns wether or not the pool contains enough of the specified energy type
        """
        if self.is_all():
            return self.__all == energy

        if not energy in self.__energy:
            return False
        
        return self.__energy[energy] >= count
    
    def drop_random(self):
        """
        Removes a random energy from the pool
        """
        if self.is_all(): raise Exception('All-type pool can\'t drop random')

        total = self.total()
        if total  == 0: return

        index = randint(1, total)
        for energy, count in self.__energy.items():
            index -= count
            if index <= 0:
                self.__energy[energy] -= 1
                break

        self.clean_energy()

    def add_pool(self, gain):
        """
        Adds all energy from the gain set
        """
        if not isinstance(gain, EnergyPool): raise Exception("gain must be an EnergyPool")
        if self.is_all(): raise Exception('All-type pool can\'t add')
        if gain.is_all(): raise Exception('All-type pool can\'t be added')

        for energy, count in gain.get_energy().items():
            self.add(energy, count)

    def remove_pool(self, cost):
        """
        Removes all energy equal to cost
        """
        if self.is_all(): raise Exception("All-type pool can't remove")
        if not isinstance(cost, EnergyPool): raise Exception("cost must be an EnergyPool")
        if not cost.is_all() and not cost.compare(self): raise Exception("This set does not countain full cost")

        # Removing all of a single type
        if cost.is_all():
            energy = [key for key in cost.get_energy()][0]
            if energy in self.__energy:
                self.__energy.pop(energy)
            return

        normal = 0
        for energy, count in cost.get_energy().items():
            if energy == 'normal':
                normal = count
                continue

            self.__energy[energy] -= count

        for energy in self.__energy:
            if normal == 0:
                break

            if self.__energy[energy] < normal:
                normal -= self.__energy[energy]
                self.__energy[energy] = 0
                continue

            self.__energy[energy] -= normal
            normal = 0

        if normal != 0:
            raise Exception("Something went wrong when removing normal energy")
        
        self.clean_energy()

    def clean_energy(self):
        """
        Cleans up pool to remove 0 values
        """
        if self.is_all(): return

        zeroed = []
        for energy in self.__energy:
            if self.__energy[energy] <= 0:
                zeroed.append(energy)

        for energy in zeroed:
            self.__energy.pop(energy)
    
    def total(self) -> int:
        """
        Returns the total count of energy in the pool
        """
        if self.is_all(): return 1
        return sum([count for _, count in self.__energy.items()])

    def compare(self, target):
        """
        Checks if the target set a contains at least the contents of this set. Counts normals as wild values
        """
        if not isinstance(target, EnergyPool):
            raise Exception("Can only compare EnergyPools to each other")
        
        if self.is_all(): raise Exception('All-type pool can\'t be compared to target')
        if target.is_all(): raise Exception('All-type pool can\'t be compared')
        
        for energy, count in self.__energy.items():
            # skip normal
            if energy == 'normal':
                continue

            if not target.has_energy(energy, count):
                return False

        if self.total() > target.total():
            return False
        
        return True
    
    def __str__(self):
        if self.is_all():
            return f"All-{self.__all.title()}"

        if len(self.__energy) == 0:
            return "None"
        
        result = ""
        for energy in self.__energy:
            result += f"{self.__energy[energy]}-{energy.title()} "

        return result
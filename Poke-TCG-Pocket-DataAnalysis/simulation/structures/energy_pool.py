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
        self.__energy:dict[str, int] = data

    def as_set(self) -> EnergySet:
        return EnergySet(set([name for name, _ in self.__energy.items()]))

    def has_energy(self, name: str) -> bool:
        """
        Checks if the pool contains the given energy type
        """
        return name in self.__energy
    
    def count(self, name: str) -> int:
        """
        Returns the count of the given energy type
        """
        if not self.has_energy(name): return 0
        return self.__energy[name]
    
    def copy(self):
        """
        Returns a copy of the energy pool
        """
        return EnergyPool(self.__energy.copy())
    
    def get_energy(self) -> dict[str, int]:
        return self.__energy.copy()
    
    def add(self, energy: str, count:int=1):
        if not energy in self.__energy:
            self.__energy[energy] = 0

        self.__energy[energy] += count

    def has_energy(self, energy:str, count:int) -> bool:
        """
        Returns wether or not the pool contains enough of the specified energy type
        """
        if not energy in self.__energy:
            return False
        
        return self.__energy[energy] >= count
    
    def drop_random(self):
        """
        Removes a random energy from the pool
        """
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

        for energy, count in gain.get_energy().items():
            self.add(energy, count)

    def remove_pool(self, cost):
        """
        Removes all energy equal to cost
        """
        if not isinstance(cost, EnergyPool): raise Exception("cost must be an EnergyPool")
        if not cost.compare(self): raise Exception("This set does not countain full cost")

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
        return sum([count for _, count in self.__energy.items()])

    def compare(self, target):
        """
        Checks if the target set a contains at least the contents of this set. Counts normals as wild values
        """
        if not isinstance(target, EnergyPool):
            raise Exception("Can only compare EnergyPools to each other")
        
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
        if len(self.__energy) == 0:
            return "None"
        
        result = ""
        for energy in self.__energy:
            result += f"{self.__energy[energy]}-{energy.title()} "

        return result
from structures.energy_pool import EnergyPool, full_energy_name, is_short_energy_name, energy_names
from file_loader import is_nan
import structures.attack_trait as trait
from random import choice

class Attack:
    def __init__(self, data:dict[str, any]):
        self.name:str = data['name']
        self.cost:EnergyPool = EnergyPool(data['cost'])
        self.loss:EnergyPool = EnergyPool(data['loss'])
        self.damage:int = Attack.none_or_value(data['damage'])
        self.__traits:set[str] = data['traits']
        self.__bonus:dict[str, any] = data['bonus']

    @staticmethod
    def generate(pk_raw:dict[str, any], a_num:int):
        if a_num == 1:
            if is_nan(pk_raw['a1name']):
                return None
            cost, loss = Attack.move_cost_split(pk_raw['a1cost'])
            traits, bonus = Attack.move_bonus_breakdown(pk_raw['a1bonus'], pk_raw['a1bonusDmg'])
            return Attack({
                'name'      : pk_raw['a1name'],
                'cost'      : cost,
                'loss'      : loss,
                'damage'    : None if is_nan(pk_raw['a1damage']) else int(pk_raw['a1damage']),
                'traits'    : traits,
                'bonus'     : bonus
            })
        elif a_num == 2:
            if is_nan(pk_raw['a2name']):
                return None
            cost, loss = Attack.move_cost_split(pk_raw['a2cost'])
            traits, bonus = Attack.move_bonus_breakdown(pk_raw['a2bonus'], pk_raw['a2bonusDmg'])
            return Attack({
                'name'      : pk_raw['a2name'],
                'cost'      : cost,
                'loss'      : loss,
                'damage'    : None if is_nan(pk_raw['a2damage']) else int(pk_raw['a2damage']),
                'traits'    : traits,
                'bonus'     : bonus
            })
        else:
            return None

    def coin_damage(self, energy: EnergyPool) -> int:
        """
        Returns bonus damage from attack coin properties.\\
        Flip coins, and deal damage per head.

        Requires active_energy for energy-based coin flips (see Celebi EX)
        """
        # Zero damage if no coin bonus
        if not self.has_coin_bonus():
            return 0
        
        coin_count = self.__bonus['coin_count']
        bonus_damage = self.bonus_damage()

        # numeric coin count
        if isinstance(coin_count, int):
            heads = sum([choice[0, 1] for _ in range(coin_count)])
            return heads * bonus_damage
        
        # endless coin count (flip until tails)
        if coin_count == 'endless':
            heads = 0
            while True:
                if choice[0, 1] == 0: break
                heads += 1
            return heads * bonus_damage

        # unrecognized type
        if not coin_count in energy:
            return 0
        
        # energy-based coins
        count = energy.count(coin_count)
        heads = sum([choice[0, 1] for _ in range(count)])
        return heads * bonus_damage

    def energy_damage(self, energy: EnergyPool) -> int:
        """
        Returns bonus damage from attack energy bonus properties.\\
        Deal damage if extra energy is attached.
        """
        if not self.has_energy_bonus():
            return 0

        bonus_type: str = self.__bonus['energy_bonus']
        bonus_count: int = self.__bonus['energy_required']
        bonus_damage: int = self.bonus_damage()

        #check active has bonus type
        if not bonus_type in energy:
            return 0
        
        # if not enough energy with bonus, no bonus damage
        bonus_cost = self.cost.copy()
        bonus_cost.add(bonus_type, bonus_count)
        if not bonus_cost.compare(energy):
            return 0

        # give bonus
        return bonus_damage

    def has_trait(self, t: str) -> bool:
        return (t in self.__traits)
    
    def has_bonus(self, b: str) -> bool:
        return (b in self.__bonus)
    
    def get_bonus(self, b: str) -> any:
        return self.__bonus[b]
    
    def try_get_bonus(self, b: str) -> any:
        if not self.has_bonus(b): return None
        return self.get_bonus(b)
    
    def has_coin_bonus(self) -> bool:
        return 'coin_damage' in self.__bonus
    
    def has_energy_bonus(self) -> bool:
        return 'energy_bonus' in self.__bonus
    
    def bonus_damage(self) -> int:
        if not self.has_bonus['damage']: return 0
        return self.__bonus['damage']
    
    def print_short(self, indent=0):
        dmg = "None" if self.damage is None else f"{self.damage} dmg"
        print(f"{"":>{indent}}Attack: {self.name.title()} {dmg} | {str(self.cost)}")

    @staticmethod
    def none_or_value(item) -> (str | None):
        return None if is_nan(item) else item

    @staticmethod
    def move_cost_split(raw_cost: str):
        parts = raw_cost.split('-')
        cost = parts[0]
        cost_dict = {
            full_energy_name(key) : cost.count(key) 
            for key in set([c for c in cost])
        }
        
        if len(parts) < 2:
            return cost_dict, None

        loss = parts[1]
        if loss[0].startswith('['):
            return cost_dict, loss[1]

        loss_dict = {
            full_energy_name(key) : loss.count(key)
            for key in set([c for c in loss])
        }
        return cost_dict, loss_dict

    @staticmethod
    def move_bonus_breakdown(raw_bonus: str, raw_bonus_dmg) -> tuple[set[str], dict[str, any]]:
        # TODO refactor to make this better for simulation
        traits = set()

        if is_nan(raw_bonus):
            return traits, dict()
        
        bonus_value = None if is_nan(raw_bonus_dmg) else int(raw_bonus_dmg)

        splits = raw_bonus.split('-')
        b_type = splits[0]
        
        if b_type.startswith('\\'):
            traits.add(trait.Chance)
            b_type = b_type[1:]

        if b_type in [trait.AttackLock, trait.Invulnerable, trait.Draw, trait.Shuffle, trait.RandomEnergy, trait.ShowHand]:
            traits.add(b_type)
            return traits, dict()

        # healing
        if b_type == 'heal':
            return traits, {
                'heal'          : bonus_value,
                'heal_target'   : 'self'
            }
        
        if b_type == 'healAll':
            return traits, {
                'heal'          : bonus_value,
                'heal_target'   : 'all'
            }

        # status'
        if b_type in ['sleep', 'poison', 'no attack', 'no support', 'paralysis', 'no retreat', 'smokescreen', 'confused']:
            return traits, {'status': b_type}
        
        # recoil and defense
        if b_type == 'recoil':
            output = {'recoil': bonus_value}
            if len(splits) > 1: 
                output |= {'recoil_special': splits[1]}
            return traits, output
        
        if b_type == 'defend':
            return traits, {'defend': bonus_value}
        
        # coin-based
        if b_type == 'coin':
            return traits, {
                'coin_count'    : 
                    int(splits[1])
                        if isinstance(splits[1], (int, float)) 
                    else full_energy_name(splits[1]),
                'damage'   : bonus_value
            }
        
        if b_type == 'allCoins':
            return traits, {
                'coin_count'    : 'endless',
                'damage'        : bonus_value
            }
        
        # targeting
        if b_type == 'free':
            return traits, {'target': 'any'}

        if b_type == 'bTarget':
            return traits, {
                'target'        : 'bench', 
                'target_count'  : 'all' if splits[1] == 'all' else int(splits[1]), 
                'damage'        : bonus_value
            }

        if b_type == 'random':
            return traits, {
                'target'        : 'random',
                'target_count'  : int(splits[1]),
                'damage'        : bonus_value
            }
        
        # multipliers
        if b_type in energy_names:
            return traits, {
                'energy_bonus'      : b_type,
                'energy_required'   : int(splits[1]),
                'damage'            : bonus_value
            }

        if b_type == 'bench':
            if is_short_energy_name(splits[1]):
                return traits, {
                    'damage': bonus_value,
                    'bench_energy_count': full_energy_name(splits[1])
                }
            
            if splits[1] in ['all', 'opp']:
                return traits, {
                    'damage': bonus_value,
                    'bench_count': splits[1]
                }
            
            return traits, {
                'damage': bonus_value,
                'bench_pkmn_count': splits[1]
            }
        
        if b_type in ['hurt', 'poisoned', 'hasTool', 'energy', 'ex', 'damaged', 'ko']:
            return traits, {
                'special_damage'    : b_type,
                'damage'            : bonus_value
            }

        if b_type == 'used last':
            return traits, {
                'special_damage'    : 'usedLast',
                'damage'            : bonus_value
            }

        if b_type == 'discard':
            return traits, {
                'discard_count'     : bonus_value,
                'discard_target'    : 'self' if len(splits) > 1 else 'opp'
            }
        
        raise KeyError(f"unrecognized b_type `{b_type}`")
from structures.energy_pool import EnergyPool, full_energy_name, is_short_energy_name, energy_names
from file_loader import is_nan
import structures.attack_trait as trait
import structures.attack_bonus as bonus
import structures.attack_bonus_special as bonusSpecial
import structures.status as status
from random import choice

class Attack:
    def __init__(self, data:dict[str, any]):
        self.name:str = data['name']
        self.cost:EnergyPool = EnergyPool(data['cost'])
        self.loss:EnergyPool = EnergyPool(data['loss'])
        self.add: EnergyPool = EnergyPool(data['add'])
        self.damage:int = Attack.none_or_value(data['damage'])
        self.__traits:set[str] = data['traits']
        self.__bonus:dict[str, any] = data['bonus']

    @staticmethod
    def generate(pk_raw:dict[str, any], a_num:int):
        if a_num == 1:
            if is_nan(pk_raw['a1name']):
                return None
            cost, loss, add = Attack.move_cost_split(pk_raw['a1cost'])
            traits, bonus = Attack.move_bonus_breakdown(pk_raw['a1bonus'], pk_raw['a1bonusDmg'])
            return Attack({
                'name'      : pk_raw['a1name'],
                'cost'      : cost,
                'loss'      : loss,
                'add'       : add,
                'damage'    : None if is_nan(pk_raw['a1damage']) else int(pk_raw['a1damage']),
                'traits'    : traits,
                'bonus'     : bonus
            })
        elif a_num == 2:
            if is_nan(pk_raw['a2name']):
                return None
            cost, loss, add = Attack.move_cost_split(pk_raw['a2cost'])
            traits, bonus = Attack.move_bonus_breakdown(pk_raw['a2bonus'], pk_raw['a2bonusDmg'])
            return Attack({
                'name'      : pk_raw['a2name'],
                'cost'      : cost,
                'loss'      : loss,
                'add'       : add,
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
        coin_count = self.try_get_bonus(bonus.Coins)
        if coin_count is None:
            return 0
        
        bonus_damage = self.bonus_damage()
        
        # endless coin count (flip until tails)
        if self.has_trait(trait.EndlessCoins):
            heads = 0
            while True:
                if choice[0, 1] == 0: break
                heads += 1
            return heads * bonus_damage

        # numeric coin count
        if isinstance(coin_count, int):
            heads = sum([choice[0, 1] for _ in range(coin_count)])
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

        bonus_type: str = self.__bonus[bonus.EnergyBonusType]
        bonus_count: int = self.__bonus[bonus.EnergyBonusCount]
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
        """
        Trys to get the bonus by name, returns None if there is no bonus with the given name
        """
        if not self.has_bonus(b): return None
        return self.get_bonus(b)
    
    def has_coin_bonus(self) -> bool:
        return bonus.Coins in self.__bonus
    
    def has_energy_bonus(self) -> bool:
        return bonus.EnergyBonusType in self.__bonus
    
    def bonus_damage(self) -> int:
        if not self.has_bonus(bonus.Damage): return 0
        return self.__bonus[bonus.Damage]
    
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

        add_dict = dict()
        if '+' in cost:
            add = cost.split('+')[1]
            cost = cost.split('+')[0]
            add_dict = {
                full_energy_name(key) : add.count(key)
                for key in set([c for c in add])
            }

        cost_dict = {
            full_energy_name(key) : cost.count(key) 
            for key in set([c for c in cost])
        }
        
        if len(parts) < 2:
            return cost_dict, None, add_dict

        loss = parts[1]
        if loss[0].startswith('['):
            return cost_dict, loss[1], add_dict

        loss_dict = {
            full_energy_name(key) : loss.count(key)
            for key in set([c for c in loss])
        }

        return cost_dict, loss_dict, add_dict

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

        # TODO change AttackLock to a status instead of a trait
        trait_dict = {
            "attackLock" : trait.AttackLock, 
            "invulnerable" : trait.Invulnerable, 
            "draw" : trait.Draw, 
            "shuffle" : trait.ShufflePokemon, 
            "random energy" : trait.RandomEnergy, 
            "show hand" : trait.ShowHand, 
            "energy discard" : trait.EnergyDiscard
        }
        if b_type in trait_dict:
            traits.add(trait_dict[b_type])
            return traits, dict()

        # healing
        if b_type == 'heal':
            return traits, {bonus.Heal: bonus_value}
        
        if b_type == 'healAll':
            traits.add(trait.HealAll)
            return traits, {bonus.Heal: bonus_value}

        # status'
        status_dict = {
            'sleep': status.Sleep, 
            'poison': status.Poisoned, 
            'burn': status.Burned, 
            'no attack': status.NoAttack, 
            'no support': status.NoSupport, 
            'paralysis': status.Paralysis, 
            'no retreat': status.NoRetreat, 
            'smokescreen': status.Smokescreen, 
            'confused': status.Confused
        }
        if b_type in status_dict:
            return traits, {bonus.Status: status_dict[b_type]}
        
        # recoil and defense
        if b_type == 'recoil':
            output = {bonus.Recoil: bonus_value}
            if len(splits) > 1: 
                traits.add(trait.RecoilOnKo)
            return traits, output
        
        if b_type == 'defend':
            return traits, {bonus.Defend: bonus_value}
        
        # coin-based
        if b_type == 'coin':
            return traits, {
                bonus.Coins: 
                    int(splits[1])
                        if isinstance(splits[1], (int, float)) 
                    else full_energy_name(splits[1]),
                bonus.Damage: bonus_value
            }
        
        if b_type == 'allCoins':
            traits.add(trait.EndlessCoins)
            return traits, {
                bonus.Coins: 0,
                bonus.Damage: bonus_value
            }
        
        # targeting
        if b_type == 'free':
            traits.add(trait.FreeTarget)
            return traits, dict()

        if b_type == 'bTarget':
            return traits, {
                bonus.Target:       'bench', 
                bonus.TargetCount:  3 if splits[1] == 'all' else int(splits[1]), 
                bonus.Damage:       bonus_value
            }

        if b_type == 'random':
            return traits, {
                bonus.Target:       'random',
                bonus.TargetCount:  int(splits[1]),
                bonus.Damage:       bonus_value
            }
        
        # multipliers
        if b_type in energy_names:
            return traits, {
                bonus.EnergyBonusType:      b_type,
                bonus.EnergyBonusCount:   int(splits[1]),
                bonus.Damage:           bonus_value
            }

        if b_type == 'bench':
            if is_short_energy_name(splits[1]):
                traits.add(trait.BenchCountType)
                return traits, {
                    bonus.BenchCount: full_energy_name(splits[1]),
                    bonus.Damage: bonus_value
                }
            
            if splits[1] in ['all', 'opp']:
                return traits, {
                    bonus.BenchCount: splits[1],
                    bonus.Damage: bonus_value
                }
            
            traits.add(trait.BenchCountPokemon)
            return traits, {
                bonus.BenchCount: splits[1],
                bonus.Damage: bonus_value
            }
        
        bonus_special_dict = {
            'hurt': bonusSpecial.Hurt, 
            'poisoned': bonusSpecial.Poisoned, 
            'hasTool': bonusSpecial.HasTool, 
            'energy': bonusSpecial.OppEnergy, 
            'ex': bonusSpecial.OppIsEX, 
            'damaged': bonusSpecial.OppDamaged, 
            'ko': bonusSpecial.OppJustKoed,
            'usedLast': bonusSpecial.RepeatAttack
        }
        if b_type in bonus_special_dict:
            return traits, {
                bonus.Special: bonus_special_dict[b_type],
                bonus.Damage: bonus_value
            }

        if b_type == 'discard':
            if len(splits) > 1:
                traits.add(trait.SelfDiscard)
            return traits, {
                bonus.Discard: bonus_value,
            }
        
        raise KeyError(f"unrecognized b_type `{b_type}`")
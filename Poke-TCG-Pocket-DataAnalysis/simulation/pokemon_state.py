from file_loader import get_pokemon, is_nan
import random as r

uid_counter = 0

def coin_flip():
    """
    flips a coin and returns the result
    {0: tails, 1: heads}
    """
    return r.choice([0, 1])

energy_short_to_full = {
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

energy_names = [energy_short_to_full[name] for name in energy_short_to_full]

def pkmn_data(pkmn_id):
    """
    Returns a new pokemon card from the given id
    """
    global uid_counter
    uid_counter += 1

    pkmn = get_pokemon(pkmn_id)


    kept_fields = ['name', 'stage', 'from', 'id', 'hp', 'type', 'ability', 'weakness', 'retreat', 'rarity']
    pkmn_data = {key : None if is_nan(pkmn[key]) else pkmn[key] for key in kept_fields}
    pkmn_data |= {
        'max_hp'    : pkmn['hp'],
        'uid'       : uid_counter,
        'status'    : [],
        'move1'     : move_data(pkmn, 1),
        'move2'     : move_data(pkmn, 2),
        'energy'    : {}
    }

    return pkmn_data

def evolve_pkmn(pre_evo, pkmn):
    """
    Evolves/replaces the pre-evolution pokemon with the new pkmn evolution
    """
    # check evolution is valid
    if not pre_evo['name'] == pkmn['from']:
        note = f'Pre-evolution does not evolve into new pokemon {pre_evo['name']} --> {pkmn['name']}. Needs {pkmn['from']}'
        raise Exception(note)

    # new pokemon carries over health from pre-evolution
    health_delta = pkmn['max_hp'] - pre_evo['max_hp']
    pkmn['hp'] = pre_evo['hp'] + health_delta

    # keep uid
    pkmn['uid'] = pre_evo['uid']

    # clear status
    pkmn['status'] = []

    # keep energy
    pkmn['energy'] = pre_evo['energy']

    # since pass by reference, reassign pre_evo values
    # replace pre-evolution with new pokemon
    for key in pre_evo:
        pre_evo[key] = pkmn[key]

def move_data(pkmn, move_id):
    if move_id == 1:
        if is_nan(pkmn['a1name']):
            return None
        cost, loss = move_cost_split(pkmn['a1cost'])
        return {
            'name'      : pkmn['a1name'],
            'cost'      : cost,
            'loss'      : loss,
            'damage'    : None if is_nan(pkmn['a1damage']) else int(pkmn['a1damage']),
            'bonus'     : move_bonus_breakdown(pkmn['a1bonus'], pkmn['a1bonusDmg'])
        }
    elif move_id == 2:
        if is_nan(pkmn['a2name']):
            return None
        cost, loss = move_cost_split(pkmn['a2cost'])
        return {
            'name'      : pkmn['a2name'],
            'cost'      : cost,
            'loss'      : loss,
            'damage'    : None if is_nan(pkmn['a2damage']) else int(pkmn['a2damage']),
            'bonus'     : move_bonus_breakdown(pkmn['a2bonus'], pkmn['a2bonusDmg'])
        }
    else:
        return None

def move_cost_split(raw_cost: str):
    parts = raw_cost.split('-')
    cost = parts[0]
    cost_dict = {
        energy_short_to_full[key] : cost.count(key) 
        for key in set([c for c in cost])
    }
    
    if len(parts) < 2:
        return cost_dict, None

    loss = parts[1]
    if loss[0].startswith('['):
        return cost_dict, loss[1]

    loss_dict = {
        energy_short_to_full[key] : loss.count(key)
        for key in set([c for c in loss])
    }
    return cost_dict, loss_dict

def move_bonus_breakdown(raw_bonus: str, raw_bonus_dmg):
    # TODO refactor to make this better for simulation

    if is_nan(raw_bonus):
        return {}
    
    bonus_value = None if is_nan(raw_bonus_dmg) else int(raw_bonus_dmg)

    splits = raw_bonus.split('-')
    b_type = splits[0]

    output = {'other': []}

    if b_type.startswith('\\'):
        output['other'] += ['chance']
        b_type = b_type[1:]

    # healing
    if b_type == 'heal':
        output |= {
            'heal'          : bonus_value,
            'heal_target'   : 'self'
        }
        return output
    
    if b_type == 'healAll':
        output |= {
            'heal'          : bonus_value,
            'heal_target'   : 'all'
        }

    # status'
    if b_type in ['sleep', 'poison', 'no attack', 'no support', 'paralysis', 'no retreat', 'smokescreen', 'confused']:
        output |= {'status': b_type}
        return output
    
    # recoil and defense
    if b_type == 'recoil':
        output |= {'recoil': bonus_value}
        if len(splits) > 1: 
            output |= {'recoil_special': splits[1]}
        return output
    
    if b_type == 'defend':
        output |= {'defend': bonus_value}
        return output
    
    # coin-based
    if b_type == 'coin':
        output |= {
            'coin_count'    : 
                energy_short_to_full[splits[1]]
                    if splits[1] in energy_short_to_full 
                else int(splits[1]),
            'damage'   : bonus_value
        }
        return output
    
    if b_type == 'allCoins':
        output |= {
            'coin_count'    : 'endless',
            'damage'        : bonus_value
        }
        return output
    
    # targeting
    if b_type == 'free':
        output |= {'target': 'any'}
        return output
    

    if b_type == 'bTarget':
        output |= {
            'target'        : 'bench', 
            'target_count'  : 'all' if splits[1] == 'all' else int(splits[1]), 
            'damage'        : bonus_value
        }
        return output

    if b_type == 'random':
        output |= {
            'target'        : 'random',
            'target_count'  : int(splits[1]),
            'damage'        : bonus_value
        }
        return output
    
    # multipliers
    if b_type in energy_names:
        output |= {
            'energy_bonus'      : b_type,
            'energy_required'   : int(splits[1]),
            'damage'            : bonus_value
        }
        return output

    if b_type == 'bench':
        output |= {'damage': bonus_value}

        if splits[1] in energy_short_to_full:
            output |= {'bench_energy_count': energy_short_to_full[splits[1]]}
            return output
        
        if splits[1] in ['all', 'opp']:
            output |= {'bench_count': splits[1]}
            return output
        
        output |= {'bench_pkmn_count': splits[1]}
        
        return output
    
    if b_type in ['hurt', 'poisoned', 'hasTool', 'energy', 'ex', 'damaged', 'ko']:
        output |= {
            'special_damage'    : b_type,
            'damage'            : bonus_value
        }
        return output

    if b_type == 'used last':
        output |= {
            'special_damage'    : 'usedLast',
            'damage'            : bonus_value
        }
        return output

    if b_type == 'discard':
        output |= {
            'discard_count'     : bonus_value,
            'discard_target'    : 'self' if len(splits) > 1 else 'opp'
        }
        return output
    
    # other
    if b_type in ['invulnerable', 'draw', 'shuffle', 'random energy', 'show hand', 'attackLock']:
        output['other'] += [b_type]
        return output
    
    raise KeyError(f"unrecognized b_type `{b_type}`")

def damage_pokemon(defender, damage):
    defender['hp'] -= damage

    if defender['hp'] < 0:
        defender['hp'] = 0

def pkmn_feinted(pokemon):
    return pokemon['hp'] <= 0

def heal_pokemon(target, health):
    target['hp'] += health
    if target['hp'] > target['max_hp']:
        target['hp'] = target['max_hp']

def pkmn_handle_status_turn_start(pkmn):
    """
    Handles all of the pokemon status from the start of a turn
    
    STATUS - EFFECT
    - sleep - flip to cure
    - burn - 20 dmg, flip to cure
    - poison - 10 dmg
    - invulnerable - cure
    - defend - cure
    """

    if 'sleep' in pkmn['status']:
        if coin_flip() == 1:
            pkmn['status'].remove('sleep')
    
    if 'burn' in pkmn['status']:
        damage_pokemon(pkmn, 20)
        if coin_flip() == 1:
            pkmn['status'].remove('burn')

    if 'poison' in pkmn['status']:
        damage_pokemon(pkmn, 10)

    if 'invulnerable' in pkmn['status']:
        pkmn['status'].remove('invulnerable')
    
    if 'defend' in pkmn:
        pkmn.pop('defend')

def pkmn_attach_energy(pkmn, energy):
    if not energy in pkmn['energy']:
        pkmn['energy'][energy] = 0
    
    pkmn['energy'][energy] += 1

def attack_list(pkmn: dict) -> list[dict]:
    """
    Returns a list of attacks (attack data) from the given pokemon
    """
    return [atk for atk in [pkmn['move1'], pkmn['move2']] if not atk is None]

def enough_energy(attack: dict[str, any], curr_energy: dict[str, int]) -> bool:
    """
    Checks if the given energy if enough to use the given attack
    """
    for energy, count in attack['cost']:
        # skip normal
        if energy == 'normal':
            continue

        # must have energy type
        if not energy in curr_energy:
            return False
        
        # must have enough of the energy type
        if count > curr_energy[energy]:
            return False
    
    # re-check for normal energy fill
    total_required_energy = sum([count for _energy, count in attack['cost']])
    total_current_energy = sum([count for _energy, count in curr_energy])

    # at this point all specific energy types have been verified,
    #   so only normal energy is required to be counted via sum-
    #   comparison of total energy vs. current
    if total_required_energy > total_current_energy:
        return False
    
    return True

def attack_damage(atk: dict[str, any], player: dict, opponent: dict, attack_sequence: list[tuple]) -> int:
    """
    Returns total attack damage to defender
    """
    damage = atk['damage']
    bonus = atk['bonus']

    active = player['active']

    # coin bonus
    if 'coin_count' in bonus:
        damage += bonus_coin_damage(
            bonus['coin_count'], 
            bonus['damage'], 
            active['energy']
        )

    # energy bonus
    if 'energy_bonus' in bonus:
        damage += bonus_energy_damage(
            atk['cost'], 
            active['energy'], 
            bonus['energy_bonus'], 
            bonus['energy_required'], 
            bonus['damage']
        )
    
    # bench bonus
    if 'bench_energy_count' in bonus:
        damage += count_bench_type(player, bonus['bench_energy_type']) * bonus['damage']

    if 'bench_count' in bonus:
        target = player if bonus['bench_count'] == 'self' else opponent
        damage += count_bench(target) * bonus['damage']

    if 'bench_pkmn_count' in bonus:
        damage += count_bench_pkmn(player, bonus['bench_pkmn_count']) * bonus['damage']

    if 'sepcial_damage' in bonus:
        special = bonus['special_damage']
        # self hurt
        if special == 'hurt':
            if active['hp'] < active['max_hp']:
                damage += bonus['damage']

        # opp poisoned
        if special == 'poisoned':
            if 'poisoned' in opponent['active']['status']:
                damage += bonus['damage']
        
        # TODO self hasTool
        # if special == 'hasTool'

        # bonus per opp. active energy attached
        if special == 'energy':
            opp_energy = sum([count for _, count in opponent['active']['energy']])
            damage += opp_energy * bonus['damage']

        # bonus against EX
        if special == 'ex':
            if opponent['active']['name'][-2:].lower() == 'ex':
                damage += bonus['damage']

        # opp. active damaged
        if special == 'damaged':
            if opponent['active']['hp'] < opponent['active']['max_hp']:
                damage += bonus['damage']

        # if own pokemon was koed last opp. turn
        if special == 'ko':
            if attack_sequence[0][2] == True:
                damage += bonus['damage']

def bonus_coin_damage(
        coin_count: any, 
        bonus_damage: int, 
        active_energy: dict) -> int:
    """
    Returns bonus damage from attack coin properties.\\
    Flip coins, and deal damage per head.

    Requires active_energy for energy-based coin flips (see Celebi EX)
    """
    if isinstance(coin_count, int):
        heads = sum([r.choice[0, 1] for _ in range(coin_count)])
        return heads * bonus_damage
    
    if coin_count == 'endless':
        heads = 0
        while True:
            if r.choice[0, 1] == 0:
                break
            heads += 1
        return heads * bonus_damage

    # energy-based coins
    if not coin_count in active_energy:
        return 0
    
    count = active_energy[coin_count]
    heads = sum([r.choice[0, 1] for _ in range(count)])
    return heads * bonus_damage

def bonus_energy_damage(
        atk_energy_needed: dict[str, int], 
        active_energy: dict[str, int], 
        bonus_type: str, 
        bonus_count: int, 
        bonus_damage: int) -> int:
    """
    Returns bonus damage from attack energy bonus properties.\\
    Deal damage if extra energy is attached.
    """

    #check active has bonus type
    if not bonus_type in active_energy:
        return 0
    
    # check each specific type requirement is met
    for energy, count in atk_energy_needed:
        if energy == 'normal': continue
        
        if not energy in active_energy: return 0
        if active_energy[energy] < count: return 0

    # enough energy is attached to active for attack + bonus
    total_energy_needed = sum([count for _, count in atk_energy_needed])
    total_active_energy = sum([count for _, count in active_energy])
    if total_active_energy < total_energy_needed + bonus_count: return 0

    # check enough of bonus type is attached for attack + bonus
    if active_energy[bonus_type] < atk_energy_needed[bonus_type] + bonus_count: return 0

    # give bonus
    return bonus_damage

def count_bench_type(player: dict, type: str):
    """
    Returns the count of the number of benched pokemon of the given type
    """
    bench = [pkmn for pkmn in player['bench'] if not pkmn is None]
    return sum([1 if pkmn['type'] == type else 0 for pkmn in bench])

def count_bench(player: dict) -> int:
    """
    Returns the count of pokemon on the bench of the player
    """
    return sum([1 for pkmn in player['bench'] if not pkmn is None])

def count_bench_pkmn(player: dict, name: str) -> int:
    """
    Returns number of pokemon on the player's bench with the given name
    """
    bench = [pkmn for pkmn in player['bench'] if not pkmn is None]
    return sum([1 for pkmn in bench if pkmn[name] == name])
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
    pkmn_data = {key : pkmn[key] for key in kept_fields}
    pkmn_data |= {
        'max_hp'    : pkmn['hp'],
        'uid'       : uid_counter,
        'status'    : [],
        'move1'     : move_data(pkmn, 1),
        'move2'     : move_data(pkmn, 2),
        'energy'    : {}
    }

    if is_nan(pkmn_data['from']):
        pkmn_data['from'] = None

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
        return None
    
    bonus_value = None if is_nan(raw_bonus_dmg) else int(raw_bonus_dmg)

    splits = raw_bonus.split('-')
    b_type = splits[0]

    if b_type.startswith('\\'):
        output = {'chance' : True}
        b_type = b_type[1:]
    else:
        output = {}

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
            'coin_damage'   : bonus_value
        }
        return output
    
    if b_type == 'allCoins':
        output |= {
            'coin_count'    : 'endless',
            'coin_damage'   : bonus_value
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
            'multiplier_count'  : b_type,
            'energy_required'   : int(splits[1]),
            'mulitplier_damage' : bonus_value
        }
        return output

    if b_type == 'bench':
        output |= {
            'multiplier_count'  : 
                f'benched type {energy_short_to_full(splits[1])}' 
                    if splits[1] in energy_short_to_full 
                else f'benched {splits[1]}' 
                    if splits[1] in ['all', 'opp']
                else f'benched pokemon {splits[1]}',
            'multiplier_damage' : bonus_value
        }
        return output
    
    if b_type in ['hurt', 'poisoned', 'hasTool', 'energy', 'ex', 'damaged']:
        output |= {
            'multiplier_count'  : f'defender {b_type}',
            'multiplier_value'  : bonus_value
        }
        return output

    if b_type == 'used last':
        output |= {
            'multiplier_count'  : f'used move last turn',
            'multiplier_value'  : bonus_value
        }
        return output

    if b_type == 'discard':
        output |= {
            'discard_count'     : bonus_value,
            'discard_target'    : 'self' if len(splits) > 1 else 'opp'
        }
        return output
    
    # other
    if b_type in ['invulnerable', 'energy discard', 'draw', 'shuffle', 'random energy', 'show hand', 'ko']:
        output |= {'other': b_type}
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
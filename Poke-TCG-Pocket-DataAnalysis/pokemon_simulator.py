import pandas as pd
from pokemon_moves import *
import numpy as np

TCG_DATA_FILE_NAME = 'pokemon-tcg.csv'
pokemon = pd.read_csv(TCG_DATA_FILE_NAME)
uid_counter = 0

# def new_pokemon(p_id, health):
#     return {
#         'p_id'  : p_id,
#         'hp'    : health,
#         'status': [],
#     }

# def add_status(pokemon, status):
#     if status in pokemon['status']:
#         return
    
#     pokemon['status'] += [status]
    
#     if 'paralysis' in pokemon['status']:
#         if 'sleep' in pokemon['status']:
#             pokemon['status'].remove['sleep']

energy_short_to_full = {
    'g' : 'grass',
    'r' : 'fire',
    'w' : 'water',
    'e' : 'electric',
    'p' : 'psychic',
    'f' : 'fighting',
    'd' : 'dark',
    'm' : 'metal',
    'x' : 'normal'
}

energy_names = [energy_short_to_full[name] for name in energy_short_to_full]

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
    if raw_bonus is np.nan:
        return None
    
    bonus_value = None if np.isnan(raw_bonus_dmg) else int(raw_bonus_dmg)

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

def move_data(pkmn, move_id):
    if move_id == 1:
        if pkmn['a1name'] is None:
            return None
        cost, loss = move_cost_split(pkmn['a1cost'])
        return {
            'name'      : pkmn['a1name'],
            'cost'      : cost,
            'loss'      : loss,
            'damage'    : None if np.isnan(pkmn['a1damage']) else int(pkmn['a1damage']),
            'bonus'     : move_bonus_breakdown(pkmn['a1bonus'], pkmn['a1bonusDmg'])
        }
    elif move_id == 2:
        if pkmn['a2name'] is None:
            return None
        cost, loss = move_cost_split(pkmn['a2cost'])
        return {
            'name'      : pkmn['a2name'],
            'cost'      : cost,
            'loss'      : loss,
            'damage'    : None if np.isnan(pkmn['a2damage']) else int(pkmn['a2damage']),
            'bonus'     : move_bonus_breakdown(pkmn['a2bonus'], pkmn['a2bonusDmg'])
        }
    else:
        return None

def pkmn_data(pkmn_id):
    pkmn = pokemon[pokemon['id'] == pkmn_id]
    if pkmn.shape[1] == 0:
        return None
    pkmn = pkmn.iloc[0]

    uid_counter =+ 1

    kept_fields = ['name', 'id', 'hp', 'type', 'ability', 'weakness', 'retreat', 'rarity']
    pkmn_data = {key : pkmn[key] for key in kept_fields}
    pkmn_data |= {
        'uid'       : uid_counter,
        'status'    : [],
        'move1'     : move_data(pkmn, 1),
        'move2'     : move_data(pkmn, 2),
    }
    return pkmn_data

def print_dict(d, indent=4):
    for key in d:
        if (isinstance(d[key], dict)):
            print(f'{'':>{indent}}{key:<13}:')
            print_dict(d[key], indent+4)
            continue
        
        print(f'{'':>{indent}}{key:<13}: {d[key]}')


def main():

    # battle_state = {
    #     'turn'      : 1,
    #     'p1_active' : None,
    #     'p1_bench'  : [],
    #     'p2_active' : None,
    #     'p2_bench'  : [],
    # }
    print_dict(pkmn_data('ss49'))

if __name__ == '__main__':
    main()
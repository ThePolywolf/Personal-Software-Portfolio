def pdict(d:dict, indent:int=0):
    for key in d:
        if (isinstance(d[key], dict)):
            print(f'{'':>{indent}}{key:<13}: (dict | {len(d[key])})')
            pdict(d[key], indent+4)
            continue

        if (isinstance(d[key], list)):
            print(f'{'':>{indent}}{key:<13}: (list | {len(d[key])})')
            plist(d[key], indent+4)
            continue
        
        print(f'{'':>{indent}}{key:<13}: {d[key]}')

def plist(l:list, indent:int=0):
    index = 0
    for item in l:
        index += 1
        if (isinstance(item, dict)):
            print(f'{'':>{indent}}{index}. (dict | {len(item)})')
            pdict(item, indent+4)
            continue

        if (isinstance(item, list)):
            print(f'{'':>{indent}}{index}. (list | {len(item)})')
            plist(item, indent+4)
            continue
        
        print(f'{'':>{indent}}{index}. {item}')

def pkmn_move_short(move, indent=0):
    dmg = "None" if move['damage'] is None else f"{move['damage']} dmg"
    print(f"{"":>{indent}}Attack: {move['name'].title()} {dmg} | {energy_set(move['cost'])}")

def energy_set(energy: dict) -> str:
    if len(energy) == 0:
        return "None"
    
    result = ""
    for pke in energy:
        result += f"{energy[pke]}-{pke.title()} "

    return result

def status_set(status: list) -> str:
    if len(status) == 0:
        return "None"
    
    status = ""
    for s in status:
        status += f"{s.title()}, "

    return status[:-2]

def pokemon(pkmn: dict, indent:int=0):
    """
    Prints pokemon card data in a pretty format
    """
    name = pkmn['name'].title()
    uid = pkmn['uid']
    pk_type = pkmn['type'].title()
    stage = "Basic" if pkmn['stage'] == 0 else f"Stage {pkmn['stage']}"
    hp = pkmn['hp']
    max_hp = pkmn['max_hp']
    pk_from = "" if pkmn['from'] is None else f"<- {pkmn['from'].title()}"

    energy = energy_set(pkmn['energy'])

    status = status_set(pkmn['status'])

    retreat = "Free" if pkmn['retreat'] == 0 else f"{pkmn['retreat']} Energy"

    print(f"{"":>{indent}}{name} ({pkmn['id']}) #{uid} | {pk_type}, {stage} {pk_from} | {hp}/{max_hp}hp")
    print(f"{"":>{indent+2}}Energy: {energy}")
    if not pkmn['ability'] is None: print(f"{"":>{indent+2}}Ability: {pkmn['ability'].title()}")
    pkmn_move_short(pkmn['move1'], indent+2)
    if not pkmn['move2'] is None: pkmn_move_short(pkmn['move2'], indent+2)
    print(f"{"":>{indent+2}}Status: {status}")
    print(f"{"":>{indent+2}}Retreat: {retreat}, {pkmn['rarity']} Rarity")

def pokemon_short(pkmn: dict, prefix: str="", indent:int=0):
    """
    Prints pokemon card data in a single line pretty format
    """
    name = pkmn['name'].title()
    uid = pkmn['uid']
    pk_type = pkmn['type'].title()
    stage = "Basic" if pkmn['stage'] == 0 else f"Stage {pkmn['stage']}"
    hp = pkmn['hp']
    max_hp = pkmn['max_hp']

    print(f"{"":>{indent}}{prefix}{name} ({pkmn['id']}) #{uid} | {pk_type}, {stage} | {hp}/{max_hp}hp")

def player(player: dict, indent=0):
    
    if len(player['hand']) == 0:
        hand = "<Empty>"
    else:
        hand = ""
        for card in player['hand']:
            hand += f"{card['data']['name'].title()}, "
        hand = hand[:-2]

    energy_pool = ""
    for energy in player['energy_pool']:
        energy_pool += f"{energy.title()}, "
    energy_pool = energy_pool[:-2]

    pokemon_short(player['active'], prefix="Active: ", indent=indent)
    
    print(f"{"":>{indent}}Bench:")
    for pkmn in player['bench']:
        if pkmn is None: print(f"{"":>{indent+4}}<Empty>")
        else: pokemon_short(pkmn, indent=indent+4)

    print(f"{"":>{indent}}Energy: {player['next_energy'].title()} <- [{energy_pool}]")
    print(f"{"":>{indent}}Status: {status_set(player['status'])}")
    print(f"{"":>{indent}}Hand: {hand}")

def game_state(game, indent=0):
    print(f"{"":>{indent}}Game State")
    print(f"{"":>{indent+2}}Player 1")
    player(game['p1'], indent=indent+6)
    print(f"{"":>{indent+2}}Player 2")
    player(game['p2'], indent=indent+6)
    print(f"{"":>{indent+2}}Turn: {game['turn']}")
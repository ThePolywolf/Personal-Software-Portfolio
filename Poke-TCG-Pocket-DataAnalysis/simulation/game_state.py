from pokemon_state import pkmn_handle_status_turn_start, pkmn_attach_energy, pkmn_data, evolve_pkmn
import random as r

def new_game_state(p1_evo_line: list[str], p2_evo_line: list[str]) -> dict[str, any]:
    """
    Creates a new game state map from the given player starters
    """
    
    return {
        'p1': player_setup_from_evo_line(p1_evo_line),
        'p2': player_setup_from_evo_line(p2_evo_line),
        'turn' : 1
    }

def get_energy_pool(all_pkmn: list[dict]):
    """
    Takes given pkmn, and returns the pool of energy required for its moves.

    *NORMAL-only pools are turned into WATER energy pools.*
    """

    energy_pool = set()

    # add required energy for attacks
    for pkmn in all_pkmn:
        for attack in [pkmn['move1'], pkmn['move2']]:
            if attack is None:
                continue
            for energy_key in attack['cost']:
                energy_pool.add(energy_key)
    
    # remove normal type
    if 'normal' in energy_pool:
        energy_pool.remove('normal')
    
    # add water if no energy types present
    if len(energy_pool) == 0:
        energy_pool.add('water')
    
    return list(energy_pool)

def player_setup_from_evo_line(evo_line: list[str]):
    """
    Returns the player setup dictionary given their starter
    """
    # make sure evolution line starts with a basic pokemon
    starter = pkmn_data(evo_line[0])
    if starter['stage'] != 0: raise Exception(f"Starter is not a basic Pokemon")

    # add full evolution line set to hand
    hand = [pkmn_data(evo_id) for evo_id in evo_line]

    # get energy pool from evo-line
    energy_pool = get_energy_pool(hand)

    # add remainder of second set of evolution line
    if len(evo_line) > 1:
        hand += [pkmn_data(evo_id) for evo_id in evo_line[1:]]
    
    return {
        'active' : starter,
        'bench' : [None, None, None],
        'energy_pool': energy_pool,
        'next_energy' : r.choice(energy_pool),
        'status': [],
        'hand': [{"type": "pokemon", "data": card} for card in hand],
        # TODO deck
        # TODO add prize points
    }

def player_next_energy(player: dict):
    """
    Sets the player's next energy
    """
    player['next_energy'] = r.choice(player['energy_pool'])

def player_current_pkmn(player: dict):
    """
    returns a list of the names of all the player's current pokemon
    """
    pkmn = []
    pkmn += player['active']['name']

    for bench_pkmn in player['bench']:
        if bench_pkmn is None:
            continue

        pkmn += [bench_pkmn['name']]

def player_bench_count(player: dict) -> int:
    """
    Returns the number of pokemon on the bench
    """
    return sum([1 if item is not None else 0 for item in player['bench']])

def player_bench_full(player: dict) -> bool:
    """
    Returns true only if player bench is full.
    """
    return player_bench_count(player) == 3

def player_add_to_bench(player: dict, pokemon: dict):
    """
    Adds the given pokemon to the bench in the given player state
    """

    index = 0
    for item in player['bench']:
        if not item is None:
            index += 1
            continue

        player['bench'][index] = pokemon
        return
    
    raise Exception('Player bench is full')

def player_switch_active(player: dict):
    """
    Switches the player's active pokemon with the first pokemon in the bench, and re-benches the current active pokemon
    """

    # must have pokemon on bench to switch
    if player_bench_count(player) == 0:
        raise Exception('No bench Pokemon to switch')

    # get first pokemon on bench
    first_filled = 0
    for item in player['bench']:
        if not player['bench'][first_filled] is None:
            continue

        first_filled += 1

    # swap bench and active
    old_active = player['active']
    player['active'] = player['bench'][first_filled]
    player['bench'][first_filled] = old_active

def player_turn_start(player: dict):
    """
    Handles the start of a player's turn, returns current player energy for attachment
    """

    pkmn_handle_status_turn_start(player)
    current_energy = player['next_energy']
    player_next_energy(player)
    # draw card

    return current_energy

def player_turn_actions(player: dict, opponent: dict, current_energy: str, first_turn:bool=False):
    """
    Takes all valid player actions before an attack occurs
    """

    player_actions = [
        'attach_energy',
        'retreat',
        # 'play_card',
        # 'play_ability'
    ]
    
    if 'no retreat' in player['status']:
        player_actions.remove('retreat')

    # temp player map keys
    player['evolved_uids'] = []
    player['abilities_used'] = []

    # first turn, active pokemon can't evolve
    if first_turn:
        player['evolved_uids'] += [player['active']['uid']]

    while True:
        # attach energy once per turn
        if 'attach_energy' in player_actions:
            pkmn_attach_energy(player['active'], current_energy)
            player_actions.remove('attach_energy')
            continue

        # TODO implement retreat

        # use abilities

        # if any cards in hand, try to play them
        if player_try_play_cards(player):
            continue

        # print("Player Hand Empty")
        # print([card['data']['name'] for card in player['skipped_cards']])

        break

    # player temp cleanup
    player.pop('evolved_uids')
    player.pop('abilities_used')

def player_try_play_cards(player: dict) -> bool:
    """
    Finds a card from player's hand that can be used. Removes the card from the player's hand. 
    Returns wether or not a a card was played.
    """

    # loop through all cards in player's and to find one to play
    for card in player['hand']:
        # pokemon
        if card['type'] == 'pokemon':
            played = player_try_play_pokemon(player, card['data'])

            if played:
                player['hand'].remove(card)
                return True
            
            # continue to next card if not played
            continue

        # supporters
        # TODO handle 'no supporter' player status

        # items

        # tools

    return False

def player_try_play_pokemon(player: dict, pkmn: dict) -> bool:
    """
    Attempts to play the given pokemon card on the player state. 
    Returns wether or not a card was played.
    """

    if pkmn['stage'] == 0:
        # play a basic card if there is room on the bench
        if player_bench_full(player):
            return False
        
        player['evolved_uids'] += [pkmn['uid']]
        player_add_to_bench(player, pkmn)

        return True
    
    card_from = pkmn['from']
    
    # check if active or bench contains pre-evolution
    for target in [player['active']] + player['bench']:
        if target is None:
            continue
        
        target_is_pre_evo = target['name'] == card_from
        target_evolved_this_turn = target['uid'] in player['evolved_uids']

        if target_is_pre_evo and not target_evolved_this_turn:
            player['evolved_uids'] += [target['uid']]
            evolve_pkmn(target, pkmn)
            return True

    return False
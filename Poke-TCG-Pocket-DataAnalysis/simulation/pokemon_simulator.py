import pretty_print as pretty
from file_loader import get_evolution_line #, total_evolution_count
from pokemon_moves import *
from pokemon_state import *
from game_state import *

def automated_take_turn(player:dict, opponent:dict, attack_sequence: list[tuple], first_turn:bool=False):
    ## TURN START
    current_energy = player_turn_start(player)
    
    ## BATTLE ACTIONS
    player_turn_actions(player, opponent, current_energy, first_turn=first_turn)

    ## HANDLE ATTACK
    attack = player_attack(player, opponent, attack_sequence[1])
    attack_sequence = ([attack] + attack_sequence)[:2]

    ## TURN END
    # status
    #   sleep       - flip to cure
    #   paralysis   - cure
    #   burn        - 20 dmg, flip to cure
    #   poison      - 10 dmg
    #   smokescreen - cure
    #   no-attack   - cure
    #   no-support  - cure
    ...

def main():
    game = new_game_state(get_evolution_line(100), get_evolution_line(304))

    # pretty.game_state(game)

    automated_take_turn(game['p1'], game['p2'], game['attacks'], first_turn=True)
    automated_take_turn(game['p2'], game['p1'], game['attacks'], first_turn=True)

    automated_take_turn(game['p2'], game['p1'], game['attacks'])
    automated_take_turn(game['p1'], game['p2'], game['attacks'])
    
    # damage_pokemon(game['p1']['active'], 110)
    # heal_pokemon(game['p1']['active'], 60)

    pretty.game_state(game)

if __name__ == '__main__':
    # main()
    pretty.pokemon(pkmn_data('mi17'))
from .file_loader import get_evolution_line #, total_evolution_count
from .game_loader import *
from .structs.utils import game_control as game_control
from . import pokemon_loader as pk

def take_turns(game: Game) -> int:
    turn_count = 0

    while True:
        game.print()
        print(f"\nTurn {turn_count + 1}")
        game_control.automated_take_turn(game)
        winner = game_control.game_over(game)

        if not winner is None:
            return winner
        
        turn_count += 1
        if turn_count >= 100:
            print("Exceeded turn limit")
            return None

def simulate(evo_1: int, evo_2: int) -> (int | None):
    player_lines = [get_evolution_line(evo_1), get_evolution_line(evo_2)]

    for i in range(len(player_lines)):
        print(f"\n Player {i + 1} Pokemon")
        for pkmn_id in player_lines[i]:
            pkmn = pk.pkmn_from_data(pkmn_id)
            pkmn.print()

    print()

    game = new_game_state(player_lines[0], player_lines[1])

    winner = take_turns(game)
    if not winner is None:
        print(f"Winner: {pk.pkmn_from_data(player_lines[winner][-1]).name}")
    else:
        print("Tie")

    game.print()

    return winner
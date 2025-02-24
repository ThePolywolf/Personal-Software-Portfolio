from file_loader import get_evolution_line #, total_evolution_count
from game_state import *
import modules.game_control as game_control
import pokemon_state as pk

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

def main():
    # player_lines = [get_evolution_line(100), get_evolution_line(304)] # gyarados EX and Garchomp
    # player_lines = [get_evolution_line(159), get_evolution_line(26)] # gyarados EX and ditto
    # player_lines = [get_evolution_line(193), get_evolution_line(293)] # magmortar and luxray
    player_lines = [get_evolution_line(29), get_evolution_line(33)] # celebi EX and mew EX

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

if __name__ == '__main__':
    main()
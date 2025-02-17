from file_loader import get_evolution_line #, total_evolution_count
# from pokemon_moves import *
from game_state import *
import modules.game_control as game_control

def main():
    game = new_game_state(get_evolution_line(100), get_evolution_line(304))

    # game.print()

    game_control.automated_take_turn(game)
    game_control.automated_take_turn(game)

    game_control.automated_take_turn(game)
    game_control.automated_take_turn(game)

    game_control.automated_take_turn(game)
    game_control.automated_take_turn(game)

    # p1 active net -50 hp
    game.p1.active.damage(110)
    game.p1.active.heal(60)

    game.print()

if __name__ == '__main__':
    main()
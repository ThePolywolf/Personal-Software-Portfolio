from structures.game import Game
import modules.player_control as p_control

def automated_take_turn(game: Game):
    turn = game.turn % 2
    if turn == 0:
        player = game.p1
        opponent = game.p2
    else:
        player = game.p2
        opponent = game.p1

    ## TURN START
    p_control.start_turn(player)
    
    ## BATTLE ACTIONS
    p_control.turn_actions(player, opponent, first_turn=(game.turn <= 1))

    ## HANDLE ATTACK
    attack = p_control.attack(player, opponent, game.sequence)
    if not attack is None:
        game.sequence.add_attack(attack)

    ## TURN END
    # status
    #   sleep       - flip to cure
    #   paralysis   - cure
    #   burn        - 20 dmg, flip to cure
    #   poison      - 10 dmg
    #   smokescreen - cure
    #   no-attack   - cure
    #   no-support  - cure
    
    game.turn += 1
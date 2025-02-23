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
    game.sequence.add_attack(attack)
    
    if attack is None:
        print("No attack")
    else:
        print(attack)

    ## TURN END
    p_control.end_turn(player, opponent)
    
    game.turn += 1

def game_over(game: Game) -> (int | None):
    turn = game.turn % 2
    if turn == 0:
        player = game.p1
        opponent = game.p2
    else:
        player = game.p2
        opponent = game.p1

    if opponent.has_won() or player.has_lost():
        return turn
    
    if player.has_won() or opponent.has_lost():
        return (turn + 1) % 2
    
    return None
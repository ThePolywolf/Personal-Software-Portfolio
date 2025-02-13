import pretty_print as pretty
from file_loader import get_evolution_line, total_evolution_count
from pokemon_moves import *
from pokemon_state import *
from game_state import *

def automated_take_turn(player:dict, opponent:dict, first_turn:bool=False):
    ## TURN START
    current_energy = player_turn_start(player)
    
    ## BATTLE ACTIONS
    player_turn_actions(player, opponent, current_energy, first_turn=first_turn)

    ## HANDLE ATTACK
    # status
    #   no-attack:  can't attack
    #   confuesd:   flip for no attack
    #   attack lock:    can't attack if used last turn
    #   smokescreen:    flip for no attack
    # opponent status:
    #   invulnerable:   no damage dealt to opp. active
    #   defend: reduced damage
    # target
    #   random-count: attack random opp. pkmn -count times
    # damage (flat, coin, bonus)
    # bonus:
    #   ex - if opp is EX
    #   active - if opp. active is -type
    #   coin - +per head, flip coin count
    #       -count: # to flip
    #       -type:  flip per type energy attached
    #   coinsAll - +per head, flip until tails
    #   bTarget - deal bonus to 1 opp. bench
    #       -count: to count opp. bench
    #       -all:   all opp.bench
    #   bench:  bonus per count
    #       -type:  count type on bench
    #       -all:   all bench
    #       -opp:   opp. all bench
    #       -pkmn_name: count of name on self bench
    #   type-count: bonus damage if extra of type attached beyond required
    #   energy: energy attached to opp. active
    #   hasTool:    bonus if tool attached
    #   hurt:   bonus if self hurt
    #   ko: bonus if pkmn ko'd last turn
    #   ownDamage:  bonus equal to total damage taken
    #   poisoned:   bonus if opp. active poisoned
    #   usedLast:   bonus if attack used last
    # outcomes:
    #   apply status (self and opp)
    #   discard energy: discard random opp. energy
    #   discard:    discard opp cards
    #       -self:  own cards
    #   shuffle:    opp shuffles deck
    #   draw:   draw self
    #   heal:   heal self
    #   heal all:   heal all own pkmn
    #   random energy:  discard any random energy from any pkmn (self and opp.)
    #   recoil: damage self
    #       -ko: only on active ko

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

    automated_take_turn(game['p1'], game['p2'], first_turn=True)
    automated_take_turn(game['p2'], game['p1'], first_turn=True)

    automated_take_turn(game['p2'], game['p1'])
    automated_take_turn(game['p1'], game['p2'])
    
    # damage_pokemon(game['p1']['active'], 110)
    # heal_pokemon(game['p1']['active'], 60)

    pretty.game_state(game)



if __name__ == '__main__':
    main()
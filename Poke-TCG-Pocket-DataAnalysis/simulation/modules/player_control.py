from structures.attack_sequence import AttackSequence, AttackData
from structures.pokemon import Pokemon
from structures.player import Player
import structures.status as status
import structures.attack_trait as trait
import modules.attacker as attacker

def add_to_bench(player: Player, pokemon: Pokemon):
    """
    Adds the given pokemon to the bench.

    Exception: Bench is full
    """
    index = player.first_empty_bench_index()

    if index is None:
        raise Exception('Player bench is full')
    
    player.bench[index] = pokemon

def switch_active(player: Player):
    """
    Switches the active pokemon with the first pokemon in the bench.

    Exception: Bench is empty
    """

    # get first pokemon on bench
    index = player.first_filled_bench_index()

    if index is None:
        raise Exception('No bench Pokemon to switch; Bench is empty')

    # swap bench and active
    old_active = player.active
    player.active = player.bench[index]
    player.bench[index] = old_active

def try_play_pokemon(player: Player, pokemon: Pokemon) -> bool:
    """
    Attempts to play the given pokemon card.

    Returns wether or not the pokemon card was played.
    """

    if pokemon.is_basic():
        if player.bench_is_full():
            return False
        
        player.track_evolution(pokemon.uid)
        add_to_bench(player, pokemon)

        return True
    
    # check if active or bench contains pre-evolution
    for target in player.all_pokemon():
        target_is_pre_evo = target.name == pokemon.pre_evo
        target_already_evolved = player.already_evolved(target.uid)

        if target_is_pre_evo and not target_already_evolved:
            player.track_evolution(target.uid)
            target.evolve(pokemon)
            return True

    return False

def start_turn(player: Player):
    """
    Handles the start of a player's turn.
    """

    # active status'
    player.active.handle_status_turn_start()

    # TODO player status'

    # progress energy
    player.progress_energy()

    # draw card

def turn_actions(player: Player, opponent, first_turn:bool=False):
    """
    Uses every available pre-attack action
    """

    if not isinstance(opponent, Player):
        raise Exception("Opponent must by a Player type")

    actions = [
        'retreat',
    ]
    
    if status.NoRetreat in player.status:
        actions.remove(status.NoRetreat)

    # temp player map keys
    player.reset_evolutions()
    player.reset_abilities()

    # first turn, active pokemon can't evolve
    if first_turn:
        player.track_evolution(player.active.uid)

    while True:
        # attach energy once per turn
        if not player.current_energy is None:
            player.active.energy.add(player.current_energy)
            player.current_energy = None
            continue

        # TODO implement retreat

        # use abilities

        # if any cards in hand, try to play them
        if try_play_cards(player):
            continue

        # print("Player Hand Empty")
        # print([card['data']['name'] for card in player['skipped_cards']])

        break

    # player temp cleanup
    player.reset_evolutions()
    player.reset_abilities()

def try_play_cards(player: Player) -> bool:
    """
    Finds a card in hand that can be used. Removes the card from hand. \\
    Returns wether or not a a card was played.
    """

    # loop through all cards in player's and to find one to play
    for card in player.hand:
        # pokemon
        if card.is_pokemon():
            played = try_play_pokemon(player, card.get_pokemon())

            if played:
                player.hand.remove(card)
                return True
            
            # continue to next card if not played
            continue

        # supporters
        # TODO handle 'no supporter' player status

        # items

        # tools

    return False

def attack(player: Player, opponent, sequence: AttackSequence) -> (None | AttackData):
    """
    Handles an attack from the player active to the opponent
    """

    if not isinstance(opponent, Player):
        raise Exception("Opponent must by a Player type")

    # handle non-attack status
    for disqualifying_status in [status.NoAttack]:
        if disqualifying_status in player.active.status:
            return None

    # get best valid attack
    attacks = player.active.moves()

    attack = None
    for atk in attacks:
        if atk.has_trait(trait.AttackLock):
            if sequence.last_attack().attack_name == atk.name:
                continue
        
        if player.active.energy.compare(atk.cost):
            attack = atk

    if attack is None:
        return None

    # TODO handle special attacks (Damage is None)

    # target = 'self'
    # if 'target' in attack['bonus']:
    #     target = attack['target']

    #   confused:   flip for no attack
    #   smokescreen:    flip for no attack

    # opponent status:
    #   invulnerable:   no damage dealt to opp. active
    #   defend: reduced damage

    # damage (flat, coin, bonus)
    damage = attacker.damage(attack, player, opponent, sequence)

    # bonus:
    #   ex - if opp is EX
    #   active - if opp. active is -type
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

    kod = False
    return AttackData(attack.name, player.active.uid, kod)
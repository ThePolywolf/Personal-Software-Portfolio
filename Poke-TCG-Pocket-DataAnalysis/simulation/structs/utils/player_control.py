from ..attack_sequence import AttackSequence, AttackData
from ..pokemon import Pokemon
from ..player import Player
from ..attack import Attack
from ..data import (
    attack_trait as trait, 
    attack_bonus as bonus, 
    status as status
)
from . import attacker as attacker
from ...pokemon_moves import special_move

from random import randint, choice

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
    
    # None if koed or other
    if old_active is None:
        player.bench[index] = None
    else:
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

def turn_actions(player: Player, opponent: Player, first_turn:bool=False):
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

def attack(player: Player, opponent: Player, sequence: AttackSequence) -> (None | AttackData):
    """
    Handles an attack from the player active to the opponent
    """
    if not isinstance(opponent, Player):
        raise Exception("Opponent must by a Player type")

    # handle non-attack status
    # TODO switch NoAttack status as a removable status when benched
    for disqualifying_status in [status.NoAttack, status.Paralysis]:
        if disqualifying_status in player.active.status:
            return None

    # get best valid attack
    attacks = player.active.moves()

    attack = None
    for atk in attacks:
        if atk.has_trait(trait.AttackLock):
            if sequence.last_attack().attack_name == atk.name:
                continue
        
        if atk.cost.compare(player.active.energy):
            attack = atk
    
    return __use_attack(attack, player, opponent, sequence)

def __use_attack(attack: Attack, player: Player, opponent: Player, sequence: AttackSequence, ignore_cost:bool=False) -> (None | AttackData):
    """
    Handles using an attack from the player active to the opponent
    """
    if attack is None:
        return None
    
    print(f"{player.active.name} is using {attack.name}")

    # attack-prevention status' | Coin flip to attack at all
    if opponent.active.has_status([status.Confused, status.Smokescreen]) and choice([0, 1]) == 0:
        return None

    # damage (direct opponent damage)
    if attack.has_trait(trait.Special):
        special = special_move(player.active.id, player, opponent)
        is_attack = isinstance(special, Attack)
        if is_attack:
            ignore_cost = attack.name == 'genome hacking'
            return __use_attack(special, player, opponent, sequence, ignore_cost=ignore_cost)
        damage = special
    else:
        damage = attacker.damage(attack, player, opponent, sequence)
    
    if attack.has_trait(trait.FreeTarget):
        damage = attack_any(damage + attack.get_bonus(bonus.Damage), player, opponent)

    if attack.has_bonus(bonus.Target):
        damage += attack_bench(attack, player)

    damage = attacker.type_bonus(damage, player.active, opponent)

    # opponent status
    if opponent.active.has_status(status.Invulnerable):
        damage = 0
    else:
        damage = opponent.active.defend(damage)

    # apply damage to active
    attacker.attack(damage, player.active, opponent.active)

    # chance outcome
    do_outcome = True
    if attack.has_trait(trait.Chance):
        if choice([0, 1]) == 0:
            do_outcome = False
    
    if do_outcome:
        attacker.outcome(damage, attack, player, opponent)

    # loss and gain
    player.active.energy.add_pool(attack.add)
    if not ignore_cost: player.active.energy.remove_pool(attack.loss)

    if attack.has_trait(trait.SwitchToBench):
        switch_active(player)

    if attack.has_trait(trait.OppSwitchToBench):
        switch_active(opponent)

    # TODO handle KO removal in post-attack actions
    koed = False if opponent.active is None else opponent.active.is_koed()

    return AttackData(attack.name, player.active.uid, koed)

def attack_bench(attack: Attack, opponent: Player) -> int:
    """
    Attacks all bench targets, and returns bonus damage to the active pokemon
    """
    target = attack.try_get_bonus(bonus.Target)
    if target is None:
        return 0

    # vars
    target_count = attack.get_bonus(bonus.TargetCount)
    damage = attack.get_bonus(bonus.Damage)

    # apply target
    if target == 'random':
        return damage_random(target_count, damage, opponent)
    
    if target == 'bench':
        opp_bench = opponent.bench_pokemon()
        # TODO sort bench by hp (min to max)
        for i in range(len(opp_bench)):
            if i >= target_count: break
            opp_bench[i].damage(damage)

def damage_random(target_count: int, damage: int, opponent: Player) -> int:
    """
    Damages random random opponent targets, and returns the damage to the active pokemon
    """
    damages = [0] * len(opponent.all_pokemon())
    for _ in range(target_count):
        damages[randint(0, len(damage) - 1)] += damage

    active_damage = damages[0]

    opp_bench = opponent.bench_pokemon()
    for i in range(opp_bench):
        opp_bench[i].damage(damages[i + 1])

    return active_damage

def attack_any(damage: int, player: Player, opponent: Player):
    """
    Chooses a target to damage, then returns damage dealt to active
    """
    # only damage active if no bench pokemon
    if opponent.bench_count() == 0:
        return damage
    
    # FIRST | attack active if KO
    active_damage = attacker.type_bonus(damage, player.active, opponent)
    active_damage = opponent.active.defend(active_damage)

    if not opponent.active.has_status(status.Invulnerable):
        if attacker.will_ko(active_damage, player.active, opponent.active):
            return damage
    
    # SECOND | attack bench if KO
    for pkmn in opponent.bench_pokemon():
        if attacker.will_ko(damage, player.active, opponent.active):
            attacker.attack(damage, player.active, pkmn)
            return 0

    # THIRD | default attack active
    return damage

def end_turn(player: Player, opponent: Player):
    """
    End of turn processing for player and opponent
    """
    player.active.handle_status_turn_end()

    ko_points(player, opponent)
    ko_points(opponent, player)

def ko_points(player: Player, opponent: Player):
    """
    Gives points from koed player pokemon to the opponent, and removes koed pokemon
    """
    points = 0

    if player.active != None and player.active.is_koed():
        points += 2 if player.active.is_ex() else 1
        player.active = None
        if player.bench_count() > 0:
            switch_active(player)

    for pkmn in player.bench_pokemon():
        if pkmn.is_koed():
            points += 2 if pkmn.is_ex() else 1

    player.remove_ko_from_bench()

    if player.active == None:
        if player.bench_count() > 0:
            switch_active(player)

    opponent.give_points(points)
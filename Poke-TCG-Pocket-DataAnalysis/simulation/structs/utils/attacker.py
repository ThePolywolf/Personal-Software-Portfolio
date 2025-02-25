from ..card import Card
from ..attack import Attack
from ..player import Player
from ..pokemon import Pokemon
from ..ability import Ability
from ..attack_sequence import AttackSequence
from ..data import (
    attack_trait as trait, 
    attack_bonus as bonus, 
    attack_bonus_special as bonusSpecial, 
    status as status,
    ability_trigger as trigger,
)
from ... import pokemon_loader as pk
from ...abilities import get_ability

from random import randint

def damage(attack: Attack, user: Player, opponent: Player, sequence: AttackSequence) -> int:
    """
    Returns total attack damage to defender
    """ 
    damage = attack.damage

    active = user.active

    # coin bonus
    damage += attack.coin_damage(user.active.energy)

    # energy bonus
    active_energy = user.active.energy.copy()
    if user.has_status(status.JungleTotem):
        active_energy.add('grass', user.active.energy.count('grass'))
    damage += attack.energy_damage(active_energy)
    
    # bench type bonus
    if attack.has_trait(trait.BenchCountType):
        bench_energy = attack.get_bonus(bonus.BenchCount)
        damage += user.count_bench_type(bench_energy) * attack.bonus_damage()
    
    # bench pokemon bonus
    if attack.has_trait(trait.BenchCountPokemon):
        bench_pokemon = attack.get_bonus(bonus.BenchCount)
        damage += user.count_bench_pkmn(bench_pokemon) * attack.bonus_damage()
    
    # bench count bonus
    if attack.has_bonus(bonus.BenchCount):
        bench_count_target = attack.get_bonus(bonus.BenchCount)
        target = opponent if bench_count_target == 'opp' else user
        damage += target.bench_count() * attack.bonus_damage()

    # special cases
    special = attack.try_get_bonus(bonus.Special)
    if not special is None:
        # self hurt
        if special == bonusSpecial.Hurt:
            if active.hp < active.max_hp:
                damage += attack.bonus_damage()

        # opp poisoned
        if special == bonusSpecial.Poisoned:
            if opponent.active.has_status(status.Poisoned):
                damage += attack.bonus_damage()
        
        # TODO self hasTool
        # if special == 'hasTool'

        # bonus per opp. active energy attached
        if special == bonusSpecial.OppEnergy:
            damage += opponent.active.energy.total() * attack.bonus_damage()

        # bonus against EX
        if special == bonusSpecial.OppIsEX:
            if opponent.active.is_ex():
                damage += attack.bonus_damage()

        # opp. active damaged
        if special == bonusSpecial.OppDamaged:
            if opponent.active.hp < opponent.active.max_hp:
                damage += attack.bonus_damage()

        # if own pokemon was koed last opp. turn
        if special == bonusSpecial.OppJustKoed:
            opp_last_attack = sequence.opponent_last_attack()
            if not opp_last_attack is None and opp_last_attack.was_kod() == True:
                damage += attack.bonus_damage()

        # repeat attack bonus
        if special == bonusSpecial.RepeatAttack:
            last_attack = sequence.last_attack()
            if not last_attack is None and last_attack.attack_name() == attack.name and last_attack.same_user(user.active.uid):
                damage += attack.bonus_damage()

    #   active - if opp. active is -type
    if attack.has_bonus(bonus.ActiveType):
        if opponent.active.type == attack.get_bonus(bonus.ActiveType):
            damage += attack.bonus_damage()
    
    #   ownDamage
    if attack.has_trait(trait.OwnDamageBonus):
        damage += user.active.max_hp - user.active.hp

    #   fighting coach
    # TODO change from a status to deal +40 for 2 fighting coach
    if user.has_status(status.FightingCoach) and user.active.type == 'fighting':
        damage += 20

    return damage

def type_bonus(damage: int, active: Pokemon, opponent: Player):
    """
    Adds bonus damage if the active is the opponents weakness, and if dealing damage
    """
    if damage > 0 and active.type == opponent.active.weakness:
        return damage + 20
    return damage

def will_ko(damage: int, active: Pokemon, taker: Pokemon) -> bool:
    if taker.has_ability():
        ability = Ability(get_ability(taker.id))
        if ability.has_trigger(trigger.Defend):
            damage -= ability.func(trigger.Defend)(active, taker)
    
    if taker.hp <= damage:
        return True
    
    return False

def attack(damage: int, user: Pokemon, taker: Pokemon):
    """
    Damages the given pokemon based on the attacker and total damage
    """
    if damage <= 0: return

    if taker.has_ability():
        ability = Ability(get_ability(taker.id))
        if ability.has_trigger(trigger.Defend):
            damage -= ability.func(trigger.Defend)(user, taker)

    if damage <= 0: return

    taker.damage(damage)

def outcome(damage: int, attack: Attack, player: Player, opponent: Player):
    """
    Handles post-attack outcomes
    """
    if not opponent.active.has_status(status.Invulnerable):
        __opponent_outcome(attack, opponent)

    # self discard

    # draw

    # self status
    o_status = attack.try_get_bonus(bonus.Status)
    if not o_status == None:
        if o_status in status.pokemon_status:
            player.active.add_status(o_status)

    # healing
    heal = attack.try_get_bonus(bonus.Heal)
    if not heal is None:
        if attack.has_trait(trait.HealAll):
            for target in player.all_pokemon():
                target.heal(heal)
        elif attack.has_trait(trait.HealDamageDealt):
            player.active.heal(damage)
        else:
            player.active.heal(heal)
    
    # random energy discard
    if attack.has_trait(trait.RandomEnergy):
        pokemon = player.all_pokemon() 
        if opponent.active.has_status(status.Invulnerable):
            pokemon += opponent.bench_pokemon()
        else:
            pokemon += opponent.all_pokemon()
        __discard_random_energy(pokemon)
    
    # recoil
    recoil = attack.try_get_bonus(bonus.Recoil)
    if not recoil is None:
        if attack.has_trait(trait.RecoilOnKo):
            if opponent.active.is_koed():
                player.active.damage(recoil)
        else:
            player.active.damage(recoil)

    # attack lock
    if attack.has_trait(trait.AttackLock):
        player.active.add_status(status.AttackLockStart)

def __opponent_outcome(attack: Attack, opponent: Player):
    # status
    o_status = attack.try_get_bonus(bonus.Status)
    if not o_status is None:
        if o_status in status.pokemon_status:
            opponent.active.add_status(o_status)
        if o_status in status.player_status:
            opponent.add_status(o_status)

    # TODO discard
    
    # energy removal
    if attack.has_trait(trait.EnergyDiscard):
        opponent.active.energy.drop_random()
    
    # shuffle back to deck (hand for now)
    if attack.has_trait(trait.ShufflePokemon):
        card_ids = opponent.active.get_card_stack()
        opponent.active = None

        for id in card_ids:
            opponent.hand += [Card(pk.pkmn_from_data(id))]

def __discard_random_energy(pokemon: list[Pokemon]):
    """
    Removes a random energy from the game across all pokemon.

    All energy have an equal chance of getting selected.
    """
    # select pokemon first, then drop random energy from the chosen pokemon
    # a pokemon's selection weight is equal to the attached energy, so all energy have the same chance of being selected
    total_weight = sum([pkmn.energy.total() for pkmn in pokemon])
        
    if total_weight == 0:
        return
    
    index = randint(1, total_weight)
    for pkmn in pokemon:
        index -= pkmn.energy.total()
        
        if index > 0:
            continue

        pkmn.energy.drop_random()

        return

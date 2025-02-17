from structures.attack import Attack
from structures.player import Player
from structures.attack_sequence import AttackSequence
import structures.status as status

def damage(attack: Attack, user: Player, opponent: Player, sequence: AttackSequence) -> int:
    """
    Returns total attack damage to defender
    """
    damage = attack.damage

    active = user.active

    # coin bonus
    damage += attack.coin_damage(user.energy_set)

    # energy bonus
    damage += attack.energy_damage(user.energy_set)
    
    # bench bonus
    bench_energy = attack.try_get_bonus('bench_energy_count')
    if not bench_energy is None:
        damage += user.count_bench_type(bench_energy) * attack.bonus_damage()

    bench_count_target = attack.try_get_bonus('bench_count')
    if not bench_count_target is None:
        target = user if bench_count_target == 'self' else opponent
        damage += target.bench_count() * attack.bonus_damage()

    bench_pkmn = attack.try_get_bonus('bench_pkmn_count')
    if not bench_pkmn is None:
        damage += user.count_bench_pkmn(bench_pkmn) * attack.bonus_damage()

    # special cases
    special = attack.try_get_bonus('sepcial_damage')
    if not special is None:
        # self hurt
        if special == 'hurt':
            if active.hp < active.max_hp:
                damage += attack.bonus_damage()

        # opp poisoned
        if special == 'poisoned':
            if opponent.active.has_status(status.Poisoned):
                damage += attack.bonus_damage()
        
        # TODO self hasTool
        # if special == 'hasTool'

        # bonus per opp. active energy attached
        if special == 'energy':
            damage += opponent.energy_set.total() * attack.bonus_damage()

        # bonus against EX
        if special == 'ex':
            if opponent.active.is_ex():
                damage += attack.bonus_damage()

        # opp. active damaged
        if special == 'damaged':
            if opponent.active.hp < opponent.active.max_hp:
                damage += attack.bonus_damage()

        # if own pokemon was koed last opp. turn
        if special == 'ko':
            if sequence.opponent_last_attack().was_kod() == True:
                damage += attack.bonus_damage()
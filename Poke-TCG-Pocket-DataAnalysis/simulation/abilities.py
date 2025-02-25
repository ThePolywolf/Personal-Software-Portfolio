from .structs.player import Player
from .structs.pokemon import Pokemon
from .structs.data import (
    ability_trigger as trigger,
    status as status
)
from .structs.utils import player_control as p_control

from random import choice

def EMPTY(_c, _p, _o):
    ...

def on_heads(function, *args):
    """
    Runs the given function with the given args on a successful coinflip
    """
    if choice([0, 1]) == 1:
        return function(*args)

def _heal(caller: Pokemon, amount: int):
    caller.heal(amount)

def _heal_all(player: Player, amount: int):
    for pokemon in player.all_pokemon():
        pokemon.heal(amount)

def _damage_active(target: Player, damage: int):
    target.active.damage(damage)

def _counter_damage(opponent: Player, damage:int):
    opponent.active.damage(damage)

def _attack(target: Player, damage:int):
    # TODO check order (KO active) -> (KO bench) -> default active
    target.active.damage(damage)

def _give_status(target: (Pokemon | Player), status: str):
    target.add_status(status)

def _give_active_energy(target: Player, energy:str, count:int=1):
    target.active.energy.add(energy, count)

def _is_type(target: Pokemon, types: list[str]) -> bool:
    return target.type in types

def _remove_all_status(target: Player):
    target.active.clear_status()

def _on_energy(energy: str, comp: str, function, *args):
    if energy == comp:
        return function(*args)

def _wash_out(_c, player: Player, _o):
    water_gained = 0
    for pokemon in player.bench_pokemon():
        water_gained += pokemon.energy.remove_all('water')
    if water_gained > 0:
        player.active.energy.add('water', water_gained)

def _wash_out_check(_c, player: Player, _o) -> bool:
    if player.bench_count() == 0:
        return False
    return 0 < sum([pokemon.energy.count('water') for pokemon in player.bench_pokemon()])

def _shadow_void(caller: Pokemon, player: Player, _o):
    if player.active.hp < player.active.max_hp:
        damage = player.active.max_hp - player.active.hp
        player.active.heal(damage)
        caller.damage(damage)
        return
    
    for pokemon in player.bench_pokemon():
        if pokemon.ability == 'shadow void':
            continue

        if pokemon.hp >= pokemon.max_hp:
            continue

        damage = pokemon.max_hp - pokemon.hp
        pokemon.heal(damage)
        caller.damage(damage)
        return

def _shadow_void_check(caller: Pokemon, player: Player, _o) -> bool:
    if caller.uid == player.active.uid:
        return False
    
    for pokemon in player.bench_pokemon():
        if caller.uid == pokemon.uid: continue
        if pokemon.ability == 'shadow void': continue

        if pokemon.hp < pokemon.max_hp:
            return True

    return False

fragrant_flower_garden = { trigger.Action: lambda _c, player, _o: _heal_all(player, 10) }
powder_heal =       { trigger.Action: lambda _c, player, _o: _heal_all(player, 20) }
psy_shadow =        { trigger.Action: lambda _c, player, _o: _give_active_energy(player, 'psychic') }
fragrance_trap =    { trigger.Action: lambda _c, _p, opponent: p_control.switch_active(opponent) }
water_shuriken =    { trigger.Action: lambda _c, _p, opponent: _attack(opponent, 20) }
sleep_pendulum =    { trigger.Action: lambda _c, _p, opponent: on_heads(_give_status, opponent.active, status.Sleep) }
# TODO better drive-off (user's choice)
drive_off =         { trigger.Action: lambda _c, _p, opponent: p_control.switch_active(opponent) }
# TODO implement systems and replace EMPTY calls
data_scan =         { trigger.Action: EMPTY }
reckless_shearing = { trigger.Action: EMPTY }

counterattack =     { trigger.Attacked: lambda _c, _p, opponent: _counter_damage(opponent, 20) }
rough_skin =        { trigger.Attacked: lambda _c, _p, opponent: _counter_damage(opponent, 20) }
crystal_body =      { trigger.Attacked: lambda _c, player, _o: _remove_all_status(player) }

shadowy_spellbind = { trigger.OpponentTurn: lambda _c, _p, opponent: _give_status(opponent, status.NoSupport) }
primeval_law =      { trigger.OpponentTurn: lambda _c, _p, opponent: _give_status(opponent, status.NoActiveEvolution) }

jungle_totem =      { trigger.PlayerTurn: lambda _c, player, _o: _give_status(player, status.JungleTotem) }
fighting_coach =    { trigger.PlayerTurn: lambda _c, player, _o: _give_status(player, status.FightingCoach) }

nightmare_aura =    { trigger.EnergyGiven: lambda energy_type, _c, _p, opponent: _on_energy('dark', energy_type, _damage_active, opponent, 20) }

lunar_plumage =     { trigger.EnergyAttached: lambda energy_type, caller, _p, _o: _on_energy('psychic', energy_type, _heal, caller, 20) }

shell_armor =       { trigger.Defend: lambda _c, _o_a: 10 }
hard_coat =         { trigger.Defend: lambda _c, _o_a: 20 }
thick_fat_piloswine = { trigger.Defend: lambda _c, o_active: 20 if _is_type(o_active, ['fire', 'water']) else 0 }
thick_fat_mamoswine = { trigger.Defend: lambda _c, o_active: 20 if _is_type(o_active, ['fire', 'water']) else 0 }
exoskeleton =       { trigger.Defend: lambda _c, _o_a: 20 }
guarded_grill =     { trigger.Defend: lambda _c, _o_a: on_heads(lambda: 100) }

levitate =          { trigger.Retreat: lambda caller, _p, _o: 0 if caller.energy.total() >= 0 else None }

wash_out = {
    trigger.MultiAction: _wash_out,
    trigger.MultiCheck: _wash_out_check
}
shadow_void = {
    trigger.MultiAction: _shadow_void,
    trigger.MultiCheck: _shadow_void_check
}
fossil = {
    trigger.MultiAction: EMPTY,
    trigger.MultiCheck: lambda _c, _p, _o: False
}

id_abilities = {
    'ga7': powder_heal,
    'ga20': fragrance_trap,
    'ga61': counterattack,
    'ga67': shell_armor,
    'ga89': water_shuriken,
    'ga123': shadowy_spellbind,
    'ga125': sleep_pendulum,
    'ga132': psy_shadow,
    'ga182': hard_coat,
    'ga188': drive_off,
    'ga209': data_scan,
    'ga245': drive_off,
    'ga249': data_scan,
    'ga261': shadowy_spellbind,
    'ga277': shadowy_spellbind,
    'mi6': jungle_totem,
    'mi19': wash_out,
    'mi46': primeval_law,
    'mi56': rough_skin,
    'mi70': jungle_totem,
    'mi72': wash_out,
    'mi78': primeval_law,
    'mi84': primeval_law,
    'ss22': fragrant_flower_garden,
    'ss32': thick_fat_piloswine,
    'ss33': thick_fat_mamoswine,
    'ss34': crystal_body,
    'ss72': shadow_void,
    'ss78': levitate,
    'ss87': exoskeleton,
    'ss92': fighting_coach,
    'ss110': nightmare_aura,
    'ss114': guarded_grill,
    'ss123': reckless_shearing,
    'ss159': fragrant_flower_garden,
    'ss160': thick_fat_mamoswine,
    'ss167': levitate,
    'ss170': fighting_coach,
    'ss175': reckless_shearing,
    'ss187': nightmare_aura,
    'ss202': nightmare_aura,
    'pA13': powder_heal,
    'pA19': water_shuriken,
    'pA36': lunar_plumage,
    'ga216': fossil,
    'ga217': fossil,
    'ga218': fossil,
    'mi63': fossil,
    'ss144': fossil,
    'ss145': fossil,
}

# TODO magneton ability

def get_ability(id: str):
    return id_abilities[id]
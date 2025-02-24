from .structs.player import Player
from .structs.attack import Attack
from .structs.data import status as status

import random as r
import json

class find_a_friend:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # add random grass basic pkmn to bench
        return 0

class leaf_supply:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # 1 grass energy to benched grass pkmn
        pkmn = player.bench_pokemon()

        # TODO smart choice
        if len(pkmn) >= 0:
            r.choice(pkmn).energy.add('grass', 1)

        return 50

class inferno_dance:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # 3 coins, 1r -> benched r-pkmn per head
        pkmn = player.bench_pokemon()
        if len(pkmn) == 0:
            return 0
        
        # TODO smart choice
        fire_energy = sum([r.choice[0, 1] for _ in range(3)])
        for _ in range(fire_energy):
            r.choice(pkmn).energy.add('fire', 1)

        return 0

class ko_crab:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        ko_damage = r.randint(0, 1) * r.randint(0, 1) * 80
        return 80 + ko_damage

class thunder_punch:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # 40 + coin (-> +40, 20 recoil)
        damage = 40
        if r.choice([0, 1]) == 1:
            damage += 40
            player.active.damage(20)
        return damage

class nidoran_call_for_family:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # TODO nidoran m from deck to bench
        return 0

class copy_anything:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # copy opponent's move with enough energy
        move_out = None
        for move in opponent.active.moves():
            if move.cost.compare(player.active.energy):
                move_out = move

        if not move_out is None:
            return move_out

        return 0

class division:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # TODO koffing from deck to bench
        return 0

class mimic:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # TODO shuffle hand and draw deck for each card opp has
        return 0

class combee_call_for_family:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # TODO grass from deck to bench
        return 0

class oceanic_gift:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # 2 w-pkmn on bench each +w
        given = 0
        for pkmn in player.bench_pokemon():
            if given >= 2:
                break
            
            if pkmn.type == 'water':
                pkmn.energy.add('water', 1)
                given += 1

        return 0

class mind_boost:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # p to azelf or mespirit
        for pkmn in player.bench_pokemon():
            if pkmn.name in ['azelf', 'mespirit']:
                pkmn.energy.add('psychic', 1)
                break

        return 20

class supreme_blast:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # 130 if uxie and azelf on bench
        bench_names = [pkmn.name for pkmn in player.bench_pokemon()]
        needed_names = ['uxie', 'azelf']

        for name in needed_names:
            if not name in bench_names:
                return 0

        return 130

class cross_poison:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # poison if >=2 heads
        heads = sum([r.randint(0, 1) for _ in range(4)])

        if heads >= 2:
            opponent.active.add_status(status.Poisoned)

        return heads * 40

class croagunk_group_beatdown:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # 20*pkmn in play
        return 20 * (player.bench_count() + 1)

class toxicroak_group_beatdown:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # 40*pkmn in play
        return 40 * (player.bench_count() + 1)

class metallic_turbo:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # 2m to pkmn in bench

        bench_pkmn = player.bench_pokemon()
        if len(bench_pkmn) > 0:
            r.choice(bench_pkmn).energy.add('metal', 2)

        return 30

class buggy_beam:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        valid_energy = [
            'grass',
            'fire',
            'water',
            'electric',
            'psychic',
            'fighting',
            'dark',
            'metal',
        ]

        opponent.current_energy = r.choice(valid_energy)

        return 80

class pluck:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # TODO discard tools from opp first
        return 20

class super_fang:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # set to half opp remaining hp, rounded down
        return opponent.active.hp // 2

class interrupt:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        # TODO discard choice from opp hand
        return 60

class genome_hacking:
    @staticmethod
    def attack(player: Player, opponent: Player) -> int:
        move = None

        for t_move in opponent.active.moves():
            if t_move.name in ['genome hacking', 'copy anything']:
                continue

            move = t_move

        if not move is None:
            return move

        return 0

moves = {
    'ga5'     : find_a_friend,
    'ga30'    : leaf_supply,
    'ga47'    : inferno_dance,
    'ga69'    : ko_crab,
    'ga101'   : thunder_punch,
    'ga166'   : nidoran_call_for_family,
    'ga205'   : copy_anything,
    'ga247'   : copy_anything,
    'ga255'   : inferno_dance,
    'ga274'   : inferno_dance,
    'mi49'    : division,
    'mi62'    : mimic,
    'ss17'    : combee_call_for_family,
    'ss50'    : oceanic_gift,
    'ss75'    : mind_boost,
    'ss76'    : supreme_blast,
    'ss106'   : cross_poison,
    'ss107'   : croagunk_group_beatdown,
    'ss108'   : toxicroak_group_beatdown,
    'ss119'   : metallic_turbo,
    'ss129'   : buggy_beam,
    'ss132'   : pluck,
    'ss135'   : super_fang,
    'ss140'   : interrupt,
    'ss157'   : combee_call_for_family,
    'ss162'   : oceanic_gift,
    'ss166'   : supreme_blast,
    'ss173'   : croagunk_group_beatdown,
    'ss177'   : super_fang,
    'ss188'   : metallic_turbo,
    'ss205'   : metallic_turbo,
    'ss207'   : metallic_turbo,
    'pA25'    : inferno_dance,
    'mi32'    : genome_hacking,
    'mi77'    : genome_hacking,
    'mi83'    : genome_hacking,
    'mi86'    : genome_hacking,
}

def special_move(card_id: str, player: Player, opponent: Player) -> (int | Attack):
    """
    Returns the damage from a special move, or a new move to run instead
    """
    move_name = f"{card_id}"
    if not move_name in moves:
        return 0
    
    return moves[move_name].attack(player, opponent)

def main():
    file_name = 'pokemon-alt-moves.json'
    with open(file_name, 'w') as file:
        json.dump(list(moves.keys()), file, indent=4)
    print(f'alt move id-s dumped to file `{file_name}`')

if __name__ == '__main__':
    main()
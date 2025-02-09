import random as r
import json

class move:
    @staticmethod
    def attack(pkmn, move_data, game_state) -> int:
        return

# def STANDARD_coin_atk(coins: int, damage_per_coin: int) -> int:
#     damage_out = 0
#     for i in range(coins):
#         damage_out += r.randint(0, 1) * damage_per_coin
#     return damage_out

class find_a_friend:
    @staticmethod
    def attack() -> int:
        # add random grass basic pkmn to bench
        return 0

class leaf_supply:
    @staticmethod
    def attack() -> int:
        # 1 grass energy to benched grass pkmn
        return 50

class inferno_dance:
    @staticmethod
    def attack() -> int:
        # 3 coins, 1r -> benched r-pkmn per head
        return

class ko_crab:
    @staticmethod
    def attack() -> int:
        ko_damage = r.randint(0, 1) * r.randint(0, 1) * 80
        return 80 + ko_damage

class thunder_punch:
    @staticmethod
    def attack() -> int:
        # 40 + coin (-> +40, 20 recoil)
        return 

class teleport:
    @staticmethod
    def attack() -> int:
        # switch back to bench
        return 0

class leach_life:
    @staticmethod
    def attack() -> int:
        # heal for damage dealt
        return 50

class knock_back:
    @staticmethod
    def attack() -> int:
        # switch opp pkmn to bench, they choose 1 to bring in
        return 70

class nidoran_call_for_family:
    @staticmethod
    def attack() -> int:
        # nidoran m from deck to bench
        return 0

class copy_anything:
    @staticmethod
    def attack() -> int:
        # copy opponent's move with energy
        return 0

class leap_out:
    @staticmethod
    def attack() -> int:
        # same as teleport
        return 0

class division:
    @staticmethod
    def attack() -> int:
        # koffing from deck to bench
        return 0

class mimic:
    @staticmethod
    def attack() -> int:
        # shuffle hand and draw deck for each card opp has
        return 0

class combee_call_for_family:
    @staticmethod
    def attack() -> int:
        # grass from deck to bench
        return 0

class oceanic_gift:
    @staticmethod
    def attack() -> int:
        # 2 w-pkmn on bench each +w
        return 0

class mind_boost:
    @staticmethod
    def attack() -> int:
        # p to azelf or mespirit
        return 20

class supreme_blast:
    @staticmethod
    def attack() -> int:
        # 130 if uxie and azelf on bench
        return 0

class cross_poison:
    @staticmethod
    def attack() -> int:
        heads = sum([r.randint(0, 1) for _ in range(4)])
        # poison if >=2 heads
        return heads * 40

class croagunk_group_beatdown:
    @staticmethod
    def attack() -> int:
        # 20*pkmn in play
        return 20

class toxicroak_group_beatdown:
    @staticmethod
    def attack() -> int:
        # 40*pkmn in play
        return 40

class metallic_turbo:
    @staticmethod
    def attack() -> int:
        # 2m to pkmn in bench
        return 30

class buggy_beam:
    @staticmethod
    def attack() -> int:
        # change opp next energy to random
        return 80

class pluck:
    @staticmethod
    def attack() -> int:
        # discard tools from opp first
        return 20

class super_fang:
    @staticmethod
    def attack() -> int:
        # set to half opp remaining hp, rounded down
        return 0

class interrupt:
    @staticmethod
    def attack() -> int:
        # discard choice from opp hand
        return 60

class genome_hacking:
    @staticmethod
    def attack() -> int:
        # copy any opp move
        return 0

moves = {
    'ga5.1'     : find_a_friend,
    'ga30.1'    : leaf_supply,
    'ga47.1'    : inferno_dance,
    'ga69.1'    : ko_crab,
    'ga101.1'   : thunder_punch,
    'ga115.1'   : teleport,
    'ga159.1'   : leach_life,
    'ga163.1'   : knock_back,
    'ga166.1'   : nidoran_call_for_family,
    'ga205.1'   : copy_anything,
    'ga247.1'   : copy_anything,
    'ga255.1'   : inferno_dance,
    'ga274.1'   : inferno_dance,
    'mi17.1'    : leap_out,
    'mi49.1'    : division,
    'mi62.1'    : mimic,
    'ss17.1'    : combee_call_for_family,
    'ss50.1'    : oceanic_gift,
    'ss68.1'    : teleport,
    'ss75.1'    : mind_boost,
    'ss76.1'    : supreme_blast,
    'ss106.1'   : cross_poison,
    'ss107.1'   : croagunk_group_beatdown,
    'ss108.1'   : toxicroak_group_beatdown,
    'ss119.1'   : metallic_turbo,
    'ss129.1'   : buggy_beam,
    'ss132.1'   : pluck,
    'ss135.1'   : super_fang,
    'ss140.1'   : interrupt,
    'ss157.1'   : combee_call_for_family,
    'ss162.1'   : oceanic_gift,
    'ss166.1'   : supreme_blast,
    'ss173.1'   : croagunk_group_beatdown,
    'ss177.1'   : super_fang,
    'ss188.1'   : metallic_turbo,
    'ss205.1'   : metallic_turbo,
    'ss207.1'   : metallic_turbo,
    'pA25.1'    : inferno_dance,
    'mi32.2'    : genome_hacking,
    'mi77.2'    : genome_hacking,
    'mi83.2'    : genome_hacking,
    'mi86.2'    : genome_hacking,
}

def main():
    file_name = 'pokemon-alt-moves.json'
    with open(file_name, 'w') as file:
        json.dump(list(moves.keys()), file, indent=4)
    print(f'alt move id-s dumped to file `{file_name}`')

if __name__ == '__main__':
    main()
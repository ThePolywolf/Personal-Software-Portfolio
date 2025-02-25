Sleep = "sleep"
Poisoned = "poisoned"
Burned = "burned"
Smokescreen = "smokescreen"
Confused = "confused"
Paralysis = "paralysis"
NoAttack = 'no attack'
NoRetreat = 'no retreat'
Invulnerable = "invulnerable"
AttackLockStart = "attack lock start"
AttackLock = "attack lock"

pokemon_status = [Sleep, Poisoned, Burned, Smokescreen, Confused, Paralysis, NoAttack, NoRetreat, Invulnerable, AttackLock, AttackLockStart]

def is_pokemon_status(status: str):
    return status in pokemon_status

NoSupport = "no support"
JungleTotem = 'jungle totem'
NoActiveEvolution = 'no active evolution'
FightingCoach = 'fighting coach'

player_status = [NoSupport, JungleTotem, NoActiveEvolution, FightingCoach]

def is_player_status(status: str):
    return status in player_status
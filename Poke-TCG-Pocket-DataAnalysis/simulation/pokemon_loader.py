from .structs.pokemon import Pokemon
from .file_loader import get_pokemon
import random as r

uid_counter = 0

def coin_flip():
    """
    flips a coin and returns the result
    """
    return r.choice([0, 1])

def pkmn_from_data(pkmn_id):
    """
    Returns a new pokemon card from the given id
    """
    global uid_counter
    uid_counter += 1
    pkmn = get_pokemon(pkmn_id)
    return Pokemon(pkmn, uid_counter)
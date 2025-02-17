from structures.player import Player
from structures.game import Game
from structures.card import Card
import pokemon_state as pk
import random as r

def new_game_state(p1_evo_line: list[str], p2_evo_line: list[str]) -> Game:
    """
    Creates a new game state map from the given player starters
    """
    
    return Game(
        player_setup_from_evo_line(p1_evo_line),
        player_setup_from_evo_line(p2_evo_line)
    )

def player_setup_from_evo_line(evo_line: list[str]) -> Player:
    """
    Returns the player given an evolution line
    """
    # make sure evolution line starts with a basic pokemon
    starter = pk.pkmn_from_data(evo_line[0])
    if starter.stage != 0: raise Exception(f"Starter is not a basic Pokemon")

    # add full evolution line set to hand
    hand = [pk.pkmn_from_data(evo_id) for evo_id in evo_line]

    # add remainder of second set of evolution line
    if len(evo_line) > 1:
        hand += [pk.pkmn_from_data(evo_id) for evo_id in evo_line[1:]]

    # convert into cards
    hand = [Card(card) for card in hand]
    
    # generate player
    return Player.from_starter_and_hand(starter, hand)
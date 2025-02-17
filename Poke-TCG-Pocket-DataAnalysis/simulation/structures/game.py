from structures.player import Player
from structures.attack_sequence import AttackSequence

class Game:
    def __init__(self, p1: Player, p2: Player, turn:int=0):
        self.p1: Player = p1
        self.p2: Player = p2
        self.turn: int = turn
        self.sequence: AttackSequence = AttackSequence()

        # progress energy for second player
        self.p2.progress_energy()

    def print(self, indent=0):
        print(f"{"":>{indent}}Game State")
        print(f"{"":>{indent+2}}Player 1")
        self.p1.print(indent+6)
        print(f"{"":>{indent+2}}Player 2")
        self.p2.print(indent+6)
        print(f"{"":>{indent+2}}Turn: {self.turn}")

        # TODO add attack sequence printing
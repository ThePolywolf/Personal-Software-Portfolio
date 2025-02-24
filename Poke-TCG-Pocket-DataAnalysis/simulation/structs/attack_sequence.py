class AttackData:
    def __init__(self, name: str, uid: int, ko: bool):
        self.__attack = name
        self.__user = uid
        self.__ko = ko

    def same_user(self, uid:int) -> bool:
        """
        Checks if the given UId is the user of the attack before
        """
        return uid == self.__user
    
    def was_kod(self) -> bool:
        """
        Checks if the user KO'ed with this move
        """
        return self.__ko
    
    def attack_name(self) -> str:
        """
        Returns the name of the attack
        """
        return self.__attack
    
    def __str__(self):
        return f"Attack: {self.__attack} by {self.__user}; did{"" if self.__ko else " not"} ko"

class AttackSequence:
    def __init__(self):
        self.__sequence:list[AttackData] = [None, None]

    def add_attack(self, attack: AttackData):
        """
        Logs the attack in the sequence
        """
        self.__sequence = ([attack] + self.__sequence)[:2]

    def last_attack(self) -> AttackData:
        """
        Returns caller's last attack
        """
        return self.__sequence[1]
    
    def opponent_last_attack(self) -> AttackData:
        """
        Returns the caller's opponent's last attack
        """
        return self.__sequence[0]
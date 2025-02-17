from structures.pokemon import Pokemon

class Card:
    def __init__(self, card):
        if isinstance(card, Pokemon):
            self.__type = 'pokemon'
            self.__card = card

        # TODO item cards and other
        else:
            raise Exception('Given card is not a recognized card type')
    
    def is_pokemon(self) -> bool:
        return self.__type == 'pokemon'
    
    def get_pokemon(self) -> Pokemon:
        return self.__card
    
    def card_name(self) -> str:
        if isinstance(self.__card, Pokemon):
            return self.__card.name.title()
        
        else:
            return "Nameless"
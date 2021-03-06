"""
The card module. hook testing
Contains the class for a single Poker Card Object.
"""

VALUES = '34567890JQKA2Z'
SUITS = 'hdsc'
VALUE_DISPLAY = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2', 'joker', 'JOKER']
MIN_VALUE = 0
MAX_VALUE = 14
SMALL_JOKER_VALUE = 13
BIG_JOKER_VALUE = 14
SUIT_DISPLAY = ['♥', '♦', '♠', '♣']

class Card(object):
    """
    The Card Object
    """
    @staticmethod
    def str_to_card(card_str):
        """
        returns a cards with value of card_str
        """
        name = card_str[0].upper()
        if name == 'Z':
            suit = int(card_str[1])
        else:
            suit = card_str[1].lower()
        return Card(str(name), suit)

    @staticmethod
    def strs_to_cards(card_strs):
        """
        returns a list of cards with value of card_strs
        """
        return [Card.str_to_card(card_str) for card_str in card_strs]

    @staticmethod
    def card_to_str(card):
        """
        returns the string representation of the card
        """
        name = card.name
        suit = card.suit
        if name == 'Z':
            suit_str = '0' if card.value == SMALL_JOKER_VALUE else '1'
        else:
            suit_index = SUIT_DISPLAY.index(suit)
            suit_str = SUITS[suit_index]
        return name + suit_str

    @staticmethod
    def cards_to_strs(cards):
        return [Card.card_to_str(card) for card in cards]


    def __init__(self, name, suit):
        super(Card, self).__init__()
        self.display = 'INVALID'
        if not name in list(VALUES):
            return

        self.name = name
        self.value = -1
        self.suit = ''

        if suit in list(SUITS) and name != 'Z':
            self.value = VALUES.index(name)
            self.suit = SUIT_DISPLAY[SUITS.index(suit)]
            self.display = "{}{}".format(self.suit, VALUE_DISPLAY[self.value])
        elif name == "Z" and not str(suit).isalpha():
            self.value = VALUES.index(name) + suit
            self.display = "{}".format(VALUE_DISPLAY[self.value])
        else:
            name = "INVALID"

    def is_royal(self):
        """Returns true if card is greater than 10"""
        # return self.value > VALUES.index('0')
        # value of card 10 is 7
        return self.value > 7

    def __lt__(self, other):
        return other != None and self.value < other.value

    def __le__(self, other):
        return other != None and self.value <= other.value

    def __eq__(self, other):
        return other != None and str(self) == str(other)

    def __ge__(self, other):
        return other != None and self.value >= other.value

    def __gt__(self, other):
        return other != None and self.value > other.value

    def __repr__(self):
        """How the card is represented in terminal"""
        return 'Card: {}'.format(self.display) + ''

    def __str__(self):
        """How the card is turned into a string"""
        return self.display

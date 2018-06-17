"""
Hand module
Contains the Hand class and other constants
"""

from itertools import groupby
from pokai.src.game.card import Card, SMALL_JOKER_VALUE, BIG_JOKER_VALUE, MIN_VALUE, MAX_VALUE
from pokai.src.game.game_tools import SINGLES, DOUBLES, TRIPLES, QUADRUPLES, STRAIGHTS,\
                                      DOUBLE_STRAIGHTS, ADJ_TRIPLES, DOUBLE_JOKER
from pokai.src.game.card_play import Play

STRAIGHT_TERMINAL_VAL = 11
SMALLEST_STRAIGHT = [5, 3, 2]
CATEGORIES = [SINGLES, DOUBLES, TRIPLES, QUADRUPLES, STRAIGHTS, DOUBLE_STRAIGHTS,
              ADJ_TRIPLES, DOUBLE_JOKER]
WILDS = [DOUBLE_JOKER, QUADRUPLES]

class Hand(object):
    """
    Hand object
    Contains a list of cards, _cards.
    Contains a dictionary of categories that a hand can play
    """
    def __init__(self, cards):
        super(Hand, self).__init__()
        self._cards = cards
        self._categories = {}
        self._sort_cards()
        self._organize()

    def _sort_cards(self):
        """Sorts the cards in order by value"""
        self._cards.sort(key=lambda x: x.value, reverse=False)

    def _organize(self):
        """Organizes the cards in categories"""
        self._categories = {x:[] for x in CATEGORIES}
        counts = {value : list(c) for value, c in groupby(self._cards, lambda card: card.value)}
        self._organize_basics(counts)
        self._organize_straights(counts)
        self._organize_jokers(counts)

    def _organize_basics(self, counts):
        """helper function that organizes singles, doubles, triples, and quadruples"""
        for value in range(MIN_VALUE, MAX_VALUE + 1):
            if not value in counts:
                continue
            card_group = counts[value]
            self._categories[CATEGORIES[len(card_group) - 1]].append(card_group)

            self._organize_adj_triples(counts, value)

    def _organize_adj_triples(self, counts, value):
        """helper function that organizes adj triples that start
        at value"""
        if (value + 1) not in counts:
            return
        if len(counts[value]) == 3 and len(counts[value + 1]) == 3:
            pair = counts[value] + counts[value + 1]
            self._categories[ADJ_TRIPLES].append(pair)

    def _organize_straights(self, counts):
        """helper function that organizes straights"""
        for i in range(2):
            last_visited = -1
            for value in range(MIN_VALUE, MAX_VALUE + 1):
                if value <= last_visited:
                    continue
                if not value in counts:
                    continue
                
                straight_group = []
                # make sure value is Ace or less
                while value in counts and value <= STRAIGHT_TERMINAL_VAL and len(counts[value]) > i:
                    straight_group += counts[value][0: i + 1]
                    value += 1
                if len(straight_group) // (i + 1) >= SMALLEST_STRAIGHT[i]:
                    self._categories[CATEGORIES[4 + i]].append(straight_group)
                    last_visited = value - 1

    def _organize_jokers(self, counts):
        """helper function that organizes jokers"""
        if SMALL_JOKER_VALUE in counts and BIG_JOKER_VALUE in counts:
            self._categories[DOUBLE_JOKER].append([self._cards[-1], self._cards[-2]])

    def get_low(self, other_card, each_count, extra=0):
        """
        Gets the lowest basic that meets the properties
        Arguments:
        other_card -- lowest card in the basic
        each_count -- if its a single, double, triple, or quad (wild)
        extra -- the number of extra cards (1 or 2 for triple)
                                           (2 or 4 for quad)
        Returns the lowest play with pos -1 or None
        """
        if each_count < 3:
            extra = 0

        extra_cards = []
        if each_count == 3 and extra:
            extra_play = self.get_low(None, extra)
            if not extra_play:
                return
            else:
                extra_cards = extra_play.cards

        if each_count == 4 and extra:
            extra_play1 = self.get_low(None, extra // 2)
            extra_play2 = self.get_second_low(None, extra // 2)
            if not extra_play1 or not extra_play2:
                return
            else:
                extra_cards = extra_play1.cards + extra_play2.cards

        play_type = CATEGORIES[each_count - 1]
        if each_count <= 4:
            for card_group in self._categories[play_type]:
                card = card_group[0]
                if not other_card or card.value > other_card.value:
                    return Play(-1, card_group + extra_cards,
                                len(extra_cards), play_type=play_type)

        return None

    def get_second_low(self, other_card, each_count, extra=0):
        """
        Gets the second lowest basic that meets the properties
        Arguments:
        other_card -- lowest card in the basic
        each_count -- if its a single, double, triple, or quad (wild)
        extra -- the number of extra cards (1 or 2 for triple)
                                           (2 or 4 for quad)
        Returns the second lowest play with pos -1 or None
        """
        first_low = self.get_low(other_card, each_count, extra=extra)
        if not first_low:
            return None
        self.remove_cards(first_low.cards)
        second_low = self.get_low(other_card, each_count, extra=extra)
        self.add_cards(first_low.cards)
        if second_low:
            return Play(-1, second_low.cards, extra, play_type=CATEGORIES[each_count - 1])
        return None

    def get_low_straight(self, other_card, each_count, length):
        """
        Gets the lowest straight that meets the properties
        Arguments:
        other_card -- lowest card in the opposing straight
        each_count -- if its a single, double, or triple straight
        length -- length of the opposing straight
                  length is ignored when other_card is None

        Returns play with pos of -1 or None
        """
        play_type = CATEGORIES[4 + each_count - 1]

        if not other_card:
            if self._categories[play_type]:
                return Play(-1, self._categories[play_type][0], 0, play_type=play_type)
            return None
        for card_group in self._categories[play_type]:
            # although first card is less, might be able to just take the top portion of the straight
            if card_group[0].value <= other_card.value:
                for i, c in enumerate(card_group):
                    if c.value > other_card.value and len(card_group) - i >= length * each_count:
                        return Play(-1, card_group[i: i + length * each_count], 0, play_type=play_type)
            elif len(card_group) >= length * each_count:
                return Play(-1, card_group[0: length * each_count], 0, play_type=play_type)
        return None

    def get_low_adj_triple(self, other_card, extra_cards):
        """
        Gets the lowest adj triple that meets the properties
        Arguments:
        other_card -- the lowest card value of the triples
        extra_cards -- 2 if it carries 2 singles
                       4 if it carries 2 doubles
        Returns play with pos of -1 or None
        """
        extra_cards = extra_cards // 2
        foundation = self.get_low_straight(other_card, 3, 2)
        if not foundation:
            return
        if extra_cards:
            extra1 = self.get_low(None, extra_cards)
            extra2 = self.get_second_low(None, extra_cards)
            if not extra1 or not extra2:
                return None
            return Play(-1, foundation.cards + extra1.cards + extra2.cards, extra_cards, play_type=ADJ_TRIPLES)
        return Play(-1, foundation.cards, 0, play_type=ADJ_TRIPLES)

    def get_low_wild(self, other_card):
        """
        Returns the lowest wild play that is above given card
        Pos of the play is -1
        """
        lowest_four = self.get_low(other_card, 4)
        if lowest_four:
            return Play(-1, lowest_four.cards, 0, play_type=QUADRUPLES)
        if self._categories[DOUBLE_JOKER]:
            return Play(-1, self._categories[DOUBLE_JOKER][0], 0, play_type=DOUBLE_JOKER)
        return None

    def get_num_wild(self):
        """
        Returns the number of wild cards in hand
        """
        return len(self._categories[DOUBLE_JOKER]) + len(self._categories[QUADRUPLES])

    def add_cards(self, cards=None, card_strs=None):
        """adds a list of cards or list of string of cards to hand"""
        if not cards:
            cards = []
        if not card_strs:
            card_strs = []
        for c in cards:
            self._add(c)
        for card_str in card_strs:
            self._add(Card.str_to_card(card_str))
        self._sort_cards()
        self._organize()

    def _add(self, card):
        if card.value > -1 and not self.contains(card):
            self._cards.append(card)

    def remove_cards(self, cards):
        """removes a list of cards from hand"""
        for c in cards:
            self._remove(c)
        self._organize()

    def _remove(self, card):
        if self.contains(card):
            self._cards.remove(card)

    def contains(self, card):
        """returns true if the same card exists in hand"""
        for c in self._cards:
            if card.display == c.display:
                return True
        return False

    def get_card(self, index):
        """gets a single card at index"""
        return self._cards[index]

    def get_cards(self):
        """gets all cards in hand"""
        return self._cards

    def num_cards(self):
        """number of cards"""
        return len(self._cards)

    def print_categories(self):
        """prints out the sorted categories of the hand"""
        for i, j in self._categories.items():
            if not j:
                continue
            print("\n{}:".format(i))
            for k in j:
                print('|' + ' '.join('{}'.format(str(l)) for l in k) + '|')

    def __eq__(self, other):
        """equality function"""
        for c in self._cards:
            if c not in other.get_cards():
                return False
        return True

    def __str__(self):
        """How the card is turned into a string"""
        sep = " | "
        s = sep
        for card in self._cards:
            s += card.display + sep
        return s.strip()
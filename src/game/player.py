"""
Player module with Player class
"""

from pokai.src.game.hand import Hand
from pokai.src.game.game_tools import SINGLES, DOUBLES, TRIPLES, QUADRUPLES, STRAIGHTS,\
                                      DOUBLE_STRAIGHTS, ADJ_TRIPLES, DOUBLE_JOKER
class Player(object):
    """docstring for Player"""
    def __init__(self, hand, position, t):
        super(Player, self).__init__()
        self.hand = hand
        self.position = position
        self.type = t
        self.order = [ADJ_TRIPLES, DOUBLE_STRAIGHTS, STRAIGHTS, TRIPLES, DOUBLES, SINGLES, QUADRUPLES,
         DOUBLE_JOKER]

    def get_cards(self):
        return self.hand.get_cards()

    def reveal(self):
        print(self.hand)

    def info(self):
        self.hand.print_categories()

    def _get_lead_play(self, hand_counts, unrevealed_cards):
        """
        Gets the best play if this player is starting.
        Returns lead play
        """
        for play_type in self.order:
            next_play = None
            if play_type == SINGLES:
                next_play = self._get_lead_basic(1, hand_counts, unrevealed_cards)
            elif play_type == DOUBLES:
                next_play = self._get_lead_basic(2, hand_counts, unrevealed_cards)
            elif play_type == TRIPLES:
                next_play = self._get_lead_triple(hand_counts, unrevealed_cards)
            elif play_type == STRAIGHTS:
                next_play = self._get_lead_straight(1, hand_counts, unrevealed_cards)
            elif play_type == DOUBLE_STRAIGHTS:
                next_play = self._get_lead_straight(2, hand_counts, unrevealed_cards)
            elif play_type == ADJ_TRIPLES:
                next_play = self._get_lead_adj_triples(hand_counts, unrevealed_cards)
            else:
                next_play = self._get_lead_wild(hand_counts, unrevealed_cards)

            if next_play:
                return next_play
        return None

    def _get_lead_basic(self, each_count, hand_counts, unrevealed_cards):
        return self.hand.get_low(None, each_count)

    def _get_lead_triple(self, hand_counts, unrevealed_cards):
        for i in [2, 1, 0]:
            next_play = self.hand.get_low(None, 3, i)
            if next_play:
                return next_play
        return None

    def _get_lead_adj_triples(self, hand_counts, unrevealed_cards):
        for i in [2, 4, 0]:
            next_play = self.hand.get_low_adj_triple(None, i)
            if next_play:
                return next_play
        return None

    def _get_lead_straight(self, each_count, hand_counts, unrevealed_cards):
        return self.hand.get_low_straight(None, each_count, -1)

    def _get_lead_wild(self, hand_counts, unrevealed_cards):
        return self.hand.get_low_wild(None)

    def get_play(self, prev_play, hand_counts, unrevealed_cards):
        """
        Returns lowest play of play_type
        """
        is_leading = not prev_play or prev_play.position == self.position
        if is_leading:
            # lead play
            next_play = self._get_lead_play(hand_counts, unrevealed_cards)
        else:
            if prev_play.play_type == SINGLES:
                next_play = self.hand.get_low(prev_play.get_base_card(), 1)
            elif prev_play.play_type == DOUBLES:
                next_play = self.hand.get_low(prev_play.get_base_card(), 2)
            elif prev_play.play_type == TRIPLES:
                next_play = self.hand.get_low(prev_play.get_base_card(), 3,
                                              prev_play.num_extra)
            elif prev_play.play_type == STRAIGHTS:
                next_play = self.hand.get_low_straight(prev_play.get_base_card(),
                                                       1, prev_play.num_base_cards())
            elif prev_play.play_type == DOUBLE_STRAIGHTS:
                next_play = self.hand.get_low_straight(prev_play.get_base_card(),
                                                       2, int(prev_play.num_base_cards() / 2))
            elif prev_play.play_type == ADJ_TRIPLES:
                next_play = self.hand.get_low_adj_triple(prev_play.get_base_card(),
                                                         prev_play.num_extra)
            else:
                next_play = self.hand.get_low_wild(prev_play.get_base_card())

            # if next play is none and the player has less than 5 * (number of wilds in hand) cards,
            # play wilds
            if not next_play and hand_counts[prev_play.position] <= 5 * self.hand.get_num_wild():
                next_play = self.hand.get_low_wild(None)

        if next_play:
            next_play.position = self.position
        return next_play

    def play(self, card_play, display=False):
        self.hand.remove_cards(card_play.cards)
        if display:
            print("{}".format(card_play.play_type))
            for c in card_play.cards:
                print(c, end=" ")
            print()

    def amount(self):
        return self.hand.num_cards()

    def in_game(self):
        return self.amount() > 0

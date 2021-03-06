"""
Player module with Player class
"""

from pokai.game.hand import Hand
from pokai.game.game_tools import SINGLES, DOUBLES, TRIPLES, QUADRUPLES, STRAIGHTS,\
                                      DOUBLE_STRAIGHTS, ADJ_TRIPLES, DOUBLE_JOKER
from pokai.game.card_play import Play

class Player(object):
    """docstring for Player"""
    def __init__(self, hand, position, name):
        super(Player, self).__init__()
        self.hand = hand
        self.position = position
        self.name = name

    def get_cards(self):
        return self.hand.get_cards()

    def reveal(self):
        print(self.hand)

    def info(self):
        self.hand.print_categories()

    def get_possible_leads(self, game_state):
        possible_leads = []
        possible_leads.append(self._get_lead_adj_triples(game_state))
        possible_leads.append(self._get_lead_straight(2, game_state))
        possible_leads.append(self._get_lead_straight(1, game_state))
        possible_leads.append(self._get_lead_triple(game_state))
        possible_leads.append(self._get_lead_basic(2, game_state))
        possible_leads.append(self._get_lead_basic(1, game_state))
        possible_leads.append(self._get_lead_quadruple(game_state))
        possible_leads.append(self._get_lead_wild(game_state))
        possible_leads = list(filter(lambda play: play, possible_leads))
        return possible_leads

    def get_best_lead_play(self, game_state):
        """
        Gets the best play if this player is starting.
        Returns lead play
        """
        return self.get_possible_leads(game_state)[0]

    def _get_lead_basic(self, each_count, game_state):
        return self.hand.get_low(None, each_count)

    def _get_lead_triple(self, game_state):
        for i in [2, 1, 0]:
            next_play = self.hand.get_low(None, 3, i)
            if next_play:
                return next_play
        return None

    def _get_lead_adj_triples(self, game_state):
        for i in [2, 4, 0]:
            next_play = self.hand.get_low_adj_triple(None, i)
            if next_play:
                return next_play
        return None

    def _get_lead_straight(self, each_count, game_state):
        return self.hand.get_low_straight(None, each_count, -1)

    def _get_lead_quadruple(self, game_state):
        for i in [4, 2, 0]:
            next_play = self.hand.get_low(None, 4, i)
            if next_play:
                return next_play
        return None

    def _get_lead_wild(self, game_state):
        return self.hand.get_low_wild(None)

    def get_best_play(self, game_state):
        """
        Returns lowest play of play_type
        """
        prev_play = game_state.prev_play
        unrevealed_cards = []
        if not prev_play or prev_play.position == self.position:
            # lead play
            next_play = self.get_best_lead_play(game_state)
        else:
            prev_type = prev_play.play_type
            if prev_type == DOUBLE_JOKER:
                return Play.get_pass_play(position=self.position)
            elif prev_type == SINGLES:
                next_play = self.get_best_singles(game_state)
            elif prev_type == DOUBLES:
                next_play = self.get_best_doubles(game_state)
            elif prev_type == TRIPLES:
                next_play = self.get_best_triples(game_state)
            elif prev_type == STRAIGHTS:
                next_play = self.get_best_straights(game_state)
            elif prev_type == DOUBLE_STRAIGHTS:
                next_play = self.get_best_double_straights(game_state)
            elif prev_type == ADJ_TRIPLES:
                next_play = self.get_best_adj_triples(game_state)
            elif prev_type == QUADRUPLES:
                next_play = self.get_best_quad(game_state)
            # if next play is none and the player has less than 5 * (number of wilds in hand) cards,
            # play wilds
            # and game_state.get_player_num_cards(prev_play.position) <= 5 * self.hand.get_num_wild():

        if next_play:
            next_play.position = self.position
        return next_play

    def include_wild_play(get_best_specific_play):
        def wrapper(self, game_state):
            next_play = get_best_specific_play(self, game_state)
            if not next_play and not game_state.prev_play.is_wild():
                return self.hand.get_low_wild(None)
            return next_play
        return wrapper

    @include_wild_play
    def get_best_singles(self, game_state):
        return self.hand.get_low(game_state.get_prev_base_card(), 1)

    @include_wild_play
    def get_best_doubles(self, game_state):
        return self.hand.get_low(game_state.get_prev_base_card(), 2)

    @include_wild_play
    def get_best_triples(self, game_state):
        prev_play = game_state.prev_play
        return self.hand.get_low(prev_play.get_base_card(), 3, prev_play.num_extra)

    @include_wild_play
    def get_best_straights(self, game_state):
        prev_play = game_state.prev_play
        return self.hand.get_low_straight(prev_play.get_base_card(), 1, prev_play.num_base_cards())

    @include_wild_play
    def get_best_double_straights(self, game_state):
        prev_play = game_state.prev_play
        return self.hand.get_low_straight(prev_play.get_base_card(), 2, prev_play.num_base_cards() // 2)

    @include_wild_play
    def get_best_adj_triples(self, game_state):
        prev_play = game_state.prev_play
        return self.hand.get_low_adj_triple(prev_play.get_base_card(), prev_play.num_extra)

    @include_wild_play
    def get_best_quad(self, game_state):
        prev_play = game_state.prev_play
        return self.hand.get_low(prev_play.get_base_card(), 4, prev_play.num_extra)

    def get_best_wild(self, game_state):
        return self.hand.get_low_wild(game_state.get_prev_base_card())

    def play(self, card_play, display=False):
        self.hand.remove_cards(card_play.cards)
        if display:
            print(card_play)

    def amount(self):
        return self.hand.num_cards()

    def in_game(self):
        return self.amount() > 0

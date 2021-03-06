"""
Testing Module for AI Player
"""

from copy import deepcopy

from pokai.game.card import Card
from pokai.game.game_state import GameState
from pokai.game.card_play import Play
from pokai.game.hand import Hand
from pokai.ai.aiplayer import AIPlayer
from pokai.game.game_tools import SINGLES, DOUBLES, TRIPLES, QUADRUPLES, STRAIGHTS,\
                                 DOUBLE_STRAIGHTS, ADJ_TRIPLES, DOUBLE_JOKER

from tests.play_checker import _check_single, _check_double, _check_triple, _check_adj_triple,\
                                     _check_quadruples, _check_straight, _check_wild

class TestAIPlayer:
    @classmethod
    def setup_class(cls):
        cls.card_strs_lv2 = ['3h', '4s', '4h', '5d', '6s', '7c', '9h', '9d', '0c',
                             'Jh', 'Jc', 'Ks', 'Kd', 'Ac', 'Ah', '2c', '2d']
        cls.card_strs_lv3 = ['4h', '5d', '6c', '7s', '8s', '0s', '0c', '0d', '0h',
                             'QH', 'QD', 'QS', 'KH', 'KS', 'KC', 'KD', 'AC']
        
    def setup_method(self):       
        hand = Hand(Card.strs_to_cards(TestAIPlayer.card_strs_lv2))
        self.test_ai_player_lv2 = AIPlayer(hand, 0, "")

        hand = Hand(Card.strs_to_cards(TestAIPlayer.card_strs_lv3))
        self.test_ai_player_lv3 = AIPlayer(hand, 0, "")

        self.game_state = GameState(17, 17)
        self.game_state_is_setup = False

    def teardown_method(self):
        assert self.game_state_is_setup
        self.check_game_state_constant()

    @staticmethod
    def generate_ai_from_card_strs(card_strs):
        hand = Hand(Card.strs_to_cards(card_strs))
        return AIPlayer(hand, 0, "")

    @staticmethod
    def generate_player_from_card_strs(card_strs):
        hand = Hand(Card.strs_to_cards(card_strs))
        return Player(hand, 0, "")

    def setup_game_state(self, plays):
        for play in plays:
            self.game_state.cards_played(play)
        self.game_state.increment_turn()
        self.initial_game_state = deepcopy(self.game_state)
        self.game_state_is_setup = True

    def check_game_state_constant(self):
        assert self.initial_game_state == self.game_state



    def test_ai_get_best_singles(self):
        prev_play = Play(2, [Card('3', 'h')], 0, play_type=SINGLES)
        self.setup_game_state([prev_play])
        best_play = self.test_ai_player_lv3.get_best_singles(self.game_state)
        assert best_play[0].name == 'A'
        _check_single(best_play.cards)

    def test_ai_get_best_singles_none(self):
        self.setup_game_state([None])
        best_play = self.test_ai_player_lv2.get_best_singles(self.game_state)
        assert best_play[0].name == '0'
        _check_single(best_play.cards)

    def test_ai_get_best_doubles(self):
        prev_play = Play(2, [Card('8', 'c'), Card('8', 'd')], 0, play_type=DOUBLES)
        self.setup_game_state([prev_play])
        best_play = self.test_ai_player_lv2.get_best_doubles(self.game_state)
        assert best_play[0].name == '9'
        _check_double(best_play.cards)

    def test_ai_get_best_doubles_none(self):
        self.setup_game_state([None])
        best_play = self.test_ai_player_lv2.get_best_doubles(self.game_state)
        assert best_play[0].name == '9' or best_play[0].name == 'J'
        _check_double(best_play.cards)

    def test_ai_get_best_triples_alone(self):
        prev_play = Play(2, [Card('J', 'h'), Card('J', 'd'), Card('J', 'c')], 0, play_type=TRIPLES)
        self.setup_game_state([prev_play])
        best_play = self.test_ai_player_lv3.get_best_triples(self.game_state)
        assert best_play[0].name == 'Q'
        _check_triple(best_play.cards)

    def test_ai_get_best_triples_single(self):
        prev_play = Play(2, [Card('J', 'h'), Card('J', 'd'), Card('J', 'c'),
                             Card('4', 'c')], 1, play_type=TRIPLES)
        self.setup_game_state([prev_play])
        best_play = self.test_ai_player_lv3.get_best_triples(self.game_state)
        assert best_play[0].name == 'Q'
        assert best_play[3].name == 'A'
        _check_triple(best_play.cards)

    def test_ai_get_best_triples_double(self):
        card_strs = ['3c', '3d', '6h', '6s', '6d', '6c', '7h', '7d', '7c',
                      '8s', '9d', '0c', 'Qs', 'Kd', 'Ac', '2h', 'Z0']
        player = TestAIPlayer.generate_ai_from_card_strs(card_strs)
        
        prev_play = Play(2, [Card('5', 'h'), Card('5', 'd'), Card('5', 'c'),
                             Card('4', 'c'), Card('4', 's')], 2, play_type=TRIPLES)
        self.setup_game_state([prev_play])
        best_play = player.get_best_triples(self.game_state)
        assert best_play[0].name == '7'
        assert best_play[3].name == '3'
        _check_triple(best_play.cards)

    def test_ai_get_best_single_straight(self):
        card_strs = ['3c', '3d', '4s', '6h', '6d', '6c', '7h', '7d', '9c',
                      '0s', 'Jd', 'Qc', 'Qs', 'Kd', 'Ac', 'Ah', 'Z0']
        player = TestAIPlayer.generate_ai_from_card_strs(card_strs)
        
        prev_play = Play(2, [Card('3', 'h'), Card('4', 'd'), Card('5', 'c'),
                             Card('6', 's'), Card('7', 's')], 0, play_type=STRAIGHTS)
        self.setup_game_state([prev_play])
        best_play = player.get_best_straights(self.game_state)
        assert best_play[0].name == '9'
        _check_straight(best_play.cards, 1)

    def test_ai_get_best_double_straight(self):
        card_strs = ['6h', '6c', '6s', '7s', '7d', '7c', '8d', '8h',
                     '9H', '9D', '0H', '0S', 'Js', 'Qd', 'KD', 'KC', '2C']
        player = TestAIPlayer.generate_ai_from_card_strs(card_strs)
        prev_play = Play(2, [Card('3', 'h'), Card('3', 'd'), Card('4', 'c'),
                             Card('4', 's'), Card('5', 's'), Card('5', 'c')], 0, play_type=DOUBLE_STRAIGHTS)
        self.setup_game_state([prev_play])
        best_play = player.get_best_double_straights(self.game_state)
        assert best_play[0].name == '8'
        _check_straight(best_play.cards, 2)

    def test_ai_get_best_adj_triple_alone(self):
        # should not take 777888 because need two sevens for 556677
        card_strs = ['5c', '5d', '6h', '6s', '7h', '7d', '7c',
                      '8s', '8d', '8c', '9s', '9d', '9c', '0h']
        player = TestAIPlayer.generate_ai_from_card_strs(card_strs)
        prev_play1 = Play(0, [Card('2', 'd'), Card('2', 's'), Card('2', 'c')],
                          0, play_type=TRIPLES)
        prev_play2 = Play(2, [Card('3', 'h'), Card('3', 'd'), Card('3', 'c'),
                              Card('4', 'd'), Card('4', 's'), Card('4', 'c'),
                              Card('5', 'h'), Card('6', 'd')], 2, play_type=ADJ_TRIPLES)
        self.setup_game_state([prev_play1, prev_play2])
        
        best_play = player.get_best_adj_triples(self.game_state)
        assert best_play[0].name == '8'
        assert best_play[3].name == '9'
        assert best_play[6].name == '7'
        assert best_play[7].name == '0'
        _check_adj_triple(best_play.cards, 2)
    
    def test_ai_get_best_quad_double(self):
        # should take 77775566 (follow up with AAAA then 88)
        card_strs = ['5c', '5d', '6h', '6s', '7h', '7d', '7c',
                      '7s', '8d', '8c', 'As', 'Ad', 'Ac', 'Ah']
        player = TestAIPlayer.generate_ai_from_card_strs(card_strs)
        prev_play1 = Play(0, [Card('2', 'd'), Card('2', 's'), Card('2', 'c')],
                          0, play_type=TRIPLES)
        prev_play2 = Play(1, [Card('9', 'd'), Card('0', 'd'), Card('J', 's'),
                              Card('Q', 'c'), Card('K', 'c')], 0, play_type=STRAIGHTS)
        prev_play3 = Play(2, [Card('4', 's'), Card('4', 'c'), Card('4', 'd'),
                              Card('4', 'h'), Card('3', 'h'), Card('3', 's'),
                              Card('5', 'h'), Card('5', 's')], 4, play_type=QUADRUPLES)
        self.setup_game_state([prev_play1, prev_play2, prev_play3])
        best_play = player.get_best_quad(self.game_state)
        assert best_play[0].name == '7'
        _check_quadruples(best_play.cards)

    def test_ai_get_best_wild(self):
        card_strs = ['5c', '5d', '6h', '6s', '7h', '7d', '7c',
                      '7s', '8d', '8c', 'As', 'Ad', 'Ac', 'Ah', 'Z0', 'Z1']
        player = TestAIPlayer.generate_ai_from_card_strs(card_strs)
        prev_play1 = Play(0, [Card('2', 'd')],
                          0, play_type=SINGLES)
        prev_play2 = Play(2, [Card('4', 's'), Card('4', 'c'), Card('4', 'd'),
                              Card('4', 'h')], 0, play_type=QUADRUPLES)
        self.setup_game_state([prev_play1, prev_play2])

        best_play = player.get_best_wild(self.game_state)
        assert best_play.get_base_card().name == 'A'
        _check_quadruples(best_play.cards)

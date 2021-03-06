"""
Main command line interface for pokai.
Pass two file names that contain the cards of player 1 and player 2 to play a
game with the AI.

Example usage: python3 main.py player_1_file player_2_file
"""

import os
import argparse

from pokai.game.card import Card
from pokai.game.hand import Hand
from pokai.ai.aiplayer import AIPlayer
from pokai.game.game_tools import get_new_ordered_deck, remove_from_deck
from pokai.game.game_state import GameState
from pokai.game.card_play import Play

from pokai.interface.interface_tools import clear_lines, print_break

PROMPT_PLAYED_CARDS = "Enter played cards separated by spaces\n"

parser = argparse.ArgumentParser(description='Play a game with the AI.')
parser.add_argument("player_1_file", type=str,
                    help='filename for player 1 cards.')
parser.add_argument("player_2_file", type=str,
                    help='filename for player 2 cards.')
parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                    help="debugs AI performance")
parsed_args = parser.parse_args()
player_1_file = parsed_args.player_1_file
player_2_file = parsed_args.player_2_file
debug = parsed_args.debug

def get_cards_from_file(filename):
    """returns a list of cards from file"""
    card_strs = []
    with open(filename, "r") as f:
        for line in f.readlines():
            card_str = line.strip()
            card_strs.append(card_str)
    return Card.strs_to_cards(card_strs)

def get_num_cards_1():
    """returns number of cards in player 1's hand"""
    cards = get_cards_from_file(player_1_file)
    return len(cards)

def get_ai_hand():
    """constructs the hand for the computer based on player's cards"""
    deck = get_new_ordered_deck()
    taken = get_cards_from_file(player_1_file) +\
            get_cards_from_file(player_2_file)

    unused_deck = remove_from_deck(deck, taken)
    return Hand(unused_deck)

def init_game():
    hand = get_ai_hand()
    n_cards1 = get_num_cards_1()
    game_state = GameState(hand.num_cards(), n_cards1)
    ai = AIPlayer(hand, 0, "Computer")
    if debug:
        print("AI's hand:")
        ai.reveal()
        print("AI's hand strength:", ai.get_hand_strength(game_state))
    return game_state, ai

def get_play_from_input(user_input):
    """returns card play based on user's input"""
    if not user_input:
        return Play.get_pass_play()
    player_card_strs = user_input.split()
    played_cards = Card.strs_to_cards(player_card_strs)
    return Play.get_play_from_cards(played_cards)

def prompt_user_for_play(game_state):
    next_play = get_play_from_input(input(PROMPT_PLAYED_CARDS))
    while game_state.play_was_used(next_play):
        clear_lines(n=2)
        next_play = get_play_from_input(input(PROMPT_PLAYED_CARDS))
    clear_lines()
    return next_play

def on_turn_end(next_play, game_state):
    turn = game_state.get_current_turn()
    print(next_play)
    print('Player {} has {} cards left.'.format(turn, game_state.get_player_num_cards(turn)))
    game_state.cards_played(next_play)
    game_state.increment_turn()

def main():
    game_state, ai = init_game()

    while game_state.game_is_on():
        print_break()
        turn = game_state.get_current_turn()

        if not turn:
            print("Computer's turn.")
            next_play = ai.get_best_play(game_state)                
            ai.play(next_play)
        else:
            print("Player {}'s turn.".format(turn))
            next_play = prompt_user_for_play(game_state)
            next_play.position = turn

        on_turn_end(next_play, game_state)

    print("Player {} won!".format(game_state.get_winner()))
    ai.reveal()

if __name__ == '__main__':
    main()

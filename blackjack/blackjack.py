"""
Simulation of Blackjack.

This is a simplified version of blackjack with the following features:

- Cards are picked from a french deck of infinite size, that is the
  probability of picking a card is always the same at each iteration.
- At the first hand the player is given two cards and the dealer one
- At each step the player can choose whether to ``stay`` or ``hit``
- If the player chooses ``hit``, the dealer picks a card for the player
- The player can choose ``hit`` until the sum of cards is higher than 21,
  in that case the player loses
- When the player ``stay`` the dealer picks a card for itself and the value of
  player and dealer hands are counted
- Who has a hand closer to 21 wins the game, if both have 21 the game is a draw
"""
import itertools
import dataclasses
import random
from typing import List


@dataclasses.dataclass
class Card:
    rank: str
    suit: str

    def __repr__(self):
        return f"Card({self.rank}, {self.suit})"


class Deck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self.cards = [
            Card(rank, suit) for suit in self.suits for rank in self.ranks
        ]

    def pick(self, n=1) -> List[Card]:
        return random.choices(self.cards, k=n)


class GameOverException(Exception):
    pass


class GameWonException(Exception):
    pass


class GameDrawException(Exception):
    pass


class Hand:
    def __init__(self, cards: List[Card]):
        self.cards = cards

    def add(self, cards: List[Card]):
        self.cards.extend(cards)

    def __repr__(self):
        return "[" + ", ".join(str(card) for card in self.cards) + "]"

    @property
    def value(self) -> int:
        """
        Count the value of the hand.

        Figures like J, Q, and K count as ten. Digits count by their
        value and aces count like 1 or 11 depending on the best value.

        For example, in case of 2 aces the value is 12, in case of 2
        figures and 1 ace the value is 21.
        """
        aces = 0
        cumulative = 0
        for card in self.cards:
            if card.rank in list('JQK'):
                cumulative += 10
            elif card.rank.isdigit():
                cumulative += int(card.rank)
            else:
                aces += 1
        if aces:
            sums = []
            min_overflow = None
            for comb in itertools.combinations([1, 11] * aces, aces):
                distance = 21 - sum(comb) - cumulative
                if distance >= 0:
                    sums.append(distance)
                elif min_overflow is None or distance > min_overflow:
                    min_overflow = distance
            if sums:
                return 21 - min(sums)
            elif min_overflow:
                return 21 - min_overflow
            else:
                raise RuntimeError('Impossible to determine hand value.')
        return cumulative


class Blackjack:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand(self.deck.pick(2))
        self.dealer_hand = Hand(self.deck.pick())

    @property
    def state(self):
        return {
            'player': self.player_hand.value,
            'dealer': self.dealer_hand.value,
        }

    def finalize_game(self):
        """Run this function when no other player's action are possible."""
        while self.dealer_hand.value < 17:
            self.dealer_hand.add(self.deck.pick())
        player = self.player_hand.value
        dealer = self.dealer_hand.value
        if player > dealer or dealer > 21:
            raise GameWonException(
                f'Player won with {player} against {dealer}'
            )
        elif player == dealer:
            raise GameDrawException(
                f'Draw with {player}'
            )
        else:
            raise GameOverException(
                f'Player lost with {player} against {dealer}'
            )

    def player_pick(self):
        self.player_hand.add(self.deck.pick())
        if self.player_hand.value > 21:
            raise GameOverException('Player exceeded 21.')

    def step(self, action):
        if action == 'hit':
            self.player_pick()
        elif action == 'stay':
            self.finalize_game()


action_mapping = {
    0: 'stay',
    1: 'hit',
}


class SimulatorModel:
    def __init__(self):
        pass

    def reset(self):
        self.blackjack = Blackjack()
        return {
            'result': -1,
            **self.blackjack.state
        }

    def step(self, action):
        try:
            self.blackjack.step(action_mapping[action['command']])
            return {
                'result': -1,
                **self.blackjack.state
            }
        except GameOverException:
            return {
                'result': 0,
                **self.blackjack.state,
            }
        except GameDrawException:
            return {
                'result': 1,
                **self.blackjack.state,
            }
        except GameWonException:
            return {
                'result': 2,
                **self.blackjack.state,
            }

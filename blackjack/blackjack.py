"""Simulation of Blackjack."""
import itertools
import dataclasses
import random
from typing import List


@dataclasses.dataclass
class Card:
    rank: str
    suit: str


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


class WonGameException(Exception):
    pass


class DrawGameException(Exception):
    pass


class Hand:
    def __init__(self, cards: List[Card]):
        self.cards = cards

    def add(self, cards: List[Card]):
        self.cards.extend(cards)

    @property
    def value(self) -> int:
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

    def step(self, action):
        if self.player_hand.value == 21:
            raise WonGameException('Player won at opening.')
        if action == 'hit':
            self.player_hand.add(self.deck.pick())
            if self.player_hand.value > 21:
                raise GameOverException('Player exceeded 21.')
        elif action == 'stay':
            while self.dealer_hand.value < 17:
                self.dealer_hand.add(self.deck.pick())

            player = self.player_hand.value
            dealer = self.dealer_hand.value
            if player > dealer or dealer > 21:
                raise WonGameException(
                    f'Player won with {player} against {dealer}'
                )
            elif player == dealer:
                raise DrawGameException(
                    f'Draw with {player}'
                )
            else:
                raise GameOverException(
                    f'Player lost with {player} against {dealer}'
                )


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
            'halted': False,
            'won': False,
            'lost': False,
            'draw': False,
            **self.blackjack.state
        }

    def step(self, action):
        try:
            self.blackjack.step(action_mapping[action])
            return {
                'halted': False,
                'won': False,
                'lost': False,
                'draw': False,
                **self.blackjack.state
            }
        except GameOverException:
            return {
                'halted': False,
                'won': False,
                'lost': True,
                'draw': False,
                **self.blackjack.state,
            }
        except DrawGameException:
            return {
                'halted': False,
                'won': False,
                'lost': False,
                'draw': True,
                **self.blackjack.state,
            }
        except WonGameException:
            return {
                'halted': False,
                'won': True,
                'lost': False,
                'draw': False,
                **self.blackjack.state,
            }

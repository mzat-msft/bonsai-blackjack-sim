import dataclasses
import random
from typing import List


@dataclasses.dataclass
class Card:
    rank: str
    suit: str

    def __radd__(self, other) -> int:
        try:
            value = int(self.rank)
        except ValueError:
            if self.rank in list('JQK'):
                value = 10
            else:
                value = 11
        return other + value


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
        return sum(self.cards)  # type: ignore


class Blackjack:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand(self.deck.pick(2))

        if self.player_hand.value > 21:
            raise GameOverException('Player exceeded 21.')

        self.dealer_hand = Hand(self.deck.pick())

    @property
    def state(self):
        return {
            'player': self.player_hand.value,
            'dealer': self.dealer_hand.value,
        }

    def step(self, action):
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
    '0': 'stay',
    '1': 'hit',
}


class SimulatorModel:
    def __init__(self):
        pass

    def reset(self):
        self.blackjack = Blackjack()
        return {'halted': False, **self.blackjack.state}

    def step(self, action):
        try:
            self.blackjack(action_mapping[action])
        except GameOverException:
            return {
                'halted': False,
                'won': False,
                'lost': True,
                'draw': False,
                **self.blackjack.state(),
            }
        except DrawGameException:
            return {
                'halted': False,
                'won': False,
                'lost': False,
                'draw': True,
                **self.blackjack.state(),
            }
        except WonGameException:
            return {
                'halted': False,
                'won': True,
                'lost': False,
                'draw': False,
                **self.blackjack.state(),
            }

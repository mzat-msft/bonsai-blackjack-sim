"""
Simulation of Blackjack.

This is a simplified version of blackjack with the following features:

- Cards are picked from a french deck of size 52. The deck is refreshed at each
  episode.
- At the first hand the player is given two cards and the dealer one
- At each step the player chooses whether to ``stay``, ``hit``, ``double`` or
  ``surrender``.
- If the player chooses ``hit``, the dealer gives a card to the player
- The player can choose ``hit`` until the sum of cards is higher than 21,
  in that case the player loses (busts).
- If the player ``surrenders`` the game ends and the player loses only half of
  the bet.
- If the player chooses to ``double``, one card is added to its hand and the
  game continues as if he selects ``stay``. In case the player wins, the reward
  should be higher than for a normal win.
- When the player ``stays`` the dealer picks cards until reaching a 17, and the
  value of player and dealer hands are compared
- Who has a hand closer to 21 wins the game, if both have the same value the
  game is a draw

TODO: Forbid choosing ``double`` after first move.
TODO: Reuse same deck for multiple hands + make deck closer to casino game (2 decks...)
TODO: Split when first two cards are pair (need action masking)
"""
import dataclasses
import itertools
import json
import random
import reprlib
import time
import traceback
from pathlib import Path
from typing import Iterable, List

from bonsai_connector.connector import BonsaiEventType


@dataclasses.dataclass
class Card:
    rank: str
    suit: str

    def __repr__(self):
        return f"Card({self.rank!r}, {self.suit!r})"

    def __str__(self):
        return f"Card({self.rank}, {self.suit})"

    @property
    def rank_numeric(self):
        """Return the numeric value of the card."""
        if self.rank in list('JQK'):
            return 10
        elif self.rank.isdigit():
            return int(self.rank)
        elif self.rank == 'A':
            return 11
        else:
            raise ValueError(f'Rank {self.rank} unknown.')


class Deck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = '♠ ♥ ♦ ♣'.split()

    def __init__(self):
        self.cards = [
            Card(rank, suit) for suit in self.suits for rank in self.ranks
        ]
        random.shuffle(self.cards)

    def pick(self, n=1) -> List[Card]:
        return [self.cards.pop() for i in range(n)]


class GameLostException(Exception):
    pass


class GameWonException(Exception):
    pass


class GameDrawException(Exception):
    pass


class GameSurrenderException(Exception):
    pass


class Hand:
    def __init__(self, cards: Iterable[Card]):
        self.cards = list(cards)

    def add(self, cards: Iterable[Card]):
        self.cards.extend(cards)

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return f"Hand({reprlib.repr(self.cards)})"

    def __str__(self):
        return str(self.cards)

    def has_ace(self):
        return self.has_rank('A')

    def has_rank(self, rank):
        """Return True if ``rank`` is present in hand."""
        return any(card.rank == str(rank) for card in self.cards)

    def has_rank_between(self, min_rank, max_rank):
        """Return True if hand has at least one card with rank between min and max."""
        return any(min_rank <= card.rank_numeric <= max_rank for card in self.cards)

    def is_ranks(self, *ranks):
        """Return True if hand is composed exactly by ``ranks``."""
        return all(self.has_rank(rank) for rank in ranks) and len(ranks) == len(self)

    @property
    def value(self) -> int:
        """
        Return the value of the hand.

        Figures like J, Q, and K count as ten. Digits count by their
        value and aces count like 1 or 11 depending on the best value.

        For example, in case of 2 aces the value is 12, in case of 2
        figures and 1 ace the value is 21.
        """
        aces = 0
        cumulative = 0
        for card in self.cards:
            if card.rank_numeric == 11:
                aces += 1
            else:
                cumulative += card.rank_numeric
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
    double: bool = False
    surrender: bool = False

    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand(self.deck.pick(2))
        self.dealer_hand = Hand(self.deck.pick())
        self.first_step = True

    def get_mask(self):
        if self.first_step:
            return [1, 1, 1]
        return [1, 1, 0]

    @property
    def state(self):
        return {
            'player': self.player_hand.value,
            'dealer': self.dealer_hand.value,
            'double': self.double,
            'player_ace': int(self.player_hand.has_ace()),
            'dealer_ace': int(self.dealer_hand.has_ace()),
            'player_hand': str(self.player_hand),
            'dealer_hand': str(self.dealer_hand),
            'surrender': self.surrender,
            'mask': self.get_mask()
        }

    def win(self):
        raise GameWonException(
            f'Player won with {self.player_hand.value}',
            f' against {self.dealer_hand.value}',
        )

    def lose(self):
        raise GameLostException(
            f'Player lost with {self.player_hand.value}',
            f' against {self.dealer_hand.value}',
        )

    def finalize_game(self):
        """Run this function when no other player action is possible."""
        if self.surrender:
            raise GameSurrenderException('Player surrendered')

        while self.dealer_hand.value < 17:
            self.dealer_hand.add(self.deck.pick())
        player = self.player_hand.value
        dealer = self.dealer_hand.value
        if player > dealer or dealer > 21:
            self.win()
        elif player == dealer:
            raise GameDrawException(
                f'Draw with {player}'
            )
        else:
            self.lose()

    def player_pick(self):
        self.player_hand.add(self.deck.pick())
        if self.player_hand.value > 21:
            self.lose()

    def step(self, action):
        if action == 'hit':
            self.player_pick()
        elif action == 'double':
            if not self.first_step:
                raise RuntimeError('Can only double-down at first step')
            self.double = True
            self.player_pick()
            self.finalize_game()
        elif action == 'stay':
            self.finalize_game()
        elif action == 'surrender':
            self.surrender = True
            self.finalize_game()
        self.first_step = False


action_mapping = {
    0: 'stay',
    1: 'hit',
    2: 'double',
    3: 'surrender',
}


class SimulatorModel:
    def __init__(self):
        with open(Path(__file__).parent / 'blackjack-interface.json', 'r') as fp:
            self.interface = json.load(fp)

    def reset(self, config):
        self.blackjack = Blackjack()
        return {
            'result': -1,
            **self.blackjack.state
        }

    def dispatch_event(self, next_event):
        if next_event.event_type == BonsaiEventType.EPISODE_START:
            return self.reset(next_event.event_content)
        elif next_event.event_type == BonsaiEventType.EPISODE_STEP:
            return self.step(next_event.event_content)
        elif next_event.event_type == BonsaiEventType.EPISODE_FINISH:
            return {'reason': next_event.event_content}
        elif next_event.event_type == BonsaiEventType.IDLE:
            return
        else:
            raise RuntimeError(
                f"Unexpected BonsaiEventType. Got {next_event.event_type}"
            )

    def step(self, action):
        try:
            self.blackjack.step(action_mapping[action['command']])
            return {
                'result': -1,
                **self.blackjack.state
            }
        except GameLostException:
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
        except GameSurrenderException:
            return {
                'result': 0,
                **self.blackjack.state,
            }
        except Exception:
            print('Exception raised.')
            traceback.print_exc()
            return {
                'result': -2,
                'halted': True,
                **self.blackjack.state,
            }

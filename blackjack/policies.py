"""Policies that can be evaluated in blackjack."""
import collections
import random
from abc import ABC, abstractmethod
from collections.abc import Sequence

from blackjack.blackjack import Hand, SimulatorModel

AVAILABLE_POLICIES = ['basic', 'random', 'random_conservative', 'player']


class Policy(ABC):
    """Abstract Base Class representing a policy."""

    @abstractmethod
    def step(self, state):
        """Choose an action from ``state``."""


class RandomPolicy(Policy):
    def __init__(self, choices: Sequence):
        self.choices = choices

    def step(self, state):
        return {'command': random.choice(self.choices)}


class PlayerPolicy(Policy):
    print_state = True

    def step(self, state):
        print(state)
        action = -1
        while action not in range(3):
            try:
                action = int(input('Select action: 0 (Stay), 1 (Hit), 2 (Double)'))
            except ValueError:
                pass
        return {'command': int(action)}


class BasicPolicy(Policy):
    """Apply strategy from https://www.blackjackapprenticeship.com/blackjack-strategy-charts/."""  # noqa

    @staticmethod
    def strategy_matrix(player: Hand, dealer: Hand, player_ace: bool):
        """Apply stragety from https://www.blackjackapprenticeship.com/blackjack-strategy-charts/."""  # noqa
        # Soft hand
        if player_ace and len(player) < 3:
            if player.has_rank(9):
                return 0
            elif player.has_rank(8) and dealer.is_ranks(6):
                return 2
            elif player.has_rank(8):
                return 0
            elif player.has_rank(7) and dealer.has_rank_between(2, 6):
                return 2
            elif player.has_rank(7) and dealer.has_rank_between(7, 8):
                return 0
            elif player.has_rank(7) and dealer.has_rank_between(9, 11):
                return 1
            elif player.has_rank(6) and dealer.is_ranks(2):
                return 1
            elif player.has_rank_between(2, 5) and dealer.has_rank_between(2, 3):
                return 1
            elif player.has_rank_between(2, 6) and dealer.has_rank_between(7, 11):
                return 1
            elif player.has_rank_between(2, 3) and dealer.is_ranks(4):
                return 1
            else:
                return 2
        # Hard hand
        if 12 <= player.value <= 16 and dealer.has_rank_between(7, 11):
            return 1
        elif player.value == 12 and dealer.has_rank_between(2, 3):
            return 1
        elif player.value >= 12:
            return 0
        elif player.value == 10 and dealer.has_rank_between(10, 11):
            return 1
        elif 10 <= player.value <= 11:
            return 2
        elif player.value == 9 and dealer.has_rank_between(3, 6):
            return 2
        else:
            return 1

    def step(self, state):
        return {
            'command': self.strategy_matrix(
                state['player_hand'], state['dealer_hand'], state['player_ace']
            )
        }


def get_policy(policy: str) -> Policy:
    if policy == 'random':
        return RandomPolicy((0, 1, 2))
    elif policy == 'random_conservative':
        return RandomPolicy((0, 1))
    elif policy == 'player':
        return PlayerPolicy()
    elif policy == 'basic':
        return BasicPolicy()
    else:
        raise ValueError(f'Policy {policy} not found.')


def get_reward(results):
    reward_mapping = {
        (0, False): -1,
        (0, True): -2,
        (1, False): 0,
        (1, True): 0,
        (2, False): 1,
        (2, True): 2,
    }
    counter = collections.Counter(results)
    reward = 0
    total = 0
    for elem, cnt in counter.items():
        total += cnt
        reward += reward_mapping[elem] * cnt
    return reward / total


def test_policy(n_games, policy_name: str):
    policy = get_policy(policy_name)
    print(f'Using {policy_name} policy.')

    model = SimulatorModel()
    results = []
    for game in range(n_games):
        state = model.reset()
        while state['result'] < 0:
            state = model.step(policy.step(state))
            if state['result'] >= 0:
                results.append((state['result'], state['double']))
        if getattr(policy, 'print_state', False):
            print(state)
    reward = get_reward(results)
    print(reward)

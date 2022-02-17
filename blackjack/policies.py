"""Policies that can be evaluated in blackjack."""
import collections
import random
from abc import ABC, abstractmethod
from collections.abc import Sequence

import requests

from blackjack.blackjack import Hand, SimulatorModel

AVAILABLE_POLICIES = ['basic', 'brain', 'random', 'random_conservative', 'player']


class Policy(ABC):
    """Abstract Base Class representing a policy."""

    @abstractmethod
    def step(self, state):
        """Choose an action from ``state``."""


class RandomPolicy(Policy):
    """Randomly select an action."""
    def __init__(self, choices: Sequence):
        self.choices = choices

    def step(self, state):
        return {'command': random.choice(self.choices)}


class PlayerPolicy(Policy):
    """Create an interactive session to evaluate a human player."""
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
        # Surrender
        if (
            player.value == 16 and dealer.has_rank_between(9, 11) or
            player.value == 15 and dealer.has_rank(10)
        ):
            return 3

        # Soft hand
        if player_ace and len(player) < 3:
            if player.has_rank(8) and dealer.is_ranks(6):
                return 2
            elif player.has_rank_between(8, 9):
                return 0
            elif player.has_rank(7) and dealer.has_rank_between(2, 6):
                return 2
            elif player.has_rank(7) and dealer.has_rank_between(7, 8):
                return 0
            elif (
                player.has_rank(7) and dealer.has_rank_between(9, 11) or
                player.has_rank(6) and dealer.is_ranks(2) or
                player.has_rank_between(2, 5) and dealer.has_rank_between(2, 3) or
                player.has_rank_between(2, 6) and dealer.has_rank_between(7, 11) or
                player.has_rank_between(2, 3) and dealer.is_ranks(4)
            ):
                return 1
            else:
                return 2
        # Hard hand
        if (
            12 <= player.value <= 16 and dealer.has_rank_between(7, 11) or
            player.value == 12 and dealer.has_rank_between(2, 3)
        ):
            return 1
        elif player.value >= 12:
            return 0
        elif player.value == 10 and dealer.has_rank_between(10, 11):
            return 1
        elif (
            10 <= player.value <= 11 or
            player.value == 9 and dealer.has_rank_between(3, 6)
        ):
            return 2
        else:
            return 1

    def step(self, state):
        return {
            'command': self.strategy_matrix(
                state['player_hand'], state['dealer_hand'], state['player_ace']
            )
        }


class BrainPolicy(Policy):
    """Poll actions from a deployed brain."""
    def __init__(self, host, port):
        self.base_url = f'http://{host}:{port}'

    def step(self, state):
        response = requests.get(f'{self.base_url}/v1/prediction', json=state)
        return response.json()


def get_policy(policy: str, host, port) -> Policy:
    if policy == 'random':
        return RandomPolicy((0, 1, 2))
    elif policy == 'random_conservative':
        return RandomPolicy((0, 1))
    elif policy == 'player':
        return PlayerPolicy()
    elif policy == 'basic':
        return BasicPolicy()
    elif policy == 'brain':
        return BrainPolicy(host, port)
    else:
        raise ValueError(f'Policy {policy} not found.')


def get_reward(state):
    # TODO: reimplement with pattern matching on python 3.10
    reward_mapping = {
        # (Result, Double, Surrender): Reward
        (0, False, True): -0.5,
        (0, False, False): -1,
        (0, True, True): -2,
        (0, True, False): -2,
        (1, False, True): 0,
        (1, False, False): 0,
        (1, True, True): 0,
        (1, True, False): 0,
        (2, False, True): 1,
        (2, False, False): 1,
        (2, True, True): 2,
        (2, True, False): 2,
    }
    return reward_mapping[state]


def get_mean_reward(results):
    counter = collections.Counter(results)
    reward = 0
    total = 0
    for elem, cnt in counter.items():
        total += cnt
        reward += get_reward(elem) * cnt
    return reward / total


def evaluate_policy(n_games, policy_name: str, host: str, port: int):
    """Evaluate policy ``policy_name`` by playing ``n_games."""
    policy = get_policy(policy_name, host=host, port=port)
    print(f'Using {policy_name} policy.')

    model = SimulatorModel()
    results = []
    for game in range(n_games):
        state = model.reset({})
        while state['result'] < 0:
            state = model.step(policy.step(state))
            if state['result'] >= 0:
                results.append((state['result'], state['double'], state['surrender']))
        if getattr(policy, 'print_state', False):
            print(state)
    reward = get_mean_reward(results)
    print(reward)

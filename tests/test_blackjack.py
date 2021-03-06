import pytest

from blackjack.blackjack import Card, Hand
from blackjack.policies import get_reward


hands = [
    (Hand([]), 0),
    (Hand([Card('2', 'x')]), 2),
    (Hand([Card('J', 'x')]), 10),
    (Hand([Card('K', 'x')]), 10),
    (Hand([Card('A', 'x')]), 11),
    (Hand([Card('A', 'x'), Card('A', 'x')]), 12),
    (Hand([Card('A', 'x'), Card('K', 'x')]), 21),
    (Hand([Card('A', 'x'), Card('3', 'x')]), 14),
    (Hand([Card('A', 'x'), Card('A', 'x'), Card('A', 'x')]), 13),
    (Hand([Card('A', 'x'), Card('J', 'x'), Card('Q', 'x')]), 21),
    (Hand([Card('A', 'x'), Card('J', 'x'), Card('Q', 'x'), Card('J', 'x')]), 31),
]


@pytest.mark.parametrize("test_input, expected", hands)
def test_hand_value(test_input, expected):
    assert test_input.value == expected


def test_hand_value_raises_valueerror():
    with pytest.raises(ValueError):
        Hand([Card('F', 'x')]).value


def test_hand_has_ace():
    assert Hand([Card('A', 'x')]).has_ace()


def test_hand_has_not_ace():
    assert not Hand([Card('J', 'x')]).has_ace()


hand_has_rank = [
    (Hand([]), 3, False),
    (Hand([Card('3', 'x')]), 3, True),
    (Hand([Card('4', 'x')]), 3, False),
    (Hand([Card('3', 'x')]), '3', True),
    (Hand([Card('4', 'x')]), '3', False),
    (Hand([Card('J', 'x')]), 'J', True),
    (Hand([Card('J', 'x')]), 'Q', False),
]


@pytest.mark.parametrize("hand, ranks, expected", hand_has_rank)
def test_hand_has_ranks(hand, ranks, expected):
    assert hand.has_rank(ranks) == expected


hand_is_ranks = [
    (Hand([]), (3, ), False),
    (Hand([Card('3', 'x')]), (3, ), True),
    (Hand([Card('4', 'x')]), (3, ), False),
    (Hand([Card('3', 'x')]), ('3', ), True),
    (Hand([Card('4', 'x')]), ('3', ), False),
    (Hand([Card('J', 'x')]), ('J', ), True),
    (Hand([Card('J', 'x')]), ('Q', ), False),
    (Hand([Card('J', 'x')]), ('J', 3), False),
    (Hand([Card('J', 'x'), Card('3', 'x')]), ('J', ), False),
    (Hand([Card('J', 'x'), Card('3', 'x')]), ('J', 3), True),
    (Hand([Card('J', 'x'), Card('3', 'x')]), ('J', 3, '3'), False),
    (Hand([Card('J', 'x'), Card('3', 'x'), Card('3', 'x')]), ('J', 3, '3'), True),
]


@pytest.mark.parametrize("hand, ranks, expected", hand_is_ranks)
def test_hand_is_ranks(hand, ranks, expected):
    assert hand.is_ranks(*ranks) == expected


hand_has_rank_between = [
    (Hand([]), (1, 3), False),
    (Hand([Card('3', 'x')]), (1, 3), True),
    (Hand([Card('A', 'x'), Card('3', 'x')]), (1, 3), True),
    (Hand([Card('4', 'x')]), (1, 3), False),
    (Hand([Card('A', 'x'), Card('4', 'x')]), (1, 3), False),
    (Hand([Card('J', 'x')]), (1, 10), True),
    (Hand([Card('A', 'x'), Card('Q', 'x')]), (1, 3), False),
]


@pytest.mark.parametrize("hand, ranks, expected", hand_has_rank_between)
def test_hand_has_rank_between(hand, ranks, expected):
    assert hand.has_rank_between(*ranks) == expected


reward_states = [
    ((0, False, False), -1),
    ((0, False, True), -.5),
    ((0, True, False), -2),
    ((0, True, True), -2),
    ((1, False, False), 0),
    ((1, False, True), 0),
    ((1, True, False), 0),
    ((1, True, True), 0),
    ((2, False, False), 1),
    ((2, False, True), 1),
    ((2, True, False), 2),
    ((2, True, True), 2),
]


@pytest.mark.parametrize("state, expected", reward_states)
def test_state_has_reward(state, expected):
    assert get_reward(state) == expected

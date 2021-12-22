import pytest

from blackjack.blackjack import Card, Hand


hands = [
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
# test_blossom.py

import pytest
from blossom import Blossom


@pytest.fixture(name="my_blossom")
def fixture_blossom():
    '''Returns a Blossom instance with parse and logger'''
    return Blossom("words_alpha.txt", "slurepg")


def test_alpha_first_word(my_blossom):
    """First word"""
    assert my_blossom.words[0] == "eels"


def test_alpha_find_word(my_blossom):
    """Find word"""
    assert my_blossom.words.index("peerless") == 111
    assert my_blossom.words[111] == "peerless"


def test_alpha_length_bonuses(my_blossom):
    """Length bonuses"""
    assert my_blossom.length_bonus("abc") == 0
    assert my_blossom.length_bonus("abcde") == 4
    assert my_blossom.length_bonus("abcdef") == 6
    assert my_blossom.length_bonus("abcdefg") == 12
    assert my_blossom.length_bonus("abcdefghi") == 18

# test_blossom.py

import pytest
from blossom import Blossom


@pytest.fixture(name="alpha_blossom")
def fixture_blossom() -> Blossom:
    '''Returns a Blossom instance with parse and logger'''
    return Blossom(words_source="words_alpha.txt", flower="slurepg", min_length=6)


def test_blossom_first_word(alpha_blossom: Blossom) -> None:
    """First word"""
    assert alpha_blossom.words[0] == "eggers"


def test_blossom_find_word(alpha_blossom: Blossom) -> None:
    """Find word"""
    assert alpha_blossom.words.index("peerless") == 40
    assert alpha_blossom.words[40] == "peerless"


def test_blossom_word_bonuses() -> None:
    """Length bonuses"""
    assert Blossom.word_bonus("g", "abc") == 0
    assert Blossom.word_bonus("b", "abc") == 5
    assert Blossom.word_bonus("g", "abcd") == 2
    assert Blossom.word_bonus("b", "abcd") == 2 + 5
    assert Blossom.word_bonus("g", "abcde") == 4
    assert Blossom.word_bonus("b", "abcde") == 9
    assert Blossom.word_bonus("b", "abcdb") == 4 + 5 * 2
    assert Blossom.word_bonus("g", "abcdef") == 6
    assert Blossom.word_bonus("b", "abcdef") == 6 + 5
    assert Blossom.word_bonus("g", "abcdefg") == 12 + 5 + 7
    assert Blossom.word_bonus("b", "abcdefg") == 12 + 5 + 7
    assert Blossom.word_bonus("g", "abcdefga") == 15 + 5 + 7
    assert Blossom.word_bonus("b", "abcdefga") == 15 + 5 + 7
    assert Blossom.word_bonus("b", "abcdefgab") == 18 + 5 * 2 + 7

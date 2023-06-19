# test_blossom.py

import pytest
from blossom import Blossom

@pytest.fixture(name="my_blossom")
def fixture_blossom():
    '''Returns a Blossom instance with parse and logger'''
    return Blossom("words_alpha.txt", "slurepg")

def test_default_initial_amount(my_blossom):
    """Test init loading of file"""
    assert my_blossom.words[0] == "eels"

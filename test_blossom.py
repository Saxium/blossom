"""Tests for blossom."""

import pytest
from blossom import Blossom, BlossomException, blossom_parser


@pytest.fixture(name="alpha_blossom")  # type: ignore[untyped-decorator]
def fixture_blossom() -> Blossom:
    """Returns a Blossom instance with parse and logger"""
    return Blossom(words_source="words_alpha4.txt", flower="slurepg", min_length=6)


def test_blossom_first_word(alpha_blossom: Blossom) -> None:
    """First word"""
    assert alpha_blossom.words
    assert "eggers" in alpha_blossom.words


def test_blossom_find_word(alpha_blossom: Blossom) -> None:
    """Find word using list.index."""
    assert alpha_blossom.words
    index = alpha_blossom.words.index("peerless")
    assert index == 40


def test_blossom_word_bonuses() -> None:
    """Length bonuses"""
    assert not Blossom.word_bonus("g", "abc")
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


def test_load_words_missing_file_raises() -> None:
    """Missing word source file raises BlossomException."""
    with pytest.raises(Exception, match="No such file"):
        Blossom(words_source="missing.txt", flower="slurepg", min_length=6)


def test_make_scores_and_show_scores(tmp_path) -> None:
    """make_scores populates scores and show_scores returns ordered values."""
    words_file = tmp_path / "words.txt"
    words_file.write_text("abcd\nabce\nabcf\n", encoding="utf-8")
    blossom = Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)
    assert blossom.make_scores("b", 0)
    scores = blossom.show_scores("b", print_output=False)
    assert scores[0][0] == "abcd"
    assert scores == sorted(scores, key=lambda item: item[1])


def test_load_words_rejects_short_words(tmp_path) -> None:
    """Blossom ignores words shorter than four letters."""
    words_file = tmp_path / "words.txt"
    words_file.write_text("ab\nabc\nabcd\nabcde\n", encoding="utf-8")
    blossom = Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)
    assert blossom.words == ["abcd", "abcde"]


def test_order_ranks_and_collect_bonus() -> None:
    """order_ranks sorts and collect_bonus filters correctly."""
    ranks = {"one": 1, "two": 2, "three": 3}
    assert Blossom.order_ranks(ranks) == [("one", 1), ("two", 2), ("three", 3)]
    assert Blossom.order_ranks(ranks, reverse=True) == [("three", 3), ("two", 2), ("one", 1)]

    blossom = Blossom(words_source="words_alpha4.txt", flower="slurepg", min_length=6)
    scores = {"apple": {"p": 10}, "pear": {"p": 8}}
    assert blossom.collect_bonus(scores, "p") == {"apple": 10, "pear": 8}


def test_top_score_and_simple_print(tmp_path) -> None:
    """top_score returns a structured result and simple_print returns words."""
    words_file = tmp_path / "words.txt"
    words_file.write_text(
        "abcd\nabce\nabcf\nabcg\nabde\nabdf\nabdg\nabef\nabeg\nabfg\nacde\nacdf\n",
        encoding="utf-8",
    )
    blossom = Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)
    result = blossom.top_score(min_score=0, print_output=False)

    total = result["total"]
    assert isinstance(total, int)
    assert total >= 0

    petals = result["petals"]
    assert isinstance(petals, str)
    assert petals

    rows = result["rows"]
    assert isinstance(rows, list)
    assert len(rows) == 12

    assert blossom.simple_print() == list(blossom.words)


def test_blossom_init_non_unique_chars() -> None:
    """Blossom init raises exception for non-unique flower chars."""
    with pytest.raises(BlossomException, match="Seven unique chars required"):
        Blossom(words_source="words_alpha4.txt", flower="aaaaaaa", min_length=6)


def test_blossom_init_wrong_length() -> None:
    """Blossom init raises exception for wrong number of chars."""
    with pytest.raises(BlossomException, match="Seven unique chars required"):
        Blossom(words_source="words_alpha4.txt", flower="abcdef", min_length=6)


def test_load_words_no_matching_words(tmp_path) -> None:
    """load_words raises exception when no words match pistil."""
    words_file = tmp_path / "words.txt"
    words_file.write_text("xyz\npqr\nstuvwx\n", encoding="utf-8")
    with pytest.raises(BlossomException, match="No words matching pistil"):
        Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)


def test_make_scores_empty_words() -> None:
    """make_scores returns False when no scores meet minimum."""
    blossom = Blossom(words_source="words_alpha4.txt", flower="slurepg", min_length=6)
    result = blossom.make_scores("s", min_score=999)
    assert result is False


def test_show_scores_empty_scores(tmp_path) -> None:
    """show_scores returns empty list when no scores for bonus."""
    words_file = tmp_path / "words.txt"
    words_file.write_text("abcd\n", encoding="utf-8")
    blossom = Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)
    blossom.scores = {"abcd": {"x": 10}}
    scores = blossom.show_scores("z", print_output=False)
    assert scores == []


def test_simple_print_returns_words(tmp_path) -> None:
    """simple_print returns all words."""
    words_file = tmp_path / "words.txt"
    words_file.write_text("ab\nabc\nabcd\n", encoding="utf-8")
    blossom = Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)
    result = blossom.simple_print()
    assert result == ["abcd"]


def test_blossom_parser_bonus() -> None:
    """Parser correctly handles bonus argument."""
    parser = blossom_parser()
    args = parser.parse_args(["-f", "abcdefg", "-b", "a"])
    assert args.flower == "abcdefg"
    assert args.bonus == "a"


def test_blossom_parser_top() -> None:
    """Parser correctly handles top argument."""
    parser = blossom_parser()
    args = parser.parse_args(["-f", "abcdefg", "-t"])
    assert args.flower == "abcdefg"
    assert args.top is True


def test_blossom_parser_print() -> None:
    """Parser correctly handles print argument."""
    parser = blossom_parser()
    args = parser.parse_args(["-f", "abcdefg", "-p"])
    assert args.flower == "abcdefg"
    assert args.print is True


def test_blossom_parser_defaults() -> None:
    """Parser sets correct defaults."""
    parser = blossom_parser()
    args = parser.parse_args(["-f", "abcdefg", "-b", "a"])
    assert args.words == "words_alpha4.txt"
    assert args.min == 6
    assert args.score == 15
    assert args.json is False
    assert args.log is False

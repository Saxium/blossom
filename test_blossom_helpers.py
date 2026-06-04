"""Tests for blossom helper functions (private functions with underscore prefix)."""

import json
import pytest
from argparse import Namespace
from blossom import (
    Blossom,
    _output_json,
    _handle_bonus,
    _handle_top,
    _handle_print,
)
import logging


def test_output_json_prints_valid_json(capsys) -> None:  # type: ignore[no-untyped-def]
    """_output_json prints valid JSON."""
    payload = {"key": "value", "number": 42}
    _output_json(payload)
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed == payload


def test_handle_bonus_with_json(tmp_path, capsys) -> None:  # type: ignore[no-untyped-def]
    """_handle_bonus returns True and outputs JSON when requested."""
    words_file = tmp_path / "words.txt"
    words_file.write_text("abcd\nabcde\n", encoding="utf-8")
    blossom = Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)
    logger = logging.getLogger(__name__)
    args = Namespace(bonus="a", score=0, json=True)
    result = _handle_bonus(blossom, args, logger)
    assert result is True
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed == {
        "bonus": "a",
        "scores": [
            {"word": "abcd", "score": 7},
            {"word": "abcde", "score": 9},
        ],
    }


def test_handle_top_with_json(tmp_path, capsys) -> None:  # type: ignore[no-untyped-def]
    """_handle_top returns True and outputs JSON when requested."""
    words_file = tmp_path / "words.txt"
    words_file.write_text(
        "abcd\nabce\nabcf\nabcg\nabde\nabdf\nabdg\nabef\nabeg\nabfg\nacde\nacdf\n",
        encoding="utf-8",
    )
    blossom = Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)
    args = Namespace(score=0, json=True)
    result = _handle_top(blossom, args)
    assert result is True
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed == {
        "total": 84,
        "petals": "bcdegf",
        "rows": [
            {"bonus": "b", "word": "abcd", "score": 7},
            {"bonus": "c", "word": "abce", "score": 7},
            {"bonus": "d", "word": "abde", "score": 7},
            {"bonus": "e", "word": "abef", "score": 7},
            {"bonus": "g", "word": "abcg", "score": 7},
            {"bonus": "f", "word": "abcf", "score": 7},
            {"bonus": "b", "word": "abdf", "score": 7},
            {"bonus": "c", "word": "acde", "score": 7},
            {"bonus": "d", "word": "abdg", "score": 7},
            {"bonus": "e", "word": "abeg", "score": 7},
            {"bonus": "g", "word": "abfg", "score": 7},
            {"bonus": "f", "word": "acdf", "score": 7},
        ],
    }


def test_handle_print_with_json(tmp_path, capsys) -> None:  # type: ignore[no-untyped-def]
    """_handle_print returns True and outputs JSON when requested."""
    words_file = tmp_path / "words.txt"
    words_file.write_text("abcd\nabcde\n", encoding="utf-8")
    blossom = Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)
    args = Namespace(json=True)
    result = _handle_print(blossom, args)
    assert result is True
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert "words" in parsed
    assert parsed["words"] == ["abcd", "abcde"]


def test_handle_print_without_json(tmp_path, capsys) -> None:  # type: ignore[no-untyped-def]
    """_handle_print prints words when JSON not requested."""
    words_file = tmp_path / "words.txt"
    words_file.write_text("abcd\nabcde\n", encoding="utf-8")
    blossom = Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)
    args = Namespace(json=False)
    result = _handle_print(blossom, args)
    assert result is True
    captured = capsys.readouterr()
    assert "abcd" in captured.out
    assert "abcde" in captured.out


def test_rank_variation_indirectly(tmp_path) -> None:
    """_rank_variation is tested indirectly through top_score."""
    words_file = tmp_path / "words.txt"
    words_file.write_text(
        "abcd\nabce\nabcf\nabcg\nabde\nabdf\nabdg\nabef\nabeg\nabfg\nacde\nacdf\n",
        encoding="utf-8",
    )
    blossom = Blossom(words_source=str(words_file), flower="abcdefg", min_length=2)
    result = blossom.top_score(min_score=0, print_output=False)
    total = result["total"]
    rows = result["rows"]
    assert isinstance(total, int)
    assert total > 0
    assert len(rows) == 12
    for row in rows:
        assert "bonus" in row
        assert "word" in row
        assert "score" in row

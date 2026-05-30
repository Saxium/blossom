#!/usr/bin/env python3
"""Blossom."""
import json
import logging
import os.path
import sys
from argparse import ArgumentParser, Namespace
from logging import Logger
from typing import Optional
from itertools import permutations
from copy import deepcopy


class BlossomException(Exception):
    """Blossom Exception."""


class Blossom:
    """Blossom Online Word Game."""

    def __init__(self, words_source: str, flower: str,
                 min_length: int, logger: Optional[Logger] = None) -> None:
        """Initialise blossom."""
        self.flower: str = flower
        self.logger: Logger = logger or logging.getLogger(__name__)
        self.words: list[str] = []
        self.scores: dict[str, dict[str, int]] = {}

        if len(set(flower)) != 7:
            raise BlossomException('Seven unique chars required for flower')

        self.petals: list[str] = list(flower)
        self.pistil: str = self.petals.pop(0)
        self.petals_set: set[str] = set(self.petals)

        self.words = self.load_words(words_source, min_length)

    def load_words(self, words_source: str, min_length: int) -> list[str]:
        """Load words and filter pistil."""
        words: list[str] = []
        if not os.path.exists(words_source):
            raise BlossomException(f'No such file: {words_source}')

        pistil_set: set[str] = {self.pistil}
        with open(words_source, encoding="utf-8", newline='') as words_file:
            for line in words_file:
                word = line.strip()
                if not word.isalpha():
                    continue
                if len(word) < min_length:
                    continue
                if self.pistil not in word:
                    continue
                if set(word) - self.petals_set == pistil_set:
                    words.append(word)

        if len(words) == 0:
            raise BlossomException(f'No words matching pistil: {self.pistil}')

        return words

    @staticmethod
    def word_bonus(bonus: str, word: str) -> int:
        """Calculate for word bonus."""
        bonus_chars: list[str] = [item for item in list(word) if item == bonus]
        all_bonus: int = 0
        if len(set(word)) == 7:
            all_bonus = 7
        if len(word) > 7:
            length_bonus = 12 + (len(word) - 7) * 3
        else:
            length_bonus = [0, 0, 0, 0, 2, 4, 6, 12][len(word)]
        score: int = length_bonus + len(bonus_chars) * 5 + all_bonus
        return score

    def make_scores(self, bonus: str, min_score: int) -> bool:
        """Calc word and total score."""
        if not self.words:
            raise BlossomException("Words list should exist")
        count: int = 0
        for word in self.words:
            score = self.word_bonus(bonus, word)
            if score >= min_score:
                count += 1
                if word in self.scores:
                    self.scores[word][bonus] = score
                else:
                    self.scores[word] = {bonus: score}
        if count == 0:
            return False
        return True

    @staticmethod
    def order_ranks(ranks: dict[str, int],
                    reverse: bool = False) -> list[tuple[str, int]]:
        """Rank dict to ordered list."""
        return sorted(ranks.items(), key=lambda x: x[1], reverse=reverse)

    def collect_bonus(self, scores: dict[str, dict[str, int]],
                      bonus: str) -> dict[str, int]:
        """Collect score:word list by bonus."""
        if not scores:
            raise BlossomException("Scores list should exist")
        build: dict[str, int] = {}
        for word, bonuses in scores.items():
            if bonus in bonuses:
                score = scores[word][bonus]
                build[word] = score
        return build

    def _rank_variation(self, petals: str) -> tuple[int, list[tuple[str, str, int]]]:
        """Score a specific petal ordering."""
        scores = deepcopy(self.scores)
        total = 0
        data: list[tuple[str, str, int]] = []
        for _ in (1, 2):
            for bonus in petals:
                ranks = self.collect_bonus(scores, bonus)
                top_list = self.order_ranks(ranks, reverse=True)
                word, rank = top_list[0]
                total += rank
                del scores[word]
                data.append((bonus, word, rank))
        return total, data

    def top_score(self, min_score: int,
                  print_output: bool = True) -> dict[str, object]:
        """Top score possible."""
        if not self.petals:
            raise BlossomException("Petals list should exist")
        for bonus in self.petals:
            if not self.make_scores(bonus, min_score):
                raise BlossomException(
                    f"No scores collected with min {min_score} bonus {bonus}")

        variations = {''.join(p) for p in permutations(self.petals)}
        best: tuple[int, str, list[tuple[str, str, int]]] = (0, "", [])
        for petals in variations:
            total, data = self._rank_variation(petals)
            if total > best[0]:
                best = (total, petals, data)
        result = {
            "total": best[0],
            "petals": best[1],
            "rows": [
                {"bonus": bonus, "word": word, "score": rank}
                for bonus, word, rank in best[2]
            ],
        }
        if print_output:
            for row in best[2]:
                bonus, word, rank = row
                print(f'{bonus} : {word} = {rank}')
            print(f'Total = {best[0]}')
        return result

    def simple_print(self) -> list[str]:
        """Gather results."""
        if not self.words:
            raise BlossomException("Words list should exist")
        return list(self.words)

    def show_scores(self, bonus: str,
                    print_output: bool = True) -> list[tuple[str, int]]:
        """Show scores for a bonus."""
        if not self.scores:
            raise BlossomException("Scores list should exist")
        ranks = self.collect_bonus(self.scores, bonus)
        ordered = self.order_ranks(ranks)
        if print_output:
            for _ in ordered:
                word, rank = _
                print(f'{word} = {rank}')
        return ordered


def blossom_parser() -> ArgumentParser:
    """Blossom parser."""
    parser = ArgumentParser()
    parser.add_argument(
        '-w', '--words', default="words.txt", help="alpha words")
    parser.add_argument(
        '-l', '--log', help="logging output", action='store_true')
    parser.add_argument('-f', '--flower', required=True,
                        help="petals (pistil first)")
    parser.add_argument('-m', '--min', type=int, default=6,
                        help="minium word length")
    parser.add_argument('-s', '--score', type=int,
                        default=15, help="words above score")
    parser.add_argument('--json', action='store_true',
                        help="json output")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--bonus', help="bonus letter")
    group.add_argument('-t', '--top', action="store_true",
                       default=False, help="highest solution")
    group.add_argument('-p', '--print', action="store_true",
                       default=False, help="just print")

    return parser


def _output_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _handle_bonus(blossom: Blossom, args: Namespace, logger: logging.Logger) -> bool:
    if not blossom.make_scores(args.bonus, args.score):
        raise BlossomException(
            f"No scores collected with min {args.score} bonus {args.bonus}")

    logger.debug("Scores: %s", blossom.scores)
    scores = blossom.show_scores(args.bonus, print_output=not args.json)
    if args.json:
        payload = {
            "bonus": args.bonus,
            "scores": [{"word": word, "score": score}
                       for word, score in scores],
        }
        _output_json(payload)
    return True


def _handle_top(blossom: Blossom, args: Namespace) -> bool:
    result = blossom.top_score(args.score, print_output=not args.json)
    if args.json:
        _output_json(result)
    return True


def _handle_print(blossom: Blossom, args: Namespace) -> bool:
    words = blossom.simple_print()
    if args.json:
        _output_json({"words": words})
        return True
    for word in words:
        print(f"{word}")
    return True


def main() -> bool:
    """Handle program parameters."""
    parser = blossom_parser()
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    handle = logging.StreamHandler()

    if args.log:
        logger.setLevel(logging.DEBUG)
        handle.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        handle.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handle.setFormatter(formatter)
    logger.addHandler(handle)

    if len(set(args.flower)) != 7:
        parser.error('Seven unique chars required for flower')

    if args.bonus:
        if len(args.bonus) != 1:
            parser.error('Single char required for bonus')

        if len(set(args.flower + args.bonus)) != 7:
            parser.error(
                f'Bonus "{args.bonus}" must be in flower "{args.flower}"')

    result = False
    try:
        blossom: Blossom = Blossom(args.words, args.flower, args.min, logger)

        if args.bonus:
            result = _handle_bonus(blossom, args, logger)
        elif args.top:
            result = _handle_top(blossom, args)
        elif args.print:
            result = _handle_print(blossom, args)
    except BlossomException as exc:
        logger.error(str(exc))
        result = False

    return result


if __name__ == "__main__":
    if main():
        sys.exit(0)
    sys.exit(1)

#!/usr/bin/python3

import logging
import os.path
import sys
from argparse import ArgumentParser
from logging import Logger
from typing import Optional
from itertools import permutations
from copy import deepcopy


class BlossomException(Exception):
    """Blossom Exception"""


class Blossom:
    """Blossom Online Word Game"""

    def __init__(self, words_source: str, flower: str,
                 min_length: int, logger: Optional[Logger] = None) -> None:
        self.flower: str = flower
        self.logger: Logger = logger or logging.getLogger(__name__)
        self.words: list[str] = []
        self.scores: dict[str, dict[str, int]] = {}

        assert len(set(flower)) == 7, 'Seven unique chars required for flower'

        self.petals: list[str] = list(flower)
        self.pistil: str = self.petals.pop(0)

        self.words = self.load_words(words_source, min_length)

    def load_words(self, words_source: str, min_length: int) -> list[str]:
        """Load words and filter pistil"""
        words: list[str] = []
        if not os.path.exists(words_source):
            raise BlossomException(f'No such file: {words_source}')

        # pylint: disable=consider-using-with
        words_file = open(words_source, encoding="utf-8", newline='')
        if words_file is None:
            raise BlossomException(f'Failed to open file: {words_source}')

        for line in words_file:
            word = line.strip()
            if len(word) >= min_length:
                if word.find(self.pistil) >= 0:
                    if set(word) - set(self.petals) == set(self.pistil):
                        words.append(word)
        words_file.close()

        if len(words) == 0:
            raise BlossomException(f'No words mathcing pistil: {self.pistil}')

        return words

    @staticmethod
    def word_bonus(bonus: str, word: str) -> int:
        """Formula for word bonus"""
        bonus_chars: list[str] = [item for item in list(word) if item == bonus]
        all_bonus: int = 0
        if len(set(word)) == 7:
            all_bonus = 7
        if len(word) > 7:
            length_bonus = 12 + (len(word) - 7) * 3
        else:
            length_bonus = [0, 0, 0, 0, 2, 5, 6, 12][len(word)]
        score: int = length_bonus + len(bonus_chars) * 5 + all_bonus
        return score

    def make_scores(self, bonus: str, min_score: int) -> bool:
        """Calc word and total score"""
        assert self.words, "Words list should exist"
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
        """Rank dict to ordered list"""
        return sorted(ranks.items(), key=lambda x: x[1], reverse=reverse)

    def collect_bonus(self, scores: dict[str, dict[str, int]],
                      bonus: str) -> dict[str, int]:
        """Collect score:word list by bonus"""
        assert scores, "Scores list should exist"
        build: dict[str, int] = {}
        for word, bonuses in scores.items():
            if bonus in bonuses:
                score = scores[word][bonus]
                build[word] = score
        return build

    def top_score(self, min_score: int) -> None:
        """Top score possible"""
        assert self.petals
        for bonus in self.petals:
            assert self.make_scores(bonus, min_score) is True

        variations: set[str] = set([''.join(p) for p in permutations(self.petals)])
        best: tuple[int, str, list[tuple[str, str, int]]] = (0, "", [])
        for petals in list(variations):
            scores: dict[str, dict[str, int]] = deepcopy(self.scores)
            total: int = 0
            data: list[tuple[str, str, int]] = []
            for _ in [1, 2]:
                for bonus in petals:
                    ranks = self.collect_bonus(scores, bonus)
                    top_list = self.order_ranks(ranks, reverse=True)
                    word, rank = top_list[0]
                    total += rank
                    del scores[word]  # Word unusable for next bonus
                    data.append((bonus, word, rank))
            if total > best[0]:
                best = (total, petals, data)
        for row in best[2]:
            bonus, word, rank = row
            print(f'{bonus} : {word} = {rank}')
        print(f'Total = {best[0]}')

    def simple_print(self) -> None:
        """Show results"""
        assert self.words, "Words list should exist"
        for word in self.words:
            print(f'{word}')

    def show_scores(self, bonus: str) -> None:
        """Show scores for a bonus"""
        ranks = self.collect_bonus(self.scores, bonus)
        for _ in self.order_ranks(ranks):
            word, rank = _
            print(f'{rank} : {word}')


def blossom_parser() -> ArgumentParser:
    """Blossom parser"""
    parser = ArgumentParser()
    parser.add_argument('-w', '--words', default="words.txt", help="alpha words")
    parser.add_argument('-l', '--log', help="logging output", action='store_true')
    parser.add_argument('-f', '--flower', required=True, help="petals (pistil first)")
    parser.add_argument('-m', '--min', type=int, default=6, help="minium word length")
    parser.add_argument('-s', '--score', type=int, default=20, help="words above score")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--bonus', help="bonus letter")
    group.add_argument('-t', '--top', action="store_true", default=False, help="highest solution")
    group.add_argument('-p', '--print', action="store_true", default=False, help="just print")

    return parser


def main() -> bool:
    """Main to handle program parameters"""
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

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handle.setFormatter(formatter)
    logger.addHandler(handle)

    if len(set(args.flower)) != 7:
        parser.error('Seven unique chars required for flower')
        return False

    if args.bonus:
        if len(args.bonus) != 1:
            parser.error('Single char required for bonus')
            return False

        if len(set(args.flower + args.bonus)) != 7:
            parser.error(f'Bonus "{args.bonus}" must be in flower "{args.flower}"')
            return False

    blossom: Blossom = Blossom(args.words, args.flower, args.min, logger)

    if args.bonus:
        assert blossom.make_scores(args.bonus, args.score) is True
        print(blossom.scores)
        blossom.show_scores(args.bonus)
        return True
    if args.top:
        blossom.top_score(args.score)
        return True
    if args.print:
        blossom.simple_print()
        return True

    return False


if __name__ == "__main__":
    if main():
        sys.exit(0)
    sys.exit(1)

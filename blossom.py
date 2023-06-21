#!/usr/bin/python3

import logging
import os.path
import sys
from argparse import ArgumentParser
from logging import Logger
from typing import Optional


class BlossomException(Exception):
    """Blossom Exception"""


class Blossom:
    """Blossom Online Word Game"""

    def __init__(self, words_source: str, flower: str,
                 min_length: int, logger: Optional[Logger] = None) -> None:
        self.flower = flower
        self.logger = logger or logging.getLogger(__name__)
        self.words = []
        self.scores = {}

        assert len(set(flower)) == 7, 'Seven unique chars required for flower'

        petals: list = list(flower)
        pistil: str = petals.pop(0)

        self.words = self.load_words(words_source, min_length, pistil, petals)

        self.pistil = pistil
        self.petals = petals

    def load_words(self, words_name, min_length, pistil, petals) -> list:
        """Load words and filter pistil"""
        words: list = []
        if not os.path.exists(words_name):
            raise BlossomException(f'No such file: {words_name}')

        # pylint: disable=consider-using-with
        words_file = open(words_name, encoding="utf-8", newline='')
        if words_file is None:
            raise BlossomException(f'Failed to open file: {words_name}')

        for line in words_file:
            word = line.strip()
            if len(word) >= min_length:
                if word.find(pistil) >= 0:
                    if set(word) - set(petals) == set(pistil):
                        words.append(word)
        words_file.close()

        if len(words) == 0:
            raise BlossomException(f'No words mathcing pistil: {pistil}')

        return words

    @staticmethod
    def length_bonus(word) -> int:
        """Formula for word length bonus"""
        length: int = len(word)
        if length < 4:
            return 0
        if length == 4:
            return 2
        if length == 5:
            return 4
        if length == 6:
            return 6
        return 12 + (length - 7) * 3

    def make_scores(self, bonus: str, min_score: int) -> bool:
        """Calc word and total score"""
        assert self.words, "Words list should exist"
        count: int = 0
        for word in self.words:
            bonus_chars: list = [item for item in list(word) if item == bonus]
            all_bonus: int = 0
            if len(set(word)) == 7:
                all_bonus = 7
            score: int = self.length_bonus(word) + len(bonus_chars) * 5 + all_bonus
            if score >= min_score:
                count += 1
                if word in self.scores:
                    self.scores[word]['bonuses'][bonus] = score
                else:
                    self.scores[word] = { 'bonuses' : { bonus: score } }
        if count == 0:
            return False
        return True

    @staticmethod
    def rank_scores(scores: dict, reverse=False) -> list:
        """Rank dict to ordered list"""
        return sorted(scores.items(), key=lambda x: x[1], reverse=reverse)

    def collect_bonus(self, bonus: str) -> dict:
        """Collect score:word list by bonus"""
        assert self.scores, "Scores list should exist"
        build = {}
        for word, bonuses in self.scores.items():
            if bonus in bonuses['bonuses']:
                score = self.scores[word]['bonuses'][bonus]
                build[word] = score
        return build

    def _avg_top(self, min_score: int):
        """Top twenty averaged"""
        assert self.petals
        build = {}
        for bonus in self.petals:
            assert self.make_scores(bonus, min_score) is True
            # ranks = self.rank_scores(scores)
            # ranks_count = min(len(scores), 5)
            # build[bonus] = ranks[:ranks_count]

    def calc_top(self, min_score: int):
        """Calculate top score"""
        self._avg_top(min_score)
        print(self.scores)

    def simple_print(self) -> bool:
        """Show results"""
        assert self.words, "Words list should exist"
        for word in self.words:
            print(f'{word}')
        return True

    def show_scores(self, bonus: str) -> None:
        """Show scores for a bonus"""
        scores = self.collect_bonus(bonus)
        for _ in self.rank_scores(scores):
            rank, word = _
            print(f'{rank} : {word}')


def blossom_parser():
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
        blossom.show_scores(args.bonus)
        return True
    if args.top:
        return blossom.calc_top(args.score)
    if args.print:
        return blossom.simple_print()

    return False


if __name__ == "__main__":
    if main():
        sys.exit(0)
    sys.exit(1)

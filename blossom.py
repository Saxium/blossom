#!/usr/bin/python3

import sys
from argparse import ArgumentParser
import os.path
import logging
from logging import Logger

class Blossom:
    """Blossom Online Word Game"""
    TMP_FILE:str = '/tmp/blossom.txt'

    def __init__(self, parser: ArgumentParser, logger: Logger = None) -> None:
        self.parser = parser
        self.logger = logger or logging.getLogger(__name__)

    def _match(self, word: str, pistil, petals) -> bool:
        """Match words with the pistil and optional number of petals """
        if word.find(pistil) >= 0:
            if set(word) - set(petals) == set(pistil):
                return True
        return False

    def _filter_words(self, words_name, min_length, pistil, petals) -> tuple:
        """Load words and filter"""
        words: list = []
        if not os.path.exists(words_name):
            self.parser.error(f'No such file: {words_name}')
            return (False, None)

        words_file = open(words_name, encoding="utf-8", newline='')    # pylint: disable=consider-using-with
        if words_file is None:
            self.parser.error(f'Failed to open file: {words_name}')
            return (False, None)

        for line in words_file:
            word = line.strip()
            if len(word) >= min_length:
                if self._match(word, pistil, petals):
                    words.append(word)

        words_file.close()
        return (True, words)

    def _length_bonus(self, word) -> int:
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

    def _rank(self, words: list, bonus: str, min_score: int) -> dict:
        """Calc word and total score"""
        build: dict = {}
        for word in words:
            bonus_chars: list = [item for item in list(word) if item == bonus]
            all_bonus: int = 0
            if len(set(word)) == 7:
                all_bonus = 7
            score: int = self._length_bonus(word) + len(bonus_chars)*5 + all_bonus
            if score >= min_score:
                build[word] = score
        return sorted((value,key) for (key,value) in build.items())

    def bloom(self, words_name: str, flower: str, bonus: str = None, min_length: int = 1, score: int = 1) -> bool:
        """Main blossum driver"""
        if len(set(flower)) != 7:
            self.parser.error('Seven unique chars required for flower')
            return False

        if len(bonus) != 1:
            self.parser.error('Single char required for bonus')
            return False

        if len(set(flower + bonus)) != 7:
            self.parser.error(f'Bonus "{bonus}" must be in flower "{flower}"')
            return False

        petals: list = list(flower)
        pistil: str = petals.pop(0)

        status, word_list = self._filter_words(words_name, min_length, pistil, petals)
        if status is False:
            return False

        ranks = self._rank(word_list, bonus, score)

        for _ in ranks:
            rank, word = _
            print(f'{rank} : {word}')

        return True

def main() -> bool:
    """Main to handle program parameters"""
    parser = ArgumentParser()
    parser.add_argument('-w', '--words', default="words_alpha.txt", help="alpha words")
    parser.add_argument('-l', '--log', help="logging output", action='store_true')
    parser.add_argument('-f', '--flower', required=True, help="petals (pistil first)")
    parser.add_argument('-b', '--bonus', required=True, help="bonus letter")
    parser.add_argument('-m', '--min', type=int, default=1, help="minium word length")
    parser.add_argument('-s', '--score', type=int, default=1, help="words above score")

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

    blossom: Blossom = Blossom(parser, logger)

    return blossom.bloom(args.words, args.flower, args.bonus, args.min, args.score)

if __name__ == "__main__":
    if main():
        sys.exit(0)
    sys.exit(1)

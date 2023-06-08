#!/usr/bin/python3

import sys
import argparse
import os.path
import json
import logging

from typing import List, TextIO, Optional

class Blossom:
    """Blossom Online Word Game"""
    TMP_FILE = '/tmp/blossom.txt'

    def __init__(self, parser, logger = None) -> None:
        self.parser = parser
        self.logger = logger or logging.getLogger(__name__)

    def _match(self, word: str, pistil, petals) -> bool:
        if word.find(pistil) >= 0:
            x = set(word) - set(petals)
            y = set(pistil)
            if x == y:
                return True
        return False

    def _filter_words(self, words_name, min, pistil, petals):
        words = []
        if not os.path.exists(words_name):
            self.parser.error(f'No such file: {words_name}')
            return (False, None)

        words_file = open(words_name, encoding="utf-8", newline='')    # pylint: disable=consider-using-with
        if words_file is None:
            self.parser.error(f'Failed to open file: {words_name}')
            return (False, None)

        for line in words_file:
            word = line.strip()
            if len(word) >= min:
                if self._match(word, pistil, petals):
                    words.append(word)

        words_file.close()
        return (True, words)

    def _length_bonus(self, word):
        length = len(word)
        if length < 4:
            return 0
        if length == 4:
            return 2
        if length == 5:
            return 4
        if length == 6:
            return 6
        return 12 + (length - 7) * 3

    def _rank(self, words: list, bonus: str, score: int):
        build = {}
        for word in words:
            bonus_chars = [item for item in list(word) if item == bonus]
            other_chars = [item for item in list(word) if item != bonus]
            all_bonus = 0
            if len(set(word)) == 7:
                all_bonus = 7
            rank = self._length_bonus(word) + len(bonus_chars)*5 + all_bonus
            if rank >= score:
                build[word] = rank
        return sorted((value,key) for (key,value) in build.items())

    def doit(self, words_name: str, flower: str, bonus: str = None, min: int = 1, score: int = 1) -> bool:
        """Create temp file with flower only"""
        if len(set(flower)) != 7:
            self.parser.error(f'Seven unique chars required for flower')
            return False

        if len(bonus) != 1:
            self.parser.error(f'Single char required for bonus')
            return False

        petals = list(flower)
        pistil = petals.pop(0)

        status, word_list = self._filter_words(words_name, min, pistil, petals)
        if status is False:
            return False

        ranks = self._rank(word_list, bonus, score)

        for x in ranks:
            rank, word = x
            print(f'{rank} : {word}')

        return True


def main() -> bool:
    """Main to handle program parameters"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--words', default="words_alpha.txt", help="alpha words")
    parser.add_argument('-l', '--log', help="logging output", action='store_true')
    parser.add_argument('-f', '--flower', required=True, help="petals (pistil first)")
    parser.add_argument('-b', '--bonus', required=True, help="bonus letter")
    parser.add_argument('-m', '--min', type=int, default=1, help="minium word length")
    parser.add_argument('-s', '--score', type=int, default=1, help="words above score")

    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler()

    if args.log:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    blossom: Blossom = Blossom(parser, logger)

    if args.flower:
        return blossom.doit(args.words, args.flower, args.bonus, args.min, args.score)

    return False

if __name__ == "__main__":
    if main():
        print("OK")
        sys.exit(0)
    print("ERR")
    sys.exit(1)

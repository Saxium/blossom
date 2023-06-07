#!/usr/bin/python3

import sys
import argparse
import os.path
import json
import logging

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import NamedStyle
from openpyxl.utils import get_column_letter

from typing import List, TextIO, Optional

class Blossom:
    """Blossom Online Word Game"""
    TMP_FILE = '/tmp/blossom.txt'

    def __init__(self, parser, logger = None) -> None:
        self.parser = parser
        self.logger = logger or logging.getLogger(__name__)
        self._petals = None
        self._bonus = None
        self._words = None

    def _match(self, word: str, pistil, petals) -> bool:
        if word.find(pistil) >= 0:
            x = set(word) - set(petals)
            y = set(pistil)
            if x == y:
                return True
        return False

    def _filter_words(self, alpha, pistil, petals):
        words = []
        if not os.path.exists(alpha):
            self.parser.error(f'No such file: {alpha}')
            return (False, None)

        alpha_file = open(alpha, encoding="utf-8", newline='')    # pylint: disable=consider-using-with
        if alpha_file is None:
            self.parser.error(f'Failed to open file: {alpha}')
            return (False, None)

        for line in alpha_file:
            word = line.strip()
            if self._match(word, pistil, petals):
                words.append(word)

        alpha_file.close()
        return (True, words)

    def _write_tmp(self, data):
        tmp_file = open(Blossom.TMP_FILE, 'w')
        if tmp_file is None:
            self.parser.error(f'Failed to write tmp file: {Blossom.TMP_FILE}')
            return False

        json_data = json.dumps(data)
        tmp_file.write(json_data)
        tmp_file.close()
        return True

    def prepare(self, flower: str, alpha: str = None) -> bool:
        """Create temp file with flower only"""
        if len(set(flower)) != 7:
            self.parser.error(f'Seven unique chars required for flower')
            return False

        if alpha is None:
            alpha = "words_alpha.txt"

        petals = list(flower)
        pistil = petals.pop(0)

        status, words = self._filter_words(alpha, pistil, petals)
        if status is False:
            return False

        data = {
            'flower' : flower,
            'pistil' : pistil,
            'petals' : petals,
            'words' : words
        }

        self.logger.info(data)

        return True


def main() -> bool:
    """Main to handle program parameters"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--alpha', help="alpha words")
    parser.add_argument('-l', '--log', help="logging output", action='store_true')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--flower', help="petals (pistil first)")
    group.add_argument('-b', '--bonus', help="bonus letter")
    group.add_argument('-s', '--show', help="show all words", action='store_true')

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
        return blossom.prepare(args.flower, args.alpha)
    if args.bonus:
        return blossom.bonus()
    if args.show:
        return blossom.show()
    return False

if __name__ == "__main__":
    if main():
        print("OK")
        sys.exit(0)
    print("ERR")
    sys.exit(1)

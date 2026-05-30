# blossom
Blossom Online Game Word Finder

## Installation

Create a local editable install and install the development/test extras:

```bash
python3 -m pip install -e '.[test]'
```

This installs the current package in editable mode and brings in:

- `pytest`
- `pylint`
- `mypy`
- `nox`

## Usage

Find all valid words for a flower:

- Provide a 7-letter flower with the pistil first.
- Use one of: bonus scoring, top score search, or just print words.

Examples:

- Show scores for a bonus letter:
	- `python3 blossom.py -f slurepg -b g -m 6 -s 15`
- Find the highest-scoring sequence:
	- `python3 blossom.py -f slurepg -t -m 6 -s 15`
- Just print all valid words:
	- `python3 blossom.py -f slurepg -p -m 6`

## Development

Run the nox sessions to test and lint the code:

```bash
nox -s pytest
nox -s pylint
nox -s mypy
```

## Notes

- Word lists are plain text files with one word per line.
- The pistil letter must appear in every word.
- Only letters from the flower are allowed in any word.

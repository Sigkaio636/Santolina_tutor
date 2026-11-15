"""A letter prior that needs no model: where the right answer tends to sit.

Kangaroo distractors are built around the right value, so when the five
options are distinct numbers the answer is rarely the smallest or the largest.
prior(problem) returns a probability for each letter A to E. The table comes
from data/prior.json (fitted on the training labels by `python3 -m
copilot.prior`); without that file the built-in rule is used: the median
value for numeric options, the fallback letter otherwise.
"""
import json
import os
import re

from .config import CONFIG

LETTERS = "ABCDE"
TABLE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "data", "prior.json")
_NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?")
_table = None


def number(text):
    """The single number in an option ("12", "3,5 cm", "3/4"), or None."""
    found = _NUMBER.findall(str(text).replace("−", "-").replace("–", "-"))
    if len(found) != 1:
        return None
    value = found[0].replace(",", ".")
    if "/" in value:
        top, bottom = value.split("/")
        return float(top) / float(bottom) if float(bottom) else None
    return float(value)


def value_order(options):
    """Letters sorted by option value, or None unless all five are distinct numbers."""
    if not options or any(letter not in options for letter in LETTERS):
        return None
    values = {letter: number(options[letter]) for letter in LETTERS}
    if None in values.values() or len(set(values.values())) < 5:
        return None
    return sorted(LETTERS, key=values.get)


def kind(problem):
    """Which row of the table a problem uses."""
    options = problem.get("options") or {}
    order = value_order(options)
    if order is None:
        return ("text" if options else "none"), None
    listed = "".join(order)
    return ("sorted" if listed in (LETTERS, LETTERS[::-1]) else "mixed"), order


def _default_table():
    fallback = CONFIG["FALLBACK_ANSWER"]
    by_letter = [0.6 if letter == fallback else 0.1 for letter in LETTERS]
    median = [0.1, 0.2, 0.4, 0.2, 0.1]
    return {"none": by_letter, "text": by_letter, "sorted": median, "mixed": median}


def table():
    global _table
    if _table is None:
        try:
            with open(TABLE_PATH, encoding="utf-8") as handle:
                _table = json.load(handle)
        except (OSError, ValueError):
            _table = _default_table()
    return _table


def prior(problem, weights=None):
    """Probability of each letter. Numeric rows are by value rank, the others by letter.

    Figure problems (text_only false) always get the fallback letter: no heuristic
    beat it there (docs/experiments/2026-11-txto-no-heuristics.md).
    """
    if problem.get("text_only") is False:
        fallback = CONFIG["FALLBACK_ANSWER"]
        return {letter: 1.0 if letter == fallback else 0.0 for letter in LETTERS}
    row_name, order = kind(problem)
    row = (weights or table())[row_name]
    if order is None:
        return dict(zip(LETTERS, row))
    return {letter: row[rank] for rank, letter in enumerate(order)}


def best(problem, weights=None):
    probabilities = prior(problem, weights)
    return max(LETTERS, key=lambda letter: (probabilities[letter], letter == CONFIG["FALLBACK_ANSWER"]))


def fit(problems, smoothing=2.0):
    """Count where the label falls, per row, with add-`smoothing` counts."""
    counts = {name: [smoothing] * 5 for name in ("none", "text", "sorted", "mixed")}
    for problem in problems:
        row_name, order = kind(problem)
        position = (order or LETTERS).index(problem["label"])
        counts[row_name][position] += 1
    return {name: [round(c / sum(row), 4) for c in row] for name, row in counts.items()}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fit the letter prior on the training labels.")
    parser.add_argument("--input", default="data/train.jsonl")
    parser.add_argument("--output", default=TABLE_PATH)
    args = parser.parse_args()
    with open(args.input, encoding="utf-8") as handle:
        problems = [json.loads(line) for line in handle if line.strip()]
    seen, unique = set(), []
    for problem in problems:  # one vote per problem: prefer the row with options
        if problem["id"] not in seen and problem["language"] == "eng":
            seen.add(problem["id"])
            unique.append(problem)
    weights = fit(unique)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(weights, handle, indent=1)
    print(f"Fitted on {len(unique)} problems, wrote {args.output}")
    for name, row in weights.items():
        print(f"  {name:7s}", row)


if __name__ == "__main__":
    main()

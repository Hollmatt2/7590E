"""Measuring automatic identification against CUAD's expert labels (brief, section 6.2).

For each category, two numbers:
- recall: of the clauses the experts labeled, how many the system flagged ("how often it finds what is there")
- false-flag rate: of the flags the system raised, how many matched no labeled clause ("how often it
  flags what is not there")
A flag matches a labeled clause when their character ranges overlap in the contract text.
"""
import random
import re
from collections import Counter
from dataclasses import dataclass, field

from .cuad import load_contracts
from .reading import split_into_clauses

EXAMPLES_KEPT = 3  # misses and wrong flags kept per category, for the report


@dataclass
class CategoryScore:
    labeled: int = 0  # clauses the experts labeled
    found: int = 0  # of those, how many the system flagged
    raised: int = 0  # flags the system raised
    wrong: int = 0  # of those, how many matched no labeled clause
    misses: list = field(default_factory=list)
    wrong_flags: list = field(default_factory=list)

    @property
    def recall(self):
        return self.found / self.labeled if self.labeled else None

    @property
    def false_flag_rate(self):
        return self.wrong / self.raised if self.raised else None


def locate(words, text):
    """The character range of `words` in `text`, allowing any spacing between the words, or None."""
    pieces = words.split()
    match = re.search(r"\s+".join(re.escape(piece) for piece in pieces), text) if pieces else None
    return match.span() if match else None


def overlaps(a, b):
    return a[0] < b[1] and b[0] < a[1]


def score_contract(title, text, labels, predictions, scores):
    """Add one contract to the running scores.

    labels: {category: [(start, end, text), ...]}; predictions: [(category, words), ...];
    scores: {category: CategoryScore} for the categories being measured.
    """
    for category, score in scores.items():
        labeled = labels.get(category, [])
        predicted = [(locate(words, text), words) for predicted_category, words in predictions if predicted_category == category]

        score.labeled += len(labeled)
        for start, end, label_text in labeled:
            if any(span and overlaps(span, (start, end)) for span, _ in predicted):
                score.found += 1
            elif len(score.misses) < EXAMPLES_KEPT:
                score.misses.append((title, label_text))

        score.raised += len(predicted)
        for span, words in predicted:
            if not (span and any(overlaps(span, (start, end)) for start, end, _ in labeled)):
                score.wrong += 1
                if len(score.wrong_flags) < EXAMPLES_KEPT:
                    score.wrong_flags.append((title, words))


def make_check_set(size, categories, minimum, seed=2026):
    """Choose `size` contract titles so each category has at least `minimum` contracts with a labeled clause.

    First it keeps taking the contract that helps the most categories still short of the minimum; then it
    fills the rest at random (with a fixed seed, so the choice can be repeated), so the set also holds
    ordinary contracts where most categories are absent.
    """
    remaining = sorted(load_contracts(), key=lambda contract: contract["title"])
    chosen, counts = [], Counter()
    while len(chosen) < size:
        short = [category for category in categories if counts[category] < minimum]
        best = max(remaining, key=lambda contract: sum(1 for category in short if contract["labels"].get(category)))
        if not short or not any(best["labels"].get(category) for category in short):
            break
        chosen.append(best)
        remaining.remove(best)
        counts.update(category for category in categories if best["labels"].get(category))
    random.Random(seed).shuffle(remaining)
    chosen += remaining[: size - len(chosen)]
    return [contract["title"] for contract in chosen]


def evaluate(titles, categories, finder):
    """Score `finder` (clause text -> [(category, words), ...]) on the given contracts."""
    # Some CUAD titles end in a space, and the check-set file is read with surrounding spaces removed,
    # so titles are compared without them.
    by_title = {contract["title"].strip(): contract for contract in load_contracts()}
    scores = {category: CategoryScore() for category in categories}
    for title in titles:
        contract = by_title[title.strip()]
        predictions = [finding for clause in split_into_clauses(contract["text"]) for finding in finder(clause)]
        score_contract(title, contract["text"], contract["labels"], predictions, scores)
    return scores

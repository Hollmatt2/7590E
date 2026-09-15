"""Helpers for the CUAD dataset (brief, section 7.1), downloaded into data/cuad/.

CUAD_v1.json holds every contract's text with 41 questions each, one per category, such as:
    'Highlight the parts (if any) of this contract related to "Cap On Liability" ... Details: <description>'
The answers are the clauses the expert annotators labeled for that category, with their
character positions in the contract text.
"""
import json
import re
from collections import Counter
from functools import cache

from django.conf import settings

CUAD_JSON = settings.BASE_DIR / "data" / "cuad" / "CUAD_v1" / "CUAD_v1.json"
CATEGORY_IN_QUESTION = re.compile(r'related to "(.+?)"')


@cache
def raw_contracts():
    with CUAD_JSON.open() as f:
        return json.load(f)["data"]


@cache
def category_summary():
    """Return (number of contracts, {category: (contracts with a labeled clause, labeled clauses, description)})."""
    contracts = raw_contracts()
    with_clause, clauses, descriptions = Counter(), Counter(), {}
    for contract in contracts:
        for paragraph in contract["paragraphs"]:
            for question in paragraph["qas"]:
                category = CATEGORY_IN_QUESTION.search(question["question"]).group(1)
                descriptions.setdefault(category, question["question"].split("Details:", 1)[-1].strip())
                if question["answers"]:
                    with_clause[category] += 1
                    clauses[category] += len(question["answers"])
    summary = {category: (with_clause[category], clauses[category], descriptions[category]) for category in descriptions}
    return len(contracts), summary


@cache
def load_contracts():
    """Every CUAD contract as {"title", "text", "labels": {category: [(start, end, text), ...]}}.

    The (start, end) positions are character positions in "text". Treat the result as read-only.
    """
    contracts = []
    for item in raw_contracts():
        for number, paragraph in enumerate(item["paragraphs"]):
            labels = {}
            for question in paragraph["qas"]:
                category = CATEGORY_IN_QUESTION.search(question["question"]).group(1)
                spans = {
                    (answer["answer_start"], answer["answer_start"] + len(answer["text"]), answer["text"])
                    for answer in question["answers"]
                }
                labels[category] = sorted(spans)
            title = item["title"] if number == 0 else f"{item['title']} (part {number + 1})"
            contracts.append({"title": title, "text": paragraph["context"], "labels": labels})
    return contracts

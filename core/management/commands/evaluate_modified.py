"""Run automatic identification on the deliberately modified standard agreements (brief, section 6.3).

    python manage.py evaluate_modified

seed/modified_agreements/answer_key.csv has one row for each provision that IS present in a file,
with the words that show it. A playbook category not listed for a file counts as absent. For each
category, the report says how many of the files containing it were flagged, and how many files
without it were flagged anyway. CUAD is public and models have likely seen it; if scores drop here,
that is a finding, not a failure. The report is saved to docs/evaluation-modified-<date>.md.
"""
import csv
from collections import defaultdict
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.forms import squash
from core.reading import ReadError, extract_text, split_into_clauses
from core.rules import RULES, find_with_rules

FOLDER = settings.BASE_DIR / "seed" / "modified_agreements"
PLAYBOOK = settings.BASE_DIR / "seed" / "playbook.csv"


class Command(BaseCommand):
    help = "Score the text rules on the modified agreements listed in seed/modified_agreements/answer_key.csv."

    def handle(self, *args, **options):
        with (FOLDER / "answer_key.csv").open(newline="") as f:
            key = [row for row in csv.DictReader(f) if row["file"].strip() and not row["file"].startswith("#")]
        if not key:
            raise CommandError("answer_key.csv has no rows yet. See seed/modified_agreements/README.md.")
        with PLAYBOOK.open(newline="") as f:
            measured = [row["cuad_category"].strip() for row in csv.DictReader(f) if row["cuad_category"].strip() in RULES]

        present = defaultdict(dict)  # file -> {category: the words that show it}
        for row in key:
            present[row["file"].strip()][row["cuad_category"].strip()] = row["expected_text"]

        counts = {c: {"present": 0, "flagged": 0, "right_words": 0, "absent": 0, "flagged_anyway": 0} for c in measured}
        per_file = []
        for name in sorted(present):
            try:
                with (FOLDER / name).open("rb") as stream:
                    text = extract_text(stream, name)
            except (OSError, ReadError) as error:
                raise CommandError(f"{name}: {error}") from error
            flagged = defaultdict(list)
            for clause in split_into_clauses(text):
                for category, words in find_with_rules(clause, measured):
                    flagged[category].append(squash(words))
            for category in measured:
                count = counts[category]
                if category in present[name]:
                    count["present"] += 1
                    if flagged[category]:
                        count["flagged"] += 1
                        expected = squash(present[name][category])
                        if expected and any(expected in words or words in expected for words in flagged[category]):
                            count["right_words"] += 1
                else:
                    count["absent"] += 1
                    count["flagged_anyway"] += bool(flagged[category])
            per_file.append(f"- `{name}`: flagged {', '.join(sorted(flagged)) or 'nothing'}")

        rows = [
            "| Category | Files containing it | Flagged | Flagged at the right words | Files without it | Flagged anyway |",
            "|---|---|---|---|---|---|",
        ]
        rows += [
            f"| {category} | {c['present']} | {c['flagged']} | {c['right_words']} | {c['absent']} | {c['flagged_anyway']} |"
            for category, c in counts.items()
        ]
        report = [
            f"# Modified-agreement evaluation, {date.today().isoformat()}",
            "",
            f"{len(present)} deliberately modified standard agreements (brief, section 6.3), listed in "
            "`seed/modified_agreements/answer_key.csv`. Method: the text rules in `core/rules.py`.",
            "",
            *rows,
            "",
            "## Per file",
            *per_file,
        ]
        path = settings.BASE_DIR / "docs" / f"evaluation-modified-{date.today().isoformat()}.md"
        path.write_text("\n".join(report) + "\n")
        self.stdout.write("\n".join(rows))
        self.stdout.write(f"Saved {path.relative_to(settings.BASE_DIR)}")

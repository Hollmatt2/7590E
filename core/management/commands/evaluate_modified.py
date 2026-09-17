"""Run automatic identification on the deliberately modified standard agreements (brief, section 6.3).

    python manage.py evaluate_modified              # the text rules and the AI step
    python manage.py evaluate_modified --method rules   # just the text pass (free)

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
from core.ai_identify import AIUnavailable, find_with_ai
from core.rules import RULES, find_with_rules

FOLDER = settings.BASE_DIR / "seed" / "modified_agreements"
PLAYBOOK = settings.BASE_DIR / "seed" / "playbook.csv"


class Command(BaseCommand):
    help = "Score the text rules on the modified agreements listed in seed/modified_agreements/answer_key.csv."

    def add_arguments(self, parser):
        parser.add_argument("--method", choices=["rules", "ai", "both"], default="both")

    def handle(self, *args, **options):
        with (FOLDER / "answer_key.csv").open(newline="") as f:
            key = [row for row in csv.DictReader(f) if row["file"].strip() and not row["file"].startswith("#")]
        if not key:
            raise CommandError("answer_key.csv has no rows yet. See seed/modified_agreements/README.md.")
        with PLAYBOOK.open(newline="") as f:
            playbook = list(csv.DictReader(f))
        # The text pass covers the categories that have a rule; the AI step covers the categories the
        # playbook gives it. Together they are what the app would do to these agreements.
        rule_categories = [row["cuad_category"].strip() for row in playbook if row["cuad_category"].strip() in RULES]
        ai_rows = [row for row in playbook if row.get("method", "").strip() == "ai"]
        ai_definitions = {row["name"].strip(): (row.get("definition") or row["name"]).strip() for row in ai_rows}
        ai_category = {row["name"].strip(): row["cuad_category"].strip() for row in ai_rows}
        methods = ["rules", "ai"] if options["method"] == "both" else [options["method"]]
        measured = sorted({c for c in rule_categories if "rules" in methods} | ({*ai_category.values()} if "ai" in methods else set()))

        present = defaultdict(dict)  # file -> {category: the words that show it}
        for row in key:
            present[row["file"].strip()][row["cuad_category"].strip()] = row["expected_text"]
        # Every modified agreement is scored, including any with no rows at all: a file where nothing
        # should be found is the sharpest test of false flags.
        files = sorted(path.name for path in FOLDER.glob("*.txt"))
        missing = [name for name in present if name not in files]
        if missing:
            raise CommandError(f"answer_key.csv names files that are not in {FOLDER}: {', '.join(missing)}")

        counts = {c: {"present": 0, "flagged": 0, "right_words": 0, "absent": 0, "flagged_anyway": 0} for c in measured}
        per_file, cost_note = [], ""
        for name in files:
            try:
                with (FOLDER / name).open("rb") as stream:
                    text = extract_text(stream, name)
            except (OSError, ReadError) as error:
                raise CommandError(f"{name}: {error}") from error
            clauses = split_into_clauses(text)
            flagged = defaultdict(list)
            if "rules" in methods:
                for clause in clauses:
                    for category, words in find_with_rules(clause, rule_categories):
                        flagged[category].append(squash(words))
            if "ai" in methods and ai_definitions:
                self.stdout.write(f"Asking the AI about {name}...")
                try:
                    findings, _ = find_with_ai(clauses, ai_definitions)
                except AIUnavailable as error:
                    raise CommandError(f"The AI step could not run: {error}") from error
                for finding in findings:
                    flagged[ai_category[finding.name]].append(squash(finding.quote))
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
            found_here = sorted(category for category, words in flagged.items() if words)
            expected_here = sorted(present.get(name, {}))
            per_file.append(
                f"- `{name}`: expected {', '.join(expected_here) or 'nothing'}; flagged "
                f"{', '.join(found_here) or 'nothing'}"
            )

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
            "`seed/modified_agreements/answer_key.csv`. Method: "
            + {"rules": "the text rules in `core/rules.py`.", "ai": "the AI step.",
               "both": "the text rules for the categories that have one, and the AI step for the categories the "
                       "playbook gives it, which is what the deployed app does."}[options["method"]],
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

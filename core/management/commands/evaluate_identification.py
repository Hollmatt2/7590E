"""Measure the text rules against CUAD's expert labels on the check set (brief, section 6.2).

    python manage.py evaluate_identification --make-check-set 40    # choose and save a check set
    python manage.py evaluate_identification                        # score the rules on it

The check set lives in seed/check_set.txt, one CUAD contract title per line, so every run uses the same
contracts. The rules run on CUAD's own contract text (the text the labels point into), split into clauses
by core/reading.py. The report is printed and saved to docs/evaluation-rules-<date>.md.
"""
import csv
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core import evaluation
from core.cuad import CUAD_JSON
from core.rules import RULES, find_with_rules

PLAYBOOK = settings.BASE_DIR / "seed" / "playbook.csv"
CHECK_SET = settings.BASE_DIR / "seed" / "check_set.txt"


def percent(value):
    return "—" if value is None else f"{value:.0%}"


class Command(BaseCommand):
    help = "Score the text rules against CUAD's labels on the check set in seed/check_set.txt."

    def add_arguments(self, parser):
        parser.add_argument("--make-check-set", type=int, metavar="SIZE", help="Choose a new check set of SIZE contracts.")
        parser.add_argument("--minimum", type=int, default=8, help="Contracts per category to aim for in a new check set.")

    def handle(self, *args, **options):
        if not CUAD_JSON.exists():
            raise CommandError(f"CUAD is not downloaded. Expected {CUAD_JSON}")
        with PLAYBOOK.open(newline="") as f:
            categories = [row["cuad_category"].strip() for row in csv.DictReader(f)]

        if options["make_check_set"]:
            size, minimum = options["make_check_set"], options["minimum"]
            titles = evaluation.make_check_set(size, categories, minimum)
            CHECK_SET.write_text(
                f"# CUAD check set, made by: python manage.py evaluate_identification --make-check-set {size} --minimum {minimum}\n"
                f"# Contracts were picked until each playbook category had {minimum} contracts with a labeled clause,\n"
                "# then the rest at random (seed 2026). One contract title per line; lines starting with # are ignored.\n"
                + "\n".join(titles) + "\n"
            )
            self.stdout.write(f"Saved {len(titles)} contracts to seed/check_set.txt\n")
        if not CHECK_SET.exists():
            raise CommandError("No check set yet. Run with --make-check-set 40 first.")
        titles = [line.strip() for line in CHECK_SET.read_text().splitlines() if line.strip() and not line.startswith("#")]

        measured = [category for category in categories if category in RULES]
        scores = evaluation.evaluate(titles, measured, lambda clause: find_with_rules(clause, measured))

        header = "| Category | Labeled clauses | Found | Recall | Flags raised | Wrong | False-flag rate |"
        rows = [header, "|---|---|---|---|---|---|---|"]
        for category, score in scores.items():
            rows.append(
                f"| {category} | {score.labeled} | {score.found} | {percent(score.recall)} | "
                f"{score.raised} | {score.wrong} | {percent(score.false_flag_rate)} |"
            )
        unmeasured = [category for category in categories if category not in RULES]

        report = [
            f"# Text-rule evaluation, {date.today().isoformat()}",
            "",
            f"Check set: {len(titles)} CUAD contracts, listed in `seed/check_set.txt`. Method: the text rules in "
            "`core/rules.py`, run on CUAD's own contract text split into clauses by `core/reading.py`. A flag counts "
            "as correct when it overlaps a clause the experts labeled for that category.",
            "",
            "- **Recall**: of the labeled clauses, the share the rules flagged.",
            "- **False-flag rate**: of the flags raised, the share that matched no labeled clause.",
            "",
            *rows,
            "",
            f"No text rule (left for the AI model or a person): {', '.join(unmeasured) or 'none'}.",
            "",
            "The rules were written before this check set was chosen. Re-scoring a changed rule on the same "
            "contracts overstates how well it works.",
            "",
            "## Examples",
        ]
        for category, score in scores.items():
            report += ["", f"### {category}", "", "Missed (labeled, not flagged):"]
            report += [f"- *{title[:60]}*: {' '.join(text.split())[:240]}" for title, text in score.misses] or ["- none"]
            report += ["", "Wrong flags (flagged, not labeled):"]
            report += [f"- *{title[:60]}*: {' '.join(text.split())[:240]}" for title, text in score.wrong_flags] or ["- none"]

        path = settings.BASE_DIR / "docs" / f"evaluation-rules-{date.today().isoformat()}.md"
        path.write_text("\n".join(report) + "\n")
        self.stdout.write("\n".join(rows))
        self.stdout.write(f"\nNo text rule: {', '.join(unmeasured) or 'none'}")
        self.stdout.write(f"Saved {path.relative_to(settings.BASE_DIR)}")

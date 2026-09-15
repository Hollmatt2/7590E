"""Measure automatic identification against CUAD's expert labels on the check set (brief, section 6.2).

    python manage.py evaluate_identification --make-check-set 40              # choose and save a check set
    python manage.py evaluate_identification                                  # score the text rules
    python manage.py evaluate_identification --method ai --limit 2 --yes      # try the AI on 2 contracts
    python manage.py evaluate_identification --method ai --yes                # the AI on the whole check set
    python manage.py evaluate_identification --method ai --reuse data/evaluations/ai-<date>.json

The check set lives in seed/check_set.txt, one CUAD contract title per line. Contracts are split into
clauses by core/reading.py, exactly as in the app. The AI method costs money: it prints an estimate and
runs only with --yes, and it saves every answer in data/evaluations/ so scores can be recomputed with
--reuse without paying again. Reports go to docs/evaluation-<method>-<date>.md.
"""
import csv
import json
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core import evaluation
from core.ai_identify import AIUnavailable, find_with_ai
from core.cuad import CUAD_JSON
from core.rules import RULES, find_with_rules

PLAYBOOK = settings.BASE_DIR / "seed" / "playbook.csv"
CHECK_SET = settings.BASE_DIR / "seed" / "check_set.txt"
SAVED = settings.BASE_DIR / "data" / "evaluations"
THRESHOLDS = [0.5, 0.7, 0.9]  # AI confidence levels to report, for the threshold note (section 6.4)
# Claude Opus 5 prices, dollars per million tokens: input, cache write, cache read, output.
PRICES = {"input": 5.00, "cache_write": 6.25, "cache_read": 0.50, "output": 25.00}


def percent(value):
    return "—" if value is None else f"{value:.0%}"


def dollars(usage):
    return (
        usage["input"] * PRICES["input"] + usage["cache_write"] * PRICES["cache_write"]
        + usage["cache_read"] * PRICES["cache_read"] + usage["output"] * PRICES["output"]
    ) / 1_000_000


class Command(BaseCommand):
    help = "Score the text rules or the AI step against CUAD's labels on the check set in seed/check_set.txt."

    def add_arguments(self, parser):
        parser.add_argument("--method", choices=["rules", "ai"], default="rules")
        parser.add_argument("--make-check-set", type=int, metavar="SIZE", help="Choose a new check set of SIZE contracts.")
        parser.add_argument("--minimum", type=int, default=8, help="Contracts per category to aim for in a new check set.")
        parser.add_argument("--limit", type=int, help="Use only the first N contracts of the check set.")
        parser.add_argument("--reuse", help="Score AI answers saved by an earlier run instead of asking again.")
        parser.add_argument("--yes", action="store_true", help="Confirm spending money on the AI method.")

    def handle(self, *args, **options):
        if not CUAD_JSON.exists():
            raise CommandError(f"CUAD is not downloaded. Expected {CUAD_JSON}")
        with PLAYBOOK.open(newline="") as f:
            playbook = [row for row in csv.DictReader(f)]
        categories = [row["cuad_category"].strip() for row in playbook]

        if options["make_check_set"]:
            self.make_check_set(options["make_check_set"], options["minimum"], categories)
        if not CHECK_SET.exists():
            raise CommandError("No check set yet. Run with --make-check-set 40 first.")
        titles = [line.strip() for line in CHECK_SET.read_text().splitlines() if line.strip() and not line.startswith("#")]
        titles = titles[: options["limit"]] if options["limit"] else titles

        if options["method"] == "rules":
            measured = [category for category in categories if category in RULES]

            def finder(clauses):
                return [(category, words, None) for clause in clauses for category, words in find_with_rules(clause, measured)]

            predictions, usage = evaluation.predict(titles, finder), None
        else:
            measured = categories
            predictions, usage = self.ai_predictions(titles, playbook, options)

        self.report(options["method"], predictions, measured, categories, usage)

    def make_check_set(self, size, minimum, categories):
        titles = evaluation.make_check_set(size, categories, minimum)
        CHECK_SET.write_text(
            f"# CUAD check set, made by: python manage.py evaluate_identification --make-check-set {size} --minimum {minimum}\n"
            f"# Contracts were picked until each playbook category had {minimum} contracts with a labeled clause,\n"
            "# then the rest at random (seed 2026). One contract title per line; lines starting with # are ignored.\n"
            + "\n".join(titles) + "\n"
        )
        self.stdout.write(f"Saved {len(titles)} contracts to seed/check_set.txt\n")

    def ai_predictions(self, titles, playbook, options):
        """Ask the AI about each contract (or load saved answers), saving progress as it goes."""
        if options["reuse"]:
            saved = json.loads((settings.BASE_DIR / options["reuse"]).read_text())
            predictions = {title: [tuple(p) for p in found] for title, found in saved["predictions"].items() if title in titles}
            return predictions, saved["usage"]

        definitions = {row["name"].strip(): row["definition"].strip() or row["name"].strip() for row in playbook}
        category_of = {row["name"].strip(): row["cuad_category"].strip() for row in playbook}
        by_title = evaluation.contracts_by_title()
        characters = sum(len(by_title[title]["text"]) for title in titles)
        estimate = dollars({"input": characters / 4 + 2000 * len(titles), "cache_write": 0, "cache_read": 0,
                            "output": 4000 * len(titles)})
        self.stdout.write(f"{len(titles)} contracts with {settings.AI_MODEL}: estimated cost about ${estimate:.2f} "
                          "(a rough guess; the model's thinking can add more).")
        if not options["yes"]:
            raise CommandError("Nothing was sent. Run again with --yes to spend the money.")

        SAVED.mkdir(parents=True, exist_ok=True)
        path = SAVED / f"ai-{date.today().isoformat()}.json"
        usage = {"input": 0, "cache_write": 0, "cache_read": 0, "output": 0}
        record = {"model": settings.AI_MODEL, "predictions": {}, "usage": usage}

        def finder(clauses):
            try:
                findings, used = find_with_ai(clauses, definitions)
            except AIUnavailable as error:
                raise CommandError(f"The AI step could not run: {error} Answers so far are in {path}.") from error
            usage["input"] += used.input_tokens
            usage["cache_write"] += used.cache_creation_input_tokens or 0
            usage["cache_read"] += used.cache_read_input_tokens or 0
            usage["output"] += used.output_tokens
            return [(category_of[f.name], f.quote, f.confidence) for f in findings]

        def save(title, found):
            record["predictions"][title] = found
            path.write_text(json.dumps(record, indent=1))
            self.stdout.write(f"  {len(record['predictions'])}/{len(titles)} {title[:60]}: {len(found)} findings")

        predictions = evaluation.predict(titles, finder, on_contract=save)
        self.stdout.write(f"Answers saved to {path.relative_to(settings.BASE_DIR)}")
        return predictions, usage

    def report(self, method, predictions, measured, categories, usage):
        scores = evaluation.score(predictions, measured)
        header = "| Category | Labeled clauses | Found | Recall | Flags raised | Wrong | False-flag rate |"
        rows = [header, "|---|---|---|---|---|---|---|"]
        for category, s in scores.items():
            rows.append(f"| {category} | {s.labeled} | {s.found} | {percent(s.recall)} | {s.raised} | {s.wrong} | "
                        f"{percent(s.false_flag_rate)} |")

        name = "Text-rule" if method == "rules" else "AI"
        report = [
            f"# {name} evaluation, {date.today().isoformat()}",
            "",
            f"Check set: {len(predictions)} CUAD contracts from `seed/check_set.txt`, split into clauses by "
            "`core/reading.py`. A flag counts as correct when it overlaps a clause the experts labeled for that "
            "category. Recall: of the labeled clauses, the share flagged. False-flag rate: of the flags raised, "
            "the share that matched no labeled clause.",
            "",
        ]
        if method == "rules":
            report.append("Method: the text rules in `core/rules.py`.")
        else:
            report.append(f"Method: the AI step in `core/ai_identify.py`, model `{settings.AI_MODEL}`, all findings. "
                          f"Tokens: {usage['input']:,} input, {usage['cache_write']:,} cache write, "
                          f"{usage['cache_read']:,} cache read, {usage['output']:,} output; cost about ${dollars(usage):.2f}.")
        report += ["", *rows]

        if method == "ai":
            report += ["", "## At different confidence thresholds", "",
                       "Findings below the threshold are ignored. For the threshold note (brief, section 6.4).", ""]
            columns = " | ".join(f"Recall ≥{t} | False flags ≥{t}" for t in THRESHOLDS)
            report += [f"| Category | {columns} |", "|---" * (1 + 2 * len(THRESHOLDS)) + "|"]
            by_threshold = [evaluation.score(predictions, measured, minimum_confidence=t) for t in THRESHOLDS]
            for category in measured:
                cells = " | ".join(f"{percent(s[category].recall)} | {percent(s[category].false_flag_rate)}" for s in by_threshold)
                report.append(f"| {category} | {cells} |")

        unmeasured = [category for category in categories if category not in measured]
        if unmeasured:
            report += ["", f"Not measured (no text rule): {', '.join(unmeasured)}."]
        if method == "rules":
            report += ["", "The rules were written before this check set was chosen. Re-scoring a changed rule on "
                       "the same contracts overstates how well it works."]

        report += ["", "## Examples"]
        for category, s in scores.items():
            report += ["", f"### {category}", "", "Missed (labeled, not flagged):"]
            report += [f"- *{title[:60]}*: {' '.join(text.split())[:240]}" for title, text in s.misses] or ["- none"]
            report += ["", "Wrong flags (flagged, not labeled):"]
            report += [f"- *{title[:60]}*: {' '.join(text.split())[:240]}" for title, text in s.wrong_flags] or ["- none"]

        path = settings.BASE_DIR / "docs" / f"evaluation-{method}-{date.today().isoformat()}.md"
        path.write_text("\n".join(report) + "\n")
        self.stdout.write("\n".join(rows))
        if usage:
            self.stdout.write(f"Cost of this run: about ${dollars(usage):.2f}")
        self.stdout.write(f"Saved {path.relative_to(settings.BASE_DIR)}")

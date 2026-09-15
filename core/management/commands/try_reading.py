"""Try the reading step on a folder of contracts, without saving anything, and report how it went.

    python manage.py try_reading data/cuad/CUAD_v1/full_contract_pdf --limit 30

Use it to decide whether reading PDFs is good enough, or whether to switch to the corpus's
plain-text files (brief, section 9: "set your own decision point for abandoning it").
With --compare-with, each file's text is compared with a reference .txt file of the same name.
"""
import statistics
import time
from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from core.reading import MAX_CLAUSE_CHARS, ReadError, extract_text, split_into_clauses

# A clause this close to the limit was almost certainly cut by length, not at a heading.
CUT_BY_LENGTH_CHARS = int(MAX_CLAUSE_CHARS * 0.95)


def words_matched(text, reference):
    """Share of the reference text's words that also appear in our text. 1.0 means nothing is missing."""
    ours, theirs = Counter(text.lower().split()), Counter(reference.lower().split())
    total = sum(theirs.values())
    return sum((ours & theirs).values()) / total if total else 0.0


class Command(BaseCommand):
    help = "Run text extraction and clause splitting on a folder of files and report the results."

    def add_arguments(self, parser):
        parser.add_argument("folder", help="Folder to search, subfolders included, for .pdf and .txt files.")
        parser.add_argument("--limit", type=int, default=30, help="How many files to try, spread across the folder.")
        parser.add_argument("--compare-with", help="Folder of reference .txt files with the same names.")

    def handle(self, *args, folder, limit, compare_with, **options):
        files = sorted(p for p in Path(folder).rglob("*") if p.suffix.lower() in {".pdf", ".txt"})
        if not files:
            raise CommandError(f"No .pdf or .txt files under {folder}")
        step = max(1, len(files) // limit)
        sample = files[::step][:limit]  # evenly spaced, so every agreement type gets a turn
        references = {p.stem: p for p in Path(compare_with).rglob("*.txt")} if compare_with else {}

        results, failures = [], 0
        for path in sample:
            started = time.perf_counter()
            try:
                with path.open("rb") as stream:
                    text = extract_text(stream, path.name)
                clauses = split_into_clauses(text)
            except ReadError as error:
                failures += 1
                self.stdout.write(self.style.WARNING(f"FAILED {path.name[:60]}: {error}"))
                continue
            seconds = time.perf_counter() - started
            cut = sum(1 for clause in clauses if len(clause) >= CUT_BY_LENGTH_CHARS)
            reference = references.get(path.stem)
            matched = words_matched(text, reference.read_text(errors="replace")) if reference else None
            results.append((seconds, len(clauses), cut, matched))
            line = f"ok  {path.name[:60]:60} {len(clauses):>4} clauses  {cut:>3} cut by length  {seconds:5.1f}s"
            if matched is not None:
                line += f"  words matched {matched:.0%}"
            self.stdout.write(line)

        self.stdout.write(f"\n{len(sample)} files tried, {failures} could not be read.")
        if not results:
            return
        seconds, counts, cuts, matched = zip(*results)
        self.stdout.write(
            f"Clauses per contract: median {statistics.median(counts):.0f}, fewest {min(counts)}, most {max(counts)}."
        )
        self.stdout.write(
            f"Clauses cut by the length limit because no heading was found: {sum(cuts)} of {sum(counts)} "
            f"({sum(cuts) / sum(counts):.0%})."
        )
        self.stdout.write(f"Seconds per contract: median {statistics.median(seconds):.1f}, slowest {max(seconds):.1f}.")
        compared = [m for m in matched if m is not None]
        if compared:
            self.stdout.write(
                f"Words matched against the reference text: median {statistics.median(compared):.0%}, "
                f"lowest {min(compared):.0%}."
            )

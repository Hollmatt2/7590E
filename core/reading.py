"""Reading a submitted agreement: pull the text out of the file, then split it into clauses.

This is workflow stage 2, ingestion and segmentation. The web request that saves an upload
never calls it. The process_agreements command does, separately (Change Notice 1).
"""
import logging
import re
from pathlib import Path

import pdfplumber
from django.db import transaction
from pdfminer.pdfdocument import PDFPasswordIncorrect
from pdfplumber.utils.exceptions import MalformedPDFException, PdfminerException

from .models import Agreement, Clause

logger = logging.getLogger(__name__)

MIN_TEXT_CHARS = 200  # less text than this and the file is almost certainly a scan
MIN_CLAUSE_CHARS = 40  # shorter pieces (a lone heading like "ARTICLE IV") join the clause after them
MAX_CLAUSE_CHARS = 3000  # longer pieces are cut at sentence ends so a reviewer can read them


class ReadError(Exception):
    """The file could not be turned into usable text. The message is shown to reviewers."""


def read_agreement(agreement_id):
    """Read one agreement that is waiting to be read.

    Returns the agreement with its new status, or None if it was not waiting (for example,
    because another worker already took it).
    """
    # Claim the agreement by switching it from "Submitted" to "Reading document" in one database step.
    # If two workers try at once, only one update changes the row, so only one of them reads the file.
    claimed = Agreement.objects.filter(pk=agreement_id, status=Agreement.Status.SUBMITTED).update(
        status=Agreement.Status.PROCESSING
    )
    if not claimed:
        return None
    agreement = Agreement.objects.get(pk=agreement_id)

    try:
        with agreement.document.open("rb") as stream:
            text = extract_text(stream, agreement.document.name)
        clauses = split_into_clauses(text)
    except ReadError as error:
        return mark_failed(agreement, str(error))
    except Exception as error:
        # A bug, or a kind of file nobody anticipated. Record it rather than leave the agreement
        # stuck at "Reading document" forever. The worker's log has the full details.
        logger.exception("Unexpected error reading agreement %s", agreement.pk)
        return mark_failed(agreement, f"Unexpected error while reading the file ({error.__class__.__name__}).")

    # Save the clauses and the new status together: either all of it is saved, or none of it.
    with transaction.atomic():
        agreement.clauses.all().delete()
        Clause.objects.bulk_create(
            Clause(agreement=agreement, position=number, text=clause_text)
            for number, clause_text in enumerate(clauses, start=1)
        )
        agreement.extracted_text = text
        agreement.read_error = ""
        agreement.status = Agreement.Status.AWAITING_IDENTIFICATION
        agreement.save(update_fields=["extracted_text", "read_error", "status"])
    return agreement


def mark_failed(agreement, reason):
    agreement.status = Agreement.Status.READ_FAILED
    agreement.read_error = reason
    agreement.save(update_fields=["status", "read_error"])
    return agreement


# Step 1: get the text out of the file

def extract_text(stream, filename):
    """Return the plain text of a PDF or .txt file. Raise ReadError when there is no usable text."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        raw = stream.read()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")  # older files; latin-1 accepts every byte, so this cannot fail
    elif suffix == ".pdf":
        try:
            with pdfplumber.open(stream) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except PDFPasswordIncorrect as error:
            raise ReadError("The PDF is password-protected.") from error
        except (PdfminerException, MalformedPDFException) as error:
            raise ReadError("The PDF is damaged and could not be opened.") from error
    else:
        raise ReadError(f"Files ending in {suffix or '(nothing)'} cannot be read.")

    if len(text.strip()) < MIN_TEXT_CHARS:
        # A scanned PDF is a picture of the pages, so there is little or no text to extract.
        raise ReadError("Almost no text was found. The file may be a scan, which this system cannot read yet.")
    return text


# Step 2: split the text into clauses

# A line that is only a page number: "3", "- 3 -", "Page 3", "Page 3 of 12".
PAGE_NUMBER = re.compile(r"^(?:page\s+)?-?\s*\d{1,3}\s*-?(?:\s+of\s+\d{1,3})?$", re.IGNORECASE)
# Lines that usually begin a new section.
NUMBERED_HEADING = re.compile(r"^\d{1,2}\.(?:\d{1,2}\.?)*(?:\s+\S|(?=[A-Z]))")  # "1. Term", "12.3 Fees", "1.DGT shall"
LETTERED_HEADING = re.compile(r"^(?:[IVXLC]{1,6}|[A-Z])\.\s+[A-Z]")  # "IV. FEES", "B. Late payments"
NAMED_HEADING = re.compile(r"^(?:ARTICLE|SECTION)\s+(?:[IVXLC]+|\d+)\b", re.IGNORECASE)  # "ARTICLE IV", "Section 5"
# A run of capitals, alone on its line or ending in a full stop: "INDEMNIFICATION", "DUTIES. The Company..."
CAPS_HEADING = re.compile(r"^[A-Z][A-Z0-9 ,&'()/\-]{3,60}(?:\.(?:\s|$)|$)")
# A table-of-contents entry: a numbered title with no full stop, ending in its page number,
# such as "4.2 Continuing Fees Payable to Us 4".
CONTENTS_ENTRY = re.compile(r"^\d{1,2}\.(?:\d{1,2}\.?)*\s+[^.]{3,70}\s\d{1,3}$")
SENTENCE_END = (".", ":", ";")
SENTENCE_BREAK = re.compile(r"(?<=[.;:])\s+(?=[A-Z(\d])")
MAX_TITLE_CHARS = 60  # a heading line this short is a title on its own, like "ARTICLE IV"


def looks_like_heading(line):
    if CONTENTS_ENTRY.match(line):
        return False  # keep a table of contents together instead of splitting it line by line
    return any(
        pattern.match(line) for pattern in (NUMBERED_HEADING, LETTERED_HEADING, NAMED_HEADING, CAPS_HEADING)
    )


def split_into_clauses(text):
    """Split an agreement's text into clauses, in document order."""
    lines = [line.strip() for line in text.replace("\xa0", " ").splitlines()]
    lines = [line for line in lines if not PAGE_NUMBER.match(line)]

    groups, current = [], []
    previous, previous_was_title = None, False
    for line in lines:
        # A wrapped sentence can also begin with "Section 9" or "2.1". So a line only starts a new
        # clause when the line before it ended a sentence, was blank, was a short title line such
        # as "ARTICLE IV" (followed directly by its first section), or was a table-of-contents entry.
        after_a_break = (
            previous is None
            or previous == ""
            or previous.endswith(SENTENCE_END)
            or previous_was_title
            or bool(CONTENTS_ENTRY.match(previous))
        )
        is_heading = bool(line) and after_a_break and looks_like_heading(line)
        if is_heading and current:
            groups.append(current)
            current = []
        if line or current:
            current.append(line)
        previous, previous_was_title = line, is_heading and len(line) <= MAX_TITLE_CHARS
    if current:
        groups.append(current)
    clauses = [tidy("\n".join(group)) for group in groups]

    if len(clauses) < 3:
        # Hardly any headings were found, so fall back to paragraphs separated by blank lines.
        clauses = [tidy(part) for part in re.split(r"\n\s*\n", "\n".join(lines))]

    clauses = merge_short([clause for clause in clauses if clause])
    return [piece for clause in clauses for piece in split_long(clause)]


def tidy(text):
    """Trim the ends and collapse runs of blank lines into one."""
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def merge_short(clauses):
    """Join any piece shorter than MIN_CLAUSE_CHARS onto the clause after it."""
    merged, carry = [], ""
    for clause in clauses:
        clause = f"{carry}\n{clause}" if carry else clause
        if len(clause) < MIN_CLAUSE_CHARS:
            carry = clause
        else:
            merged.append(clause)
            carry = ""
    if carry:  # a short piece at the very end joins the clause before it
        if merged:
            merged[-1] = f"{merged[-1]}\n{carry}"
        else:
            merged.append(carry)
    return merged


def split_long(clause):
    """Cut a clause longer than MAX_CLAUSE_CHARS into pieces, at sentence ends where possible."""
    if len(clause) <= MAX_CLAUSE_CHARS:
        return [clause]
    pieces, current = [], ""
    for sentence in SENTENCE_BREAK.split(clause):
        if current and len(current) + 1 + len(sentence) > MAX_CLAUSE_CHARS:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}" if current else sentence
    pieces.append(current)

    # A single sentence can still be over the limit. Cut it at the last space before the limit.
    result = []
    for piece in pieces:
        while len(piece) > MAX_CLAUSE_CHARS:
            cut = piece.rfind(" ", 0, MAX_CLAUSE_CHARS)
            if cut <= 0:
                cut = MAX_CLAUSE_CHARS
            result.append(piece[:cut].strip())
            piece = piece[cut:].strip()
        if piece:
            result.append(piece)
    return result

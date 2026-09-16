# Study guide 2: reading, identification, review rules and evaluation

The second half of the code: everything that happens away from the web pages. Same purpose as guide 1
(brief §12.2).

## How to use this

Paste this whole file into a chat with Claude and say:

> Quiz me on this. Ask one question at a time about what a piece of code does, why it is built that way,
> and what happens if the input is wrong. Start easy and get harder. After each answer, tell me what I got
> right, what I missed, and the short correct answer. I am new to coding, so keep the language plain.

---

# core/reading.py — turning a file into clauses

This is workflow stage 2, ingestion and segmentation. The website never calls it; the worker does.

```python
class ReadError(Exception):
    """The file could not be turned into usable text. The message is shown to reviewers."""
```
A custom error type. Raising it means "this file cannot be read, and here is a sentence a reviewer can act
on", as opposed to a bug.

```python
def read_agreement(agreement_id):
    claimed = Agreement.objects.filter(pk=agreement_id, status=Agreement.Status.SUBMITTED).update(
        status=Agreement.Status.PROCESSING)
    if not claimed:
        return None
```
**The most important five lines in the file.** This is one database instruction: "change this row to Reading
document, but only if it is still Submitted". The database guarantees only one worker can win, and `update`
returns how many rows changed. If two workers start at once, the loser gets 0 and stops. Without this, both
would read the same file and create duplicate clauses.

```python
    try:
        with agreement.document.open("rb") as stream:
            text = extract_text(stream, agreement.document.name)
        clauses = split_into_clauses(text)
    except ReadError as error:
        return mark_failed(agreement, str(error))
    except Exception as error:
        logger.exception(...)
        return mark_failed(agreement, f"Unexpected error while reading the file ({error.__class__.__name__}).")
```
`"rb"` means read the raw bytes, not text. Two nets: a known problem (a scan, a damaged PDF) gets a plain
explanation; anything unexpected is recorded too, with the details in the worker's log, so a bad file can
never leave an agreement stuck at "Reading document" forever.

```python
    with transaction.atomic():
        agreement.clauses.all().delete()
        Clause.objects.bulk_create(Clause(agreement=agreement, position=number, text=clause_text)
                                   for number, clause_text in enumerate(clauses, start=1))
        agreement.extracted_text = text; agreement.read_error = ""
        agreement.status = Agreement.Status.AWAITING_IDENTIFICATION
        agreement.save(update_fields=[...])
```
`transaction.atomic()` means all of this is saved, or none of it: no agreement ever ends up marked ready with
half its clauses. `bulk_create` writes all clauses in one instruction instead of one at a time.
`enumerate(..., start=1)` numbers them from 1.

```python
def extract_text(stream, filename):
    if suffix == ".txt":
        try: text = raw.decode("utf-8-sig")
        except UnicodeDecodeError: text = raw.decode("latin-1")
    elif suffix == ".pdf":
        try:
            with pdfplumber.open(stream) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except PDFPasswordIncorrect: raise ReadError("The PDF is password-protected.")
        except (PdfminerException, MalformedPDFException): raise ReadError("The PDF is damaged...")
    if len(text.strip()) < MIN_TEXT_CHARS:
        raise ReadError("Almost no text was found. The file may be a scan...")
```
Text files are usually UTF-8; if that fails, latin-1 accepts any byte, so reading never crashes on an old
file. `page.extract_text() or ""` guards against a page with no text returning nothing. **Bad input:**
password-protected, damaged, wrong type, or a scan (a picture of text, which has almost no characters) each
produce a specific message.

## Splitting text into clauses

```python
PAGE_NUMBER = re.compile(r"^(?:page\s+)?-?\s*\d{1,3}\s*-?(?:\s+of\s+\d{1,3})?$", re.IGNORECASE)
NUMBERED_HEADING = re.compile(r"^\d{1,2}\.(?:\d{1,2}\.?)*(?:\s+\S|(?=[A-Z]))")
LETTERED_HEADING  = re.compile(r"^(?:[IVXLC]{1,6}|[A-Z])\.\s+[A-Z]")
NAMED_HEADING     = re.compile(r"^(?:ARTICLE|SECTION)\s+(?:[IVXLC]+|\d+)\b", re.IGNORECASE)
CAPS_HEADING      = re.compile(r"^[A-Z][A-Z0-9 ,&'()/\-]{3,60}(?:\.(?:\s|$)|$)")
CONTENTS_ENTRY    = re.compile(r"^\d{1,2}\.(?:\d{1,2}\.?)*\s+[^.]{3,70}\s\d{1,3}$")
```
These are regular expressions: patterns for matching text. In plain words they mean:
- a line that is only a page number ("3", "- 3 -", "Page 2 of 9")
- a numbered heading ("1. Term", "12.3 Fees", and "1.DGT shall" with no space)
- a lettered or roman heading ("IV. FEES", "B. Late payments")
- "ARTICLE IV" or "Section 5"
- a line of capitals, alone or ending in a full stop ("INDEMNIFICATION", "DUTIES.")
- a table-of-contents line: a numbered title with no full stop, ending in its page number

```python
        after_a_break = (previous is None or previous == "" or previous.endswith(SENTENCE_END)
                         or previous_was_title or bool(CONTENTS_ENTRY.match(previous)))
        is_heading = bool(line) and after_a_break and looks_like_heading(line)
```
**Why a heading needs the line before it.** A wrapped sentence can start with "Section 9 of this Agreement",
which looks exactly like a heading. So a line only starts a new clause when the line before it finished a
sentence, was blank, was a short title, or was a contents line. This was a real bug: a test caught it.

```python
    if len(clauses) < 3:
        clauses = [tidy(part) for part in re.split(r"\n\s*\n", "\n".join(lines))]
```
If a contract has almost no headings the rules find, fall back to paragraphs separated by blank lines.

`merge_short` joins any piece under 40 characters onto the next one, so a bare "ARTICLE IV" is not a clause of
its own. `split_long` cuts anything over 3,000 characters at sentence ends, and if a single sentence is still
too long, at the last space before the limit, so no clause is unreadably large. Measured on 30 CUAD contracts:
a median of 37 clauses each, and 5% cut by length rather than at a heading.

---

# core/rules.py — the text rules

```python
RULES = {"Governing Law": r"\b(?:governed\s+by|construed\s+(?:in\s+accordance\s+with|under)|governing\s+law)\b", ...}
COMPILED = {category: re.compile(pattern, re.IGNORECASE) for category, pattern in RULES.items()}
```
One pattern per CUAD category, for the eight provisions a pattern can find. `\b` means a word boundary, so
"assign" does not match inside "reassignment". Compiling once at import is faster than compiling per contract.

```python
def sentence_around(text, start, end):
    earlier = [m.end() for m in SENTENCE_END.finditer(text, 0, start)]
    begin = earlier[-1] if earlier else 0
    later = SENTENCE_END.search(text, end)
    return text[begin:(later.end() if later else len(text))].strip()
```
When a pattern matches, the finding is the whole sentence around it, not the matched fragment, so a reviewer
sees it in context. `SENTENCE_END` is a full stop or semicolon followed by a space, which is why "2.1" and
"U.S." do not count as sentence ends.

```python
        for match in pattern.finditer(text):
            sentence = sentence_around(text, *match.span())
            if sentence and sentence not in seen: seen.add(sentence); found.append((category, sentence))
```
Several matches in one sentence produce one finding, not three.

**Honesty point for the presentation:** measured against CUAD's expert labels on 40 contracts, these rules
find 32–80% of labeled clauses depending on the category, and 22–73% of their flags are wrong. No rule is
reliable on its own, which is the argument for the AI step.

---

# core/auto_identify.py — running the automatic methods

```python
    if agreement.status != Agreement.Status.AWAITING_IDENTIFICATION: return "skipped"
    if agreement.flags.exclude(source=Flag.Source.MANUAL).exists(): return "skipped"
```
Runs once per agreement, and only at the right stage, so a second run cannot double the findings.

```python
    by_category = {p.cuad_category: p for p in provisions
                   if p.method == Provision.Method.RULES and p.cuad_category in COMPILED}
```
Only provisions whose method is "rules" **and** that actually have a rule written. A provision set to "rules"
with no rule is simply not covered, and the agreement then waits for a person.

```python
        try:
            findings, _ = find_with_ai([c.text for c in clauses], {p.name: p.definition or p.name for p in ai_provisions})
        except AIUnavailable as error:
            logger.warning(...); note = f"AI unavailable: {error}"
        else:
            ... covered.update(...)
    every_method_ran = all(provision.pk in covered for provision in provisions)
    with transaction.atomic():
        Flag.objects.bulk_create(flags)
        if every_method_ran: agreement.status = Agreement.Status.IN_REVIEW; agreement.save(...)
```
The heart of the fallback the brief asks about (§5, "what happens when the AI service goes down"): if every
provision's method ran, the agreement goes straight to review; if anything could not run, it waits on the
manual screen with whatever was found already listed. Either way a person decides on every flag.

---

# core/ai_identify.py — the AI step

```python
INSTRUCTIONS = """You review vendor agreements for Calder Industrial Supply... report each passage where one
of the provisions listed below is present... category / clause / quote / confidence / reason..."""
```
The instructions sent with every request. They ask for the exact quote, forbid paraphrasing, say a heading or
cross-reference is not the provision itself, and say to identify only, never to judge whether a term is
acceptable (that is the brief's professional boundary, §2).

```python
def credentials_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY") or ... or (Path.home() / ".config" / "anthropic").exists())
```
Checked first, so a missing key gives a clear "AI unavailable" instead of an error from deep inside a library.

```python
def output_schema(names):
    finding = {"type": "object", "properties": {"category": {"type": "string", "enum": names}, "clause": {"type": "integer"},
               "quote": {"type": "string"}, "confidence": {"type": "number"}, "reason": {"type": "string"}},
               "required": [...], "additionalProperties": False}
```
A schema is a description of the shape the answer must take. The API guarantees the reply matches it, so the
code never has to cope with prose where it expected data. `enum` limits the category to the playbook's names.

```python
        if settings.AI_MODEL in MODELS_WITH_FALLBACKS:
            manager = client.beta.messages.stream(**request, betas=[FALLBACK_BETA], fallbacks="default")
        else:
            manager = client.messages.stream(**request)
```
On models that support it, a request Claude declines is retried automatically on another Claude model. Haiku
does not support that setting, so it is not sent. Streaming is used because contracts are long.

```python
    if message.stop_reason == "refusal": raise AIUnavailable("Claude declined to process this agreement.")
    if message.stop_reason == "max_tokens": raise AIUnavailable("The answer was cut off before it finished.")
```
**Bad output, handled:** a declined request and a truncated answer are both turned into "the AI is
unavailable", which sends the agreement to a person rather than saving half an answer.

```python
        position = int(item.get("clause", 0)) - 1
        if not (0 <= position < len(clauses) and quote in squashed[position]):
            position = next((index for index, text in enumerate(squashed) if quote in text), None)
            if position is None: dropped += 1; continue
```
**The check that matters.** Every quote must appear word for word somewhere in the agreement. If the model
puts the right quote under the wrong clause number, the code finds the clause that really contains it. If the
quote is nowhere, the finding is dropped and counted in the log. This enforces the brief's rule that nothing
may be shown that cannot be traced to source text, even when a model invents something.

```python
        confidence = min(max(float(item.get("confidence", 0)), 0.0), 1.0)
```
Clamps the score into 0–1, so a stray 1.7 cannot reach the database.

---

# core/review.py — the review rules

```python
STATUS_AFTER = {FlagDecision.Action.ACCEPT: Flag.Status.ACCEPTED, ...}

def record_decision(flag, user, action, reason):
    with transaction.atomic():
        decision = FlagDecision.objects.create(flag=flag, decided_by=user, action=action, reason=reason)
        flag.status = STATUS_AFTER[action]; flag.save(update_fields=["status"])
```
Two things saved together: a new decision row (the record) and the flag's current status (convenience). A
later decision adds another row; the earlier one stays.

```python
def allowed_outcomes(agreement):
    if agreement.status == ESCALATED: return [CLEARED, CLEARED_WITH_CONDITIONS]
    if agreement.flags.filter(status=Flag.Status.ESCALATED).exists(): return [ESCALATED]
    return [CLEARED, CLEARED_WITH_CONDITIONS, ESCALATED]
```
The rules in three lines: an escalated agreement is finished by the approver; one escalated finding forces the
whole agreement to be escalated; otherwise all three outcomes are available.

```python
def record_disposition(agreement, user, outcome, conditions=""):
    if undecided_count(agreement): raise ReviewError("Decide every finding before recording the outcome.")
    if outcome not in allowed_outcomes(agreement): raise ReviewError(...)
    with transaction.atomic():
        moved = Agreement.objects.filter(pk=agreement.pk, status=agreement.status).update(status=outcome)
        if not moved: raise ReviewError("Someone else recorded an outcome for this agreement first.")
        return Disposition.objects.create(...)
```
The same "change it only if it is still what I saw" trick as the reading worker, so two reviewers pressing the
button at the same moment cannot both record an outcome.

`audit_history` collects three kinds of event (findings marked by a person, decisions, outcomes) and sorts
them by time, which is what the History table on the agreement page shows.

---

# core/cuad.py and core/evaluation.py — measuring

```python
@cache
def load_contracts():
    ... labels[category] = sorted({(a["answer_start"], a["answer_start"] + len(a["text"]), a["text"]) for a in question["answers"]})
```
CUAD is 510 real contracts with lawyers' labels. Each label is a start and end position in the contract's
text. `@cache` keeps the parsed file in memory, since reading it takes a second or two.

```python
def locate(words, text):
    match = re.search(r"\s+".join(re.escape(piece) for piece in pieces), text)
    return match.span() if match else None
def overlaps(a, b): return a[0] < b[1] and b[0] < a[1]
```
To score a finding, the code has to know where it sits in the contract. The pattern allows any spacing between
the words. Two ranges overlap when each starts before the other ends.

```python
        score.labeled += len(labeled)
        for start, end, label_text in labeled:
            if any(span and overlaps(span, (start, end)) for span, _ in predicted): score.found += 1
        score.raised += len(predicted)
        for span, words in predicted:
            if not (span and any(...)): score.wrong += 1
```
The two numbers the brief requires (§6.2): of the clauses lawyers labeled, how many the system flagged
(recall), and of the flags raised, how many matched no labeled clause (the false-flag rate). Examples of both
are kept for the report, which answers the brief's question "what happened in the other 6%".

```python
def make_check_set(size, categories, minimum, seed=2026):
    ... keeps taking the contract that helps the most categories still short of the minimum ...
    random.Random(seed).shuffle(remaining); chosen += remaining[: size - len(chosen)]
```
Builds the 40-contract check set: enough examples of every category to measure, then ordinary contracts at
random so the set is not all positives. The fixed `seed` means the same random choice every time, so the
result can be repeated.

---

# The commands (`core/management/commands/`)

Each file is one command run with `python manage.py <name>`.

| Command | What it does |
|---|---|
| `seed_demo` | Demo logins, the playbook, sample contracts. Safe to run again; the deployed site runs it at every start. |
| `load_playbook` | Reads `seed/playbook.csv` into the playbook. Refuses an unknown severity or method. |
| `process_agreements [--watch]` | The worker: reads waiting agreements, then runs automatic identification. |
| `try_reading <folder>` | Tries reading a folder of contracts without saving, and reports clause counts and timing. |
| `count_categories` | Counts CUAD's labeled clauses per category. |
| `evaluate_identification` | Scores the rules, or the AI with `--method ai`, against CUAD's labels. Shows a cost estimate, needs `--yes`, saves the AI's answers so they can be re-scored for free. |
| `evaluate_modified` | Scores the rules on the deliberately modified standard contracts (§6.3). |

---

# The tests

`python manage.py test` runs 55 checks in about half a minute. They are the evidence that the rules above
actually hold:

- Intake: a past date, an oversized file and a Word file renamed to `.pdf` are all refused; submitting does
  not read the document.
- Permissions: a requester cannot open someone else's agreement or its file; a reviewer can.
- Reading: a real PDF is built inside the test, so no sample file is needed; a scan, a damaged PDF and a
  second read are all handled.
- Splitting: numbered, lettered and capitalised headings; page numbers removed; a table of contents kept
  together; a wrapped "Section 9" line not treated as a heading.
- The AI step: quotes that are not in the agreement are dropped, a wrong clause number is corrected, a
  confidence above 1 is clamped, and a missing key means "unavailable" without any request being sent.
- Review: a decision needs a reason; changing a decision keeps the first; the outcome waits for every finding;
  an escalated finding forces escalation; only the approver finishes an escalated agreement; nobody reviews
  their own submission; a finding with decisions cannot be deleted.

---

# The deployment files

- `start.sh` — what the server runs: apply database changes, gather static files, load demo data, then start
  the website and the reading worker side by side. `wait -n` stops the container if either one stops, so
  Railway restarts it.
- `Procfile` — tells Railway to run `start.sh`.
- `requirements.txt` — the exact versions of every Python package.

---

# Questions I should be able to answer

1. How does the worker make sure two copies never read the same file?
2. Why is a finding the whole sentence rather than the matched words?
3. What stops the AI from inventing a quote that is not in the contract?
4. What happens when the AI is switched off or its key is missing?
5. Why does one escalated finding escalate the whole agreement?
6. What are the two numbers reported per category, and why not a single accuracy figure?
7. Why does the check set include contracts that contain none of the categories?
8. What does `transaction.atomic()` protect against in `read_agreement`?

# Technical presentation: facts to build the slides from

About 10 minutes on the stack, the APIs, the tools, and the challenges (8/20 session). Srinivasan may open any
file and ask what it does, why it is built that way, and what happens with malformed input (brief §12.2);
`docs/code-walkthrough.md` covers every file. Numbers below are from real runs on 2026-09-14.

## What the system does
Intake, reading and clause splitting, identification, flags, review, outcome, record, reporting: the full
required workflow from Change Notice 1. Identification can be done by a person, by text rules, or by the AI
step, and a person decides on every finding.

## Stack and APIs
- Python 3.14, Django 6.1: server-rendered pages, Django's login and admin.
- SQLite locally, Postgres on Railway.
- pdfplumber for PDF text extraction.
- The Anthropic API with Claude Haiku 4.5 for the AI step (one setting switches to Opus 5), through Anthropic's
  Python library.
- Deployment: Railway, one service running gunicorn and the reading worker, with a volume for uploads.
- Code on GitHub: github.com/Hollmatt2/7590E.

## Architecture points worth showing
- Submitting only saves the file. A separate worker (`process_agreements`) reads it, so a big PDF never
  makes a page hang (Change Notice 1: submission and analysis in separate requests).
- The worker claims an agreement in one database step, so two workers never read the same file.
- Every finding points to its exact words. The manual form refuses words that are not in the clause, and
  AI quotes that are not word for word in the agreement are dropped (brief §5).
- Decisions and outcomes are only ever added, never edited, and a finding with decisions cannot be
  deleted: that is the audit record.
- If the AI is down or switched off, the agreement waits for a person on the manual screen (brief §5: "what
  happens when the AI service goes down").

## The AI step
- One request per agreement: the playbook definitions plus the numbered clauses.
- The answer must match a fixed JSON shape: provision, clause number, exact quote, confidence 0–1, reason.
- Haiku 4.5 costs about a fifth of Opus 5 per token; the evaluation shows whether its accuracy is enough.
- Low-confidence findings (below 0.5 for now) are marked and listed last; a person still decides.
- Evaluation prints a cost estimate, needs `--yes`, and saves the answers so scores can be recomputed for free.

## Numbers
- Reading: 30 of 30 CUAD PDFs read; median 98% of words match CUAD's text; median about 1 second per contract.
- Splitting: median 37 clauses per contract; 5% of clauses cut by length.
- Category counts across CUAD's 510 contracts (`docs/cuad-category-counts.md`): governing law in 86%,
  warranty duration in 15%. Calder's two stated problems (uncapped liability, renewal notice) are among the rarest.
- Text rules on a 40-contract check set: they find 32–80% of labeled clauses; 22–73% of their flags are wrong.
- AI step: not yet measured (needs the API key).

## Rules versus model (brief §9: the split "makes a strong technical presentation")
- Each playbook provision has a `method`: text rule or AI. For now: rules for the 8 categories that have one,
  the AI for the 4 that need judgment (cap on liability, uncapped liability, exclusivity, warranty duration).
- The evaluation can score both methods on the same contracts. Your decision to present: which categories
  keep a rule, which move to the AI, and why, using those numbers.

## Challenges
- PDF layouts: numbering styles the splitter missed (fixed: "1.DGT", "DUTIES.", tables of contents).
- Rules that match the words but not the meaning ("governed by" appears in unrelated sentences).
- The AI's confidence is its own estimate, so the threshold has to be checked against real results.
- Cost versus accuracy in the model choice (Haiku 4.5 or Opus 5).
- A solo team, and a lot of AI-written code to understand.

## Next
Measure the AI step, deploy, the modified-agreement test, usability sessions.

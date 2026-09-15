# Technical presentation: facts to build the slides from

About 10 minutes on the stack, the APIs, the tools, and the challenges (8/20 session). Srinivasan may open any
file and ask what it does, why it is built that way, and what happens with malformed input (brief §12.2);
`docs/code-walkthrough.md` covers every file. Numbers below are from real runs on 2026-09-14.

## What the system does
Intake, reading and clause splitting, identification, flags, review, outcome, record, reporting: the full
required workflow from Change Notice 1, working end to end with a person doing identification. Text rules
already add findings automatically; the AI step comes next and fills in the same findings.

## Stack
- Python 3.14, Django 6.1: server-rendered pages, Django's login and admin.
- SQLite locally, Postgres on Railway.
- pdfplumber for PDF text extraction.
- Deployment: Railway, one service running gunicorn and the reading worker, with a volume for uploads.

## Architecture points worth showing
- Submitting only saves the file. A separate worker (`process_agreements`) reads it, so a big PDF never
  makes a page hang (Change Notice 1: submission and analysis in separate requests).
- The worker claims an agreement in one database step, so two workers never read the same file.
- Every finding points to its exact words; the form refuses words that are not in the clause (brief §5).
- Decisions and outcomes are only ever added, never edited, and a finding with decisions cannot be
  deleted: that is the audit record.
- With automation switched off, the app still works with people doing identification (brief §5's
  architectural test).

## Numbers
- Reading: 30 of 30 CUAD PDFs read; median 98% of words match CUAD's text; median about 1 second per contract.
- Splitting: median 37 clauses per contract; 5% of clauses cut by length.
- Category counts across CUAD's 510 contracts (`docs/cuad-category-counts.md`): governing law in 86%,
  warranty duration in 15%. Calder's two stated problems (uncapped liability, renewal notice) are among the rarest.
- Text rules on a 40-contract check set: they find 32–80% of labeled clauses; 22–73% of their flags are wrong.

## Rules versus model (brief §9: the split "makes a strong technical presentation")
- Rules for 8 categories, measured. None is reliable alone.
- The 4 categories that need judgment (cap on liability, uncapped liability, exclusivity, warranty duration)
  have no rule.
- Your decision to present: which categories keep a rule, which go to the model, and why, using the numbers.

## Challenges
- PDF layouts: numbering styles the splitter missed (fixed: "1.DGT", "DUTIES.", tables of contents).
- Rules that match the words but not the meaning ("governed by" appears in unrelated sentences).
- The AI provider and key are not chosen yet.
- A solo team, and a lot of AI-written code to understand.

## Next
The AI step, deployment, the modified-agreement test, usability sessions.

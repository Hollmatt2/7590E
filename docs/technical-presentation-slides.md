# Technical presentation slides — 10 minutes, Thursday 2026-09-17, 6 pm

A draft to edit into your own words. One heading per slide, bullets to put on it, and a "say" line for what
you add out loud. Every number is from a real run; the source file is named so you can show it if asked.

---

## Slide 1 — Vendor Agreement Review Assistant

- Calder Industrial Supply (fictional client)
- Matt Holliday, solo team
- Live: web-production-48b18.up.railway.app
- Code: github.com/Hollmatt2/7590E

**Say:** It is deployed and working; everything in this deck is measured, not planned.

---

## Slide 2 — What it does

- A requester submits a contract with vendor, type, business unit and needed-by date
- The system reads it, splits it into clauses, and finds the playbook provisions
- Every finding carries the exact words that show it
- A reviewer accepts, dismisses or escalates each finding with a reason, then records the outcome
- It identifies provisions; it does not advise. A person decides everything.

**Say:** The client's problem is that 200 contracts a year get signed and only 40 reach legal. This picks
which 40, and shows why.

---

## Slide 3 — Stack and hosting, and why

- Python and Django: login, roles, admin screens and a database schema come built in, so the semester goes on
  the workflow rather than on plumbing
- Postgres database, and a storage volume for uploaded contracts
- pdfplumber to read PDFs
- Anthropic's API, Claude Haiku 4.5, for the AI step
- Hosted on Railway: deploys straight from GitHub, and gives the database and storage in the same place
- Everything the deployment needs is a setting, not code, so the same code runs on my laptop and in public

**Say:** Haiku is the small, cheap model. The whole 40-contract evaluation cost 88 cents.

---

## Slide 4 — What is running right now

- Running: intake, reading and clause splitting, text rules, the AI step, manual identification, review with
  reasons, outcomes, the audit record, reports, roles, four demo logins, demo contracts
- The document reading runs as a separate worker, not inside the web page
- 55 automated tests
- Not built yet: the modified-contract test (§6.3), the threshold note, usability sessions

**Say:** Submitting only saves the file. If reading happened inside the request, a big PDF would freeze the
page. That was Change Notice 1's warning and it shaped the design.

---

## Slide 5 — PDF ingestion: decided, with evidence

- Tried the reading step on 30 CUAD contracts: 30 of 30 read
- A median 98% of words matched CUAD's own text files, lowest 92%
- About 1 second per contract
- Decision: stay with PDFs. Plain text stays available as a fallback and is accepted by the upload form.
- Source: `docs/ingestion-trial-2026-09-14.txt`

**Say:** The brief warned that PDF extraction is where projects die, and asked for a decision point. This is it,
made on measurements in week 4 rather than in November.

---

## Slide 6 — The hard part: splitting a contract into clauses

- Contracts number sections in many ways: "1. Term", "12.3", "1.DGT shall", "ARTICLE IV", "DUTIES."
- A wrapped line beginning "Section 9 of this Agreement" is not a heading; the rule checks the line before it
- Tables of contents are kept whole rather than split into dozens of fragments
- Result: a median 37 clauses per contract, and 5% of clauses cut by length because no heading was found

**Say:** Each of those was a real failure I found by running the corpus, not a guess.

---

## Slide 7 — Category selection

- CUAD has 41 categories; the brief asks for 8 to 12, justified
- Two tests: does Calder's stated problem touch it, and are there enough labeled examples to measure it
- Counted every category across all 510 contracts: `docs/cuad-category-counts.md`
- Governing law appears in 86% of contracts; warranty duration in 15%
- Calder's two stated problems, uncapped liability and renewal notice periods, are among the rarest at 22%
- Indemnification, which the brief suggests, has no CUAD label at all, so it cannot be measured
- The check set of 40 contracts was built so every chosen category has at least 12 examples
- **Decision: ten categories.** Exclusivity and warranty duration are scoped out: Calder never raised either,
  and both measured worst (46% and 67% of flags wrong). They stay in the backlog, one row each to add back
- Severity is set, not left at medium: high only for the four provisions behind Calder's two stated failures,
  the liability pair and the renewal pair; low for governing law and audit rights
- Reasons per category: `docs/playbook-selection.md`

**Say:** I kept ten. Calder's own story decides what belongs in the playbook, and the corpus counts decide
whether I can prove anything about it. Both tests had to pass.

---

## Slide 8 — Text rules versus the model

| Category | Text rule | AI (Haiku) |
|---|---|---|
| Governing law | 80% found, 60% of flags wrong | 90% found, 5% wrong |
| Notice period to stop renewal | 47%, 27% | 88%, 24% |
| Auto-renewal | 67%, 48% | 86%, 25% |
| Assignment restriction | 50%, 40% | 62%, 9% |
| Insurance | 41%, 22% | 26%, 13% |

- Measured the same way on the same 40 contracts, against lawyers' labels
- Rules are fast and free but match words, not meaning: "governed by" turns up in unrelated sentences
- The model wins nearly everywhere; insurance is the one place the rule finds more
- **Decision: eight categories on the model, two on rules.** Insurance stays on a rule because it finds more
  and Calder fears a miss more than noise; audit rights stays because the two tie and the rule is free
- Each playbook entry carries its own method, so the split is a setting, not a rewrite
- Added today: an administrator can add keywords to any category without a developer. Tried it on uncapped
  liability and measured it: 0 of 20 labeled clauses found, every flag raised was wrong, so the keywords were
  removed. Those clauses are carve-outs written dozens of ways; there is no shared phrase to match

**Say:** The brief asked us to decide per category rather than route everything through a model. This is that
decision, with numbers behind it.

---

## Slide 9 — Confidence, and where it gets weak

- Every AI finding carries a confidence score and the exact quote; quotes that are not in the contract are dropped
- Weakest category kept: uncapped liability, 26% found with 75% of flags wrong. It stays because it is one of
  Calder's two stated problems; dropping it to improve the average would leave the client worse off
- Raising the bar to 0.9 confidence: governing law 90% found with no wrong flags, auto-renewal 71% with none,
  cap on liability's wrong flags fall from 28% to 4%
- Today the app marks findings below 0.5 as low confidence and lists them last; a person still decides
- Source: `docs/evaluation-ai-2026-09-17.md`

**Say:** Uncapped liability is one of the client's two stated problems and is where the system is weakest. That
is the number I would most want to improve, and the threshold note will argue where to set the bar.

---

## Slide 10 — Blockers and what is next

- Blockers: one-person team; the categories with few labeled examples are the ones the client cares most about;
  the model's confidence is its own estimate and still has to be checked against results; neither method is
  reliable on uncapped liability, and a word list does not fix it
- Solved along the way: the first deployment ran with debug mode on and a public secret key, found by checking
  from outside and fixed the same day; it is in the risk log
- Next: the 10 deliberately modified contracts (§6.3), the threshold note, usability sessions before 10/7

**Say:** The system works end to end. What is left is proving how well, and writing down the judgment calls.

---

## If he opens a file (brief §12.2)

Files most likely to be opened, and the one sentence to lead with:

- `core/models.py` — the tables; decisions and outcomes are add-only, which is what makes the record trustworthy
- `core/reading.py` — reading and splitting; the worker claims an agreement in one database step so two workers
  can't read the same file
- `core/rules.py` — one pattern per category; a finding is the whole sentence around the match
- `core/ai_identify.py` — one request per contract; the answer must match a fixed JSON shape, and any quote not
  in the contract is dropped
- `core/review.py` — the review rules in one file: every finding decided before an outcome, and one escalated
  finding escalates the agreement
- `core/permissions.py` — who may do what, including that nobody reviews their own submission

Full explanations: `docs/study-guide-1-web-app.md` and `docs/study-guide-2-pipeline.md`.

# 8. Development and testing

## What I built

A web application, the Vendor Agreement Review Assistant, for Calder Industrial Supply. It is live at https://calder.100-59-211-221.nip.io (AWS Lightsail, since 2026-11-03) and the code is at github.com/Hollmatt2/7590E.

- Django 6, Python 3.14, Postgres on the live site (SQLite on a laptop).
- Four roles: requester, reviewer, approver, administrator.
- Flow: a requester submits an agreement (PDF or .txt). A background step reads it and splits it into clauses. Text rules and Claude Haiku 4.5 find the playbook provisions. A reviewer decides on every finding (accept, dismiss or escalate, with a reason) and records an outcome: cleared, cleared with conditions, or escalated to the approver.
- The ten playbook provisions are in `seed/playbook.csv`. Two use text rules (insurance, audit rights); eight use the AI step.
- The app works with the AI switched off. The provisions the AI looks for then wait on the manual screen, where a reviewer highlights words in a clause and tags them.
- Findings with AI confidence below 0.9 are marked "check carefully" and listed last. Nothing is hidden.
- Scanned PDFs have no text layer. They are marked "Could not read the document". There is no OCR.
- Reports answer Procurement's questions: agreements waiting by stage, turnaround, and provisions found most often.

How each module was made is in `docs/provenance-log.md`. The file map is `docs/code-walkthrough.md`.

## How I tested it

### 1. Automated tests

`python manage.py test` runs 63 tests (`core/tests.py`, `core/test_review.py`, `core/test_auto.py`). I ran it on 2026-11-23 with the project's virtual environment and local SQLite settings: **63 tests, all passed, 35 seconds.** They cover permissions by role, intake checks, the review rules (decisions, outcomes, the audit record), the text rules, and automatic identification including the AI-unavailable path. [CONFIRM: the README still says "about 50" tests; the real count is 63.]

### 2. Check set of 40 CUAD contracts

CUAD is a public set of contracts with clauses labeled by legal experts. I scored the system against its labels on 40 contracts (`seed/check_set.txt`), chosen so every playbook category has at least 12 contracts with a labeled clause. "Found" is the share of labeled clauses the system flagged. "Wrong" is the share of its flags that matched no labeled clause.

| Provision | Text rules: found / wrong | AI step: found / wrong |
|---|---|---|
| Governing law | 80% / 60% | 90% / 5% |
| Notice period to stop renewal | 47% / 27% | 88% / 24% |
| Auto-renewal (CUAD "Renewal Term") | 67% / 48% | 86% / 25% |
| Assignment restriction | 50% / 40% | 62% / 9% |
| Change of control | 63% / 58% | 60% / 32% |
| Termination for convenience | 33% / 73% | 60% / 44% |
| Cap on liability | no rule | 48% / 28% |
| Uncapped liability | 0% / 100% (keyword experiment) | 26% / 75% |
| Insurance | 41% / 22% | 26% / 13% |
| Audit rights | 32% / 26% | 32% / 24% |

Sources: `docs/evaluation-rules-2026-09-17.md` and `docs/evaluation-ai-2026-09-17.md`. The AI run used 40 contracts, cost about $0.88, and the percentages come from those files. The earlier rules run is `docs/evaluation-rules-2026-09-14.md`. Insurance and audit rights stay on text rules because insurance finds more that way (41% against 26%) and audit rights scores the same.

What the numbers say:
- Reliable enough to act on: governing law, notice period to stop renewal, auto-renewal. Each is defined by what a clause says.
- Useful with checking: assignment, change of control, termination for convenience, cap on liability, insurance, audit rights.
- Not reliable: uncapped liability, one of Calder's two stated problems. The system finds about 3 in 10 and most of its flags are wrong. I kept it in the playbook and say so openly (`docs/known-issues.md`).

### 3. Ten modified agreements

CUAD may be in the AI's training data, so the check set can flatter it. I took ten Bonterms and Common Paper standard agreements and changed each on purpose (a notice period cut, an insurance clause removed, an assignment clause inverted, and so on). `seed/modified_agreements/answer_key.csv` records what each file contains. `python manage.py evaluate_modified` scores the same rules and AI step the app runs. Results: `docs/evaluation-modified-2026-09-17.md`, discussion in `docs/verification.md` section 6.3.

- Provisions defined by their own wording held up (governing law 7 of 7, assignment 5 of 5, termination for convenience 5 of 5).
- Uncapped liability did not hold: 1 of 4 files.
- When a protection was inverted, not removed, the system still flagged the topic. It reads topic, not direction. Every finding shows the exact words so a reviewer can catch this.
- Ten files is a small set, and I made the changes myself. It is a check against memorization, not a second opinion.

### 4. Threshold note

`docs/threshold-note.md` records the confidence threshold decision (brief 6.4). On the check set, AI findings at 0.9 or above were wrong 9% of the time and findings below 0.9 were wrong 76% of the time. I set the line at 0.9 and made it a mark, not a filter. A miss costs Calder more than a wasted reviewer hour, so no finding is suppressed. The administrator can change the threshold in the running site (see chapter 10).

### 5. Other checks
- Reading step trial on 30 CUAD PDFs: `docs/ingestion-trial-2026-09-14.txt`. All 30 were read; median 98% of words matched CUAD's text.
- Each deployment is checked from outside with the list in `docs/deployment-runbook.md`.
- Requirement-by-requirement status: `docs/requirements-checklist.md`.

## Not done

- **Brief 6.1 label spot-check: not done.** I have not checked a sample of CUAD's labels against the Labeling Handbook (`docs/verification.md`, 6.1, notes blank).
- Usability sessions with outside people: not done as of 2026-11-23 (`docs/risk-log.md`, risk 12; `docs/usability-sessions.md`). [CONFIRM: update if sessions happen before 12/8.]
- The AI's confidence score as a predictor of correctness has only been checked on the check set, not on reviewer experience.

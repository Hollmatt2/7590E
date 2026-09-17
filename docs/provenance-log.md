# Component provenance log

Required by the project brief, section 12.1. One row per module, updated as the project changes.

How each module was made:
- **Framework-generated**: created by a Django or pip command and not changed by hand
- **Predominantly AI-generated**: written by Claude (Claude Code)
- **Substantially modified**: generated code that I then changed in a meaningful way
- **Predominantly hand-written**: written by me

## Code

| Module | What it does | How it was made | Last change |
|---|---|---|---|
| `manage.py` | Command-line entry point for running and managing the project | Framework-generated (`startproject`) | 2026-09-12 |
| `config/settings.py` | Project settings | Framework-generated; AI-edited for the `core` app, the custom user model, uploads, login, environment variables and deployment | 2026-09-14 |
| `config/urls.py` | Maps web addresses to code | Framework-generated; AI-edited to add the login pages and the `core` app | 2026-09-14 |
| `config/asgi.py`, `config/wsgi.py` | How a web host starts the app | Framework-generated (`startproject`) | 2026-09-12 |
| `core/models.py` | Database tables: users and roles, playbook, agreements, clauses, flags, decisions, dispositions, reviewer notes, administrator settings | Predominantly AI-generated; updated for Change Notice 1 | 2026-09-14 |
| `core/admin.py` | Shows the tables in Django's admin screen, including the playbook screen an administrator edits | Predominantly AI-generated | 2026-09-17 |
| `core/migrations/` | Instructions that create and change the tables | Framework-generated (`makemigrations`, from `core/models.py`) | 2026-09-14 |
| `core/urls.py` | The app's web addresses | Predominantly AI-generated | 2026-09-14 |
| `core/views.py` | The pages: intake, submissions, agreement with clause search, identification, review, outcome, queue, reports | Predominantly AI-generated | 2026-09-17 |
| `core/forms.py` | Intake, findings, decision and outcome forms and their input checks | Predominantly AI-generated | 2026-09-14 |
| `core/permissions.py` | Who may see and do what | Predominantly AI-generated | 2026-09-14 |
| `core/review.py` | Review rules: decisions, outcomes, and the agreement's history | Predominantly AI-generated | 2026-09-14 |
| `core/reading.py` | Extracts the text of a PDF or .txt file and splits it into clauses | Predominantly AI-generated | 2026-09-14 |
| `core/rules.py` | Text rules that find some provisions with patterns | Predominantly AI-generated | 2026-09-14 |
| `core/ai_identify.py` | The AI step: asks Claude which provisions an agreement contains, and checks the answer | Predominantly AI-generated | 2026-09-15 |
| `core/auto_identify.py` | Runs automatic identification (rules and the AI) after a document is read | Predominantly AI-generated | 2026-09-15 |
| `core/cuad.py` | Reads CUAD's labels and category descriptions | Predominantly AI-generated | 2026-09-14 |
| `core/evaluation.py` | Scores identification against CUAD's labels and picks the check set | Predominantly AI-generated | 2026-09-14 |
| `core/templates/` | The HTML pages | Predominantly AI-generated | 2026-09-17 (UGA header and footer in `base.html`) |
| `core/static/core/site.css` | The site's look: UGA brand colors and typefaces | Predominantly AI-generated | 2026-09-17 |
| `core/static/core/brand/` | University of Georgia logo files | Official files from UGA's brand download center, unchanged (see its README) | 2026-09-17 |
| `core/templatetags/review_extras.py` | Highlights the supporting words inside a clause | Predominantly AI-generated | 2026-09-14 |
| `core/management/commands/seed_demo.py` | Demo logins, playbook and sample agreements | Predominantly AI-generated | 2026-09-14 |
| `core/management/commands/load_playbook.py` | Loads the playbook from `seed/playbook.csv` | Predominantly AI-generated | 2026-09-14 |
| `core/management/commands/process_agreements.py` | The reading worker, outside the web request | Predominantly AI-generated | 2026-09-14 |
| `core/management/commands/try_reading.py` | Tries the reading step on a folder of contracts | Predominantly AI-generated | 2026-09-14 |
| `core/management/commands/count_categories.py` | Counts labeled clauses per CUAD category | Predominantly AI-generated | 2026-09-14 |
| `core/management/commands/evaluate_identification.py` | Scores the rules on the CUAD check set | Predominantly AI-generated | 2026-09-14 |
| `core/management/commands/evaluate_modified.py` | Scores the rules on the modified standard agreements | Predominantly AI-generated | 2026-09-14 |
| `core/tests.py`, `core/test_review.py`, `core/test_auto.py` | Automated checks | Predominantly AI-generated | 2026-09-14 |
| `core/apps.py` | App registration | Framework-generated (`startapp`) | 2026-09-12 |
| `start.sh`, `Procfile`, `.python-version` | How the deployed site starts | Predominantly AI-generated | 2026-09-14 |
| `.gitignore` | Files Git must never save | Predominantly AI-generated | 2026-09-14 |
| `requirements.txt` | Python packages the project needs | Framework-generated (`pip freeze`) | 2026-09-14 |

## Data

| File | What it is | How it was made | Last change |
|---|---|---|---|
| `seed/playbook.csv` | The playbook categories, severities and definitions | Placeholder of the brief's suggested categories, written by Claude; definitions copied from CUAD; the final choice is mine | 2026-09-14 |
| `seed/check_set.txt` | The CUAD contracts used for evaluation | Generated by `evaluate_identification --make-check-set`; mine to change | 2026-09-14 |
| `seed/sample_contracts/` | Demo contracts | Copied unchanged from CUAD (CC BY 4.0) | 2026-09-14 |
| `seed/modified_agreements/` | Modified standard agreements and their answer key | Instructions by Claude; the agreements and answer key are mine to make | 2026-09-14 |

## Documents

Whether this log also covers binder documents, or AI-written text needs the syllabus's prompt-and-response
appendix, is an open question for Dr. Srinivasan.

| Document | How it was made | Last change |
|---|---|---|
| `README.md`, `docs/deployment-runbook.md`, `docs/known-issues.md`, `docs/playbook-maintenance.md`, `docs/code-walkthrough.md`, `docs/technical-presentation-notes.md` | Predominantly AI-generated | 2026-09-14 |
| `docs/study-guide-1-web-app.md`, `docs/study-guide-2-pipeline.md` | Predominantly AI-generated: explanations of the code written for me to study from and be quizzed on | 2026-09-16 |
| `docs/change-log.md` | Predominantly AI-generated (drafted by Claude from Change Notice 1) | 2026-09-14 |
| `docs/ambiguity-log.md`, `docs/risk-log.md`, `docs/threshold-note.md`, `docs/verification.md`, `docs/usability-sessions.md` | Templates and factual entries by Claude; decisions, ratings and reasoning are mine | 2026-09-14 |
| `docs/cuad-category-counts.md`, `docs/evaluation-*.md`, `docs/ingestion-trial-*.txt` | Generated by the project's commands | 2026-09-14 |
| `docs/provenance-log.md` | This log | Predominantly AI-generated | 2026-09-14 |

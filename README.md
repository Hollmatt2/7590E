# Calder Agreement Review

A web application for Calder Industrial Supply's vendor-agreement review (MIST 7590E capstone, Fall 2026).
A requester submits an agreement. The system reads it, splits it into clauses, and identifies which
playbook provisions it contains. A reviewer decides on each finding; the agreement is cleared, cleared
with conditions, or escalated to the approver. Every decision is recorded, and reports answer
Procurement's questions.

The system identifies provisions and shows the text behind each one. It does not give legal advice,
negotiate, or redline, and a person decides on every finding.

## Run it on a new machine

You need Python 3.14 (3.12 or later works) and git.

```bash
git clone https://github.com/Hollmatt2/7590E.git calder-review
cd calder-review
python -m venv .venv
source .venv/bin/activate            # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate             # creates the database file, db.sqlite3
python manage.py seed_demo           # demo logins, the playbook, four sample agreements
python manage.py runserver           # the website, at http://127.0.0.1:8000
```

In a second terminal (with the virtual environment active), start the reading step. It reads submitted
documents, splits them into clauses, and runs the text rules:

```bash
python manage.py process_agreements --watch
```

Log in as `requester`, `reviewer`, `approver` or `admin`. The password is `calder-demo`.

## Tests

`python manage.py test` runs every automated check (about 50; under a minute).

## Commands

| Command | What it does |
|---|---|
| `seed_demo` | Demo logins (one per role), the playbook, sample agreements. Safe to run again. |
| `load_playbook` | Loads `seed/playbook.csv` into the playbook. |
| `process_agreements [--watch]` | Reads submitted documents, splits them into clauses, runs automatic identification. |
| `try_reading <folder>` | Tries text extraction and splitting on a folder of contracts, without saving anything. |
| `count_categories` | Counts CUAD's labeled clauses per category into `docs/cuad-category-counts.md`. Needs CUAD. |
| `evaluate_identification` | Scores the text rules against CUAD's labels on `seed/check_set.txt`. With `--method ai` it scores the AI step instead; that costs money, so it shows an estimate and needs `--yes`. Needs CUAD. |
| `evaluate_modified` | Scores the rules on the modified standard agreements in `seed/modified_agreements/`. |

## The CUAD dataset (only for the evaluation commands)

```bash
mkdir -p data/cuad
curl -L -o data/cuad/CUAD_v1.zip 'https://zenodo.org/records/4595826/files/CUAD_v1.zip?download=1'
cd data/cuad && unzip CUAD_v1.zip
```

The `data/` folder is never committed.

## Settings

Everything that differs between a laptop and the deployed site is an environment variable.

| Variable | On a laptop | On the deployed site |
|---|---|---|
| `DJANGO_SECRET_KEY` | a development value | required: a long random string |
| `DJANGO_DEBUG` | `1` | `0` |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Railway's address is added automatically |
| `DATABASE_URL` | SQLite file | Railway's Postgres |
| `MEDIA_ROOT` | `media/` | `/data/media`, on the Railway volume |
| `DEMO_PASSWORD` | `calder-demo` | set your own |
| `AUTO_IDENTIFY` | `rules,ai` | `rules,ai` |
| `ANTHROPIC_API_KEY` | your Anthropic key, for the AI step | the same, set in Railway |
| `AI_MODEL` | `claude-haiku-4-5` | `claude-haiku-4-5` (or `claude-opus-5`) |
| `AI_LOW_CONFIDENCE` | `0.5` | the threshold from the threshold note |

Without `ANTHROPIC_API_KEY`, the app still works: the provisions the AI looks for wait for a person.

## Where things are

- `core/models.py`: the data model. `core/views.py`: the pages. `core/reading.py`: reading documents.
  `core/rules.py`: text rules. `core/review.py`: review rules. `core/evaluation.py`: scoring.
- `docs/code-walkthrough.md` explains every file.
- `docs/deployment-runbook.md`, `docs/known-issues.md`, `docs/playbook-maintenance.md`: running and
  maintaining the system.
- `docs/change-log.md`, `docs/provenance-log.md`, `docs/ambiguity-log.md`, `docs/risk-log.md`: project records.

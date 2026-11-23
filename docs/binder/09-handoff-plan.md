# 9. Handoff plan

This is how Calder would take over the system. Calder is a fictional client, so the plan describes what I would do if they adopted it.

## What Calder receives

| Item | Where |
|---|---|
| Source code | github.com/Hollmatt2/7590E (private); local copy `/home/hollmatt1/Projects/calder-review` |
| How to run it | `README.md` |
| Deployment steps | `docs/deployment-runbook.md` (first deployment on Railway, kept as a record), `deploy/lightsail/README.md` (current) |
| Known limits | `docs/known-issues.md` |
| Changing the playbook | `docs/playbook-maintenance.md` |
| Code map | `docs/code-walkthrough.md` |
| Decisions and records | `docs/change-log.md`, `docs/ambiguity-log.md`, `docs/risk-log.md`, `docs/provenance-log.md`, `docs/threshold-note.md` |
| Test evidence | `docs/verification.md` and the `docs/evaluation-*.md` files |
| Playbook | `seed/playbook.csv` (ten provisions) |
| Seed data | `python manage.py seed_demo` creates the demo logins, the playbook and four sample agreements (`seed/sample_contracts/`) |
| Demo accounts | `requester`, `reviewer`, `approver`, `admin`. The password is `DEMO_PASSWORD` (default `calder-demo`) |
| Evaluation data | `seed/check_set.txt`, `seed/modified_agreements/`. CUAD itself is downloaded separately (README) |

Before go-live Calder deletes the demo accounts and creates real ones.

## Who needs what access

| Person | Needs |
|---|---|
| Procurement staff, regional managers | A requester account |
| Legal reviewers | A reviewer account |
| Associate General Counsel or delegate | An approver account |
| Calder's administrator (the playbook owner) | An administrator account for the `/admin/` screens; read access to the reports |
| Calder IT | The hosting account, the server login, the GitHub repository, and the environment settings (secret key, database password, API key) |

Accounts are created and given roles at `/admin/` (chapter 10). The app has no self-service sign-up.

## API key handling

- The key is `ANTHROPIC_API_KEY`, an environment variable. It is never in the repository (`.gitignore` covers `.env`).
- On the live site it is in `/opt/calder/.env` on the server, readable only by the `ubuntu` user.
- Calder should create its own Anthropic account and key, and I remove mine. One key per environment.
- If a key is ever committed or exposed: rotate it the same hour and record it in `docs/risk-log.md`.
- Cost: the 40-contract AI evaluation cost about $0.88 on Claude Haiku 4.5. [CONFIRM: per-agreement cost has not been measured; estimate from that run is about two cents per contract.]
- Without a key the app still works. The eight AI provisions wait for a person.

## Hosting options

The app is one container (website plus the reading step) and a Postgres database, plus a place for uploaded files.

1. **Lightsail with Docker Compose (current).** `deploy/lightsail/`: `deploy.sh` copies the code and rebuilds. Caddy provides HTTPS. Postgres data is in the `pgdata` volume and PDFs in the `media` volume. Deployment is from a laptop with the SSH key; pushing to GitHub does not deploy. [CONFIRM: no scripted rollback or database backup exists in `deploy/lightsail/`. Risk 13 in the risk log says "deploy and rollback are scripted"; only deploy is. Either add a backup step or change the wording.]
2. **A platform service** such as Railway, which it was before 2026-11-03. Push-to-deploy, but the project was lost on 10/25, so Calder should choose a provider it controls and back up the database and files.
3. **Calder's own cloud account or servers.** The Dockerfile and compose file in `deploy/lightsail/` are the starting point. The settings table in `README.md` lists every environment variable.

For any option Calder needs: HTTPS, a daily database backup, a backup of the uploaded files, and a named person who reads the logs when an agreement stays "Not read yet".

## Training and support
- The user manuals are chapters 10 and 11.
- A 30-minute walkthrough per role, using the sample agreements. [CONFIRM: whether I offer a post-semester support window; as a student project there is none promised.]
- Playbook changes go through `seed/playbook.csv` or `/admin/` (`docs/playbook-maintenance.md`).

## Decisions that belong to Calder

1. **Whether review becomes mandatory before signing.** Today the tool is a place to submit and review, and nothing stops a manager from signing without it. Calder said that 160 of its 200 agreements a year are signed by a regional manager who scrolled to the signature block. The system helps only if agreements go through it. That is a policy decision for Calder's leadership.
2. **The trade-off between misses and wrong flags.** I chose to mark low-confidence findings and hide none, because a miss costs more than a reviewer's hour (`docs/threshold-note.md`). Calder may weigh it differently. The threshold is a setting. Moving it to 0.8 or 0.5 changes how many findings are marked. It does not change what is found.
3. **Retention of uploaded documents.** The setting starts at 0 days, which keeps everything. Calder sets the period and then schedules `python manage.py purge_documents`.
4. **Which provisions are in the playbook, their severity, and which agreement types they apply to.** I chose ten from the brief's list and CUAD. Calder's legal team owns the real list.
5. **What the reviewer does about uncapped liability.** The system finds only about 3 in 10 of these. Calder should decide whether to rely on a reviewer search (the clause search on each agreement page) or a different control.
6. **Notifications.** The app sends no email. Calder decides whether to add them.

## Documents that still describe Railway

Updated on 2026-11-23: the README settings table, `docs/known-issues.md`, `docs/requirements-checklist.md`
and the risk log now describe Lightsail, and `docs/deployment-runbook.md` carries a note pointing to
`deploy/lightsail/README.md`.

Still to clean up before handoff: comments in `start.sh`, and the `RAILWAY_PUBLIC_DOMAIN` host setting in
`config/settings.py` (harmless on Lightsail). The presentations, study guides and code walkthrough mention
Railway as history and can stay as they are.

# 13. Appendices

All paths are in the repository `/home/hollmatt1/Projects/calder-review` (github.com/Hollmatt2/7590E).

## A. Index

| Appendix | What it is | File |
|---|---|---|
| A1 | Ambiguity log: questions about the brief, answers and decisions | `docs/ambiguity-log.md` |
| A2 | Change log: changes to scope, with reasons | `docs/change-log.md` |
| A3 | Risk log | `docs/risk-log.md` |
| A4 | Provenance log: how each module was made (AI or hand) | `docs/provenance-log.md` |
| A5 | Evaluation, text rules, 2026-09-14 and 2026-09-17 | `docs/evaluation-rules-2026-09-14.md`, `docs/evaluation-rules-2026-09-17.md` |
| A6 | Evaluation, AI step, 2026-09-17 | `docs/evaluation-ai-2026-09-17.md` |
| A7 | Evaluation, modified agreements, 2026-09-17 | `docs/evaluation-modified-2026-09-17.md`; files in `seed/modified_agreements/` |
| A8 | Threshold note | `docs/threshold-note.md` |
| A9 | Verification against brief section 6 | `docs/verification.md` |
| A10 | Playbook selection and CUAD category counts | `docs/playbook-selection.md`, `docs/cuad-category-counts.md` |
| A11 | Reading trial on 30 CUAD PDFs | `docs/ingestion-trial-2026-09-14.txt` |
| A12 | Requirements checklist | `docs/requirements-checklist.md` |
| A13 | Usability sessions (plan; sessions not yet run) | `docs/usability-sessions.md` |
| A14 | Known issues | `docs/known-issues.md` |
| A15 | Deployment runbook (Railway, outdated) and Lightsail notes | `docs/deployment-runbook.md`, `deploy/lightsail/README.md` |
| A16 | Playbook maintenance | `docs/playbook-maintenance.md` |
| A17 | Code walkthrough | `docs/code-walkthrough.md` |
| A18 | Data model | ER diagram in `06-requirements.md`, section 6.8; code in `core/models.py` |
| A19 | Playbook and seed data | `seed/playbook.csv`, `seed/check_set.txt`, `seed/sample_contracts/` |
| A20 | AI use (below) | this file |


## B. AI use

### How I used AI
- I used Claude (Claude Code, Anthropic) to draft most of the code and documents, working under my direction. I chose the project, the playbook, the thresholds and the trade-offs, reviewed the work, ran it and decided what to keep.
- `docs/provenance-log.md` records every module as framework-generated, predominantly AI-generated, substantially modified, or hand-written. Most modules are predominantly AI-generated. I wrote the decisions, ratings and reasoning in the ambiguity log, risk log, threshold note and verification document; Claude drafted the structure and factual entries.
- Measurements come from the project's own commands (`evaluate_identification`, `evaluate_modified`). Claude helped compute summary tables from their saved answers, and I checked the figures against the evaluation files.
- Claude also drafted the study guides and the binder sections in this folder from the repository's own documents, and I reviewed them.
- The product itself uses an AI model: Claude Haiku 4.5 identifies provisions in uploaded agreements. A person decides on every finding. The product works with the AI off.
- AI-drafted text can contain errors. Items marked [CONFIRM] in the binder are claims I had not verified when drafted.

### Prompts and responses

The syllabus asks that AI-generated writing be cited with its prompt and response in an appendix.

[Matt: decide which prompt/response pairs to include. Candidates: the prompt that produced the playbook selection and the matching response; the threshold note drafting; the code walkthrough; the binder sections 08, 09, 10, 11 and this appendix. Paste each as:]

**Citation format**
- Tool and model: Claude (Anthropic), model [CONFIRM: model name and version]
- Date: [date]
- Used for: [document or module]
- Prompt: [paste]
- Response: [paste or link to the saved transcript]
- What I changed afterward: [summary]

### Where the AI step is specified
- Code: `core/ai_identify.py` (prompt and answer checking), `core/auto_identify.py` (how it combines with the text rules).
- Model setting: `AI_MODEL` (default `claude-haiku-4-5`).
- Cost and quality: `docs/evaluation-ai-2026-09-17.md`.

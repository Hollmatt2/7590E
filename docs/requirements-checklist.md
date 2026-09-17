# Every requirement, and where it stands

Brief v1 as amended by Change Notice 1 (2026-09-09), plus the syllabus items that carry a grade.
"Fixed" means the sponsor's word for a requirement that cannot change without a change request.
Status as of 2026-09-17.

## Section 3: users, roles and permissions (Fixed)

| Requirement | Status | Where |
|---|---|---|
| Requester: submit, track own submissions, see outcome and conditions | Done | Intake, My submissions, agreement page |
| Reviewer: work the queue, accept / dismiss / escalate each flag with a reason, add notes, complete a review | Done | Work queue, review page, notes (2026-09-17) |
| Approver: everything a Reviewer can do, plus final disposition on escalated items | Done | `core/permissions.py`, `allowed_outcomes` |
| Administrator: manage the playbook and users, configure thresholds, reach reporting | Done | Admin screens: Provisions, Users, Configuration (2026-09-17) |
| Documents and review notes are not public; authentication past the landing page | Done | Every view is behind a login; document download is permission-checked |

## Section 4: core workflow, as amended (Fixed)

| Stage | Status | Where |
|---|---|---|
| 1 Intake: vendor, type, business unit, needed-by, document | Done | `submit_agreement` |
| 2 Ingestion and segmentation | Done | `core/reading.py`, run by the `process_agreements` worker |
| 3 Identification against the playbook | Done | text rules, the AI step, and the manual screen |
| 4 Flag generation: provision, severity, exact source text, reason, confidence | Done | `Flag` model; every finding quotes its clause |
| 5 Review: accept, dismiss, escalate, each with a reason | Done | `core/review.py`, review page |
| 6 Disposition: cleared, cleared with conditions, escalated | Done | `record_disposition` |
| 7 Record: everything persists and can be retrieved | Done | Add-only decisions and dispositions; History table |
| 8 Reporting: aggregate views for Procurement and Legal | Done | Reports page: waiting by stage, turnaround, provisions found most often |
| Comparison to standard positions, deviation characterization, gap detection | Out of required scope | Moved to stretch by Change Notice 1; fields kept in the model |

## Section 5: the AI component, as amended (Fixed)

| Requirement | Status | Where |
|---|---|---|
| Identify which playbook provisions appear in each agreement | Done | `core/ai_identify.py`, eight of ten categories |
| Return the supporting span of source text | Done | Quotes verified against the contract; unverifiable quotes dropped |
| Return a confidence indicator | Done | 0–1 per finding, constrained in the database |
| No chat interface, no drafting or redlining, no AI-only disposition, nothing untraceable to source text | Done | None of these exist in the app |
| The architectural test: remove the AI and it is still a legitimate application | Done | Manual identification path kept; AI failure leaves the agreement for a person |
| A defined behaviour for low-confidence findings | Done | Marked and listed last at 0.9; nothing suppressed (`docs/threshold-note.md`) |

## Section 6: checking that it works (Fixed)

| Requirement | Status | Where |
|---|---|---|
| 6.1 A check set of at least 30 contracts covering the chosen categories | Done | 40 contracts, `seed/check_set.txt`, every category with 12+ examples |
| 6.1 Spot-check labels against the Labeling Handbook, note what surprised you | **Not done** | Matt only |
| 6.2 Two numbers per category, for each method | Done | `docs/evaluation-rules-*.md`, `docs/evaluation-ai-2026-09-17.md` |
| 6.2 Say which categories are handled reliably and which are not, and why | Done | `docs/verification.md` |
| 6.2 Do not report a single overall accuracy figure | Done | Every table is per category |
| 6.3 Ten deliberately modified standard agreements, and whether performance holds | **Not started** | 11 base files and the `evaluate_modified` command are ready; the answer key is empty |
| 6.4 Threshold note, one to two pages, four questions | Done | `docs/threshold-note.md` |

## Section 8: scope, required for a complete project

| Requirement | Status |
|---|---|
| Document ingestion including PDF, with text extraction | Done |
| Clause segmentation | Done |
| Classification against a defined playbook subset | Done: ten categories, selected and justified (`docs/playbook-selection.md`) |
| Review queue with accept, dismiss and escalate, each carrying a reason | Done |
| Role-based access control | Done |
| Durable, attributable audit record of all review decisions | Done |
| Reporting views for Procurement and Legal | Done |
| Deployed and reachable at a URL, seeded with demo data and an account for each role | Done: web-production-48b18.up.railway.app, four demo logins |
| Verification results per Section 6 | Partial: 6.3 outstanding |

## Section 9: technical constraints (Fixed)

| Requirement | Status |
|---|---|
| Web-based, deployed to a public URL well before the final presentation | Done, 2026-09-15 |
| Persistent storage with a defined schema | Done: Postgres; the schema is `core/models.py` and its migrations |
| Source control from Week 2, every member committing | **Missed**: repository created 2026-09-15; recorded in the risk log |
| No real personal data, no real proprietary contracts | Done: public corpus only |
| API keys in environment variables, never in the repository; a committed key gets rotated and logged | Done |
| Decide per category whether a rule or a model fits | Done, with measurements (`docs/playbook-selection.md`) |
| Prove the PDF ingestion path early, with your own decision point | Done, 2026-09-14 |

## Section 10: ambiguity log (graded)

| Requirement | Status |
|---|---|
| A log recording, for each ambiguity: question, options, decision, reasoning, consequence | Done: 18 entries, the brief's 8 plus 10 found while building (`docs/ambiguity-log.md`). Entries 9–18 and the risk-log judgments are drafted and need Matt's confirmation |

## Section 11: governance and handoff (Fixed)

| Requirement | Status |
|---|---|
| Usability sessions with people outside the team, before the managerial storytelling presentation (10/7) | **Not scheduled**: Matt only |
| Document what you observed and what you changed | Not started; template ready |
| README covering setup from a clean machine | Done |
| Seed data and a documented path to a running local instance | Done |
| Deployment runbook | Done |
| A known-issues list, written honestly | Done |
| Playbook maintenance instructions | Done |

## Section 12: development practice and AI use

| Requirement | Status |
|---|---|
| Component provenance log, one row per module, updated as you go | Done |
| Be able to explain any file he opens, including what happens with malformed input | Matt's: study guides written, drill page built |

## Syllabus items with a grade attached

| Item | When | Status |
|---|---|---|
| Technical presentation | Thu 2026-09-17, 6 pm | Slides drafted, demo scripted |
| Peer evaluation #1 | Tue 2026-10-06 | Not due |
| Managerial storytelling presentation | Wed 2026-10-07 | Not due; usability sessions must come first |
| Sitrep | Wed 2026-10-28 | Not due |
| Final practice presentation, 15 minutes | Wed 2026-11-18, 7–9 pm | Not due |
| Final video (30%) and binder (40%), binder by 10 pm | Tue 2026-12-08 | Not due |

## What is deliberately not being built

Stretch, listed in Section 8 or moved there by Change Notice 1: standard positions and deviation
characterization, gap detection, playbook versioning with re-evaluation, clause-level comment threads,
vendor history, bulk intake. Out of scope in Section 8: negotiation and redlining, e-signature, vendor master
data, integration with live Calder systems, mobile apps, multi-tenancy, non-English agreements.

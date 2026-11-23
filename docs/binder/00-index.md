# Project binder (draft)

MIST 7590E AI Technology Capstone, Fall 2026. Matt Holliday, solo team. Vendor Agreement Review Assistant for
Calder Industrial Supply. Due Tue 2026-12-08 by 10 pm on eLC.

This is a first draft written by Claude on 2026-11-23 from the brief, Change Notice 1, the syllabus binder
outline, the repo docs, the code and git history (recorded in `docs/provenance-log.md`). Read every section,
fix the items below, and put it in your own words where it doesn't sound like you before submitting.

## Sections (the syllabus outline, in order)

| Section | Words |
|---|---|
| [1. Executive Summary](01-executive-summary.md) | 474 |
| [2. Business Case](02-business-case.md) | 383 |
| [3. Scope Statement](03-scope-statement.md) | 468 |
| [4. Methodology](04-methodology.md) | 573 |
| [5. Project Planning and Scheduling](05-planning-and-schedule.md) | 829 |
| [6. Requirements](06-requirements.md) | 3762 |
| [7. Design](07-design.md) | 1364 |
| [8. Development and testing](08-development-and-testing.md) | 999 |
| [9. Handoff plan](09-handoff-plan.md) | 944 |
| [10. Administrator manual (outline)](10-admin-manual.md) | 1034 |
| [11. User manual (outline)](11-user-manual.md) | 1047 |
| [12. Conclusions and Final Thoughts](12-conclusions.md) | 575 |
| [13. Appendices](13-appendices.md) | 578 |

The diagrams are Mermaid blocks. GitHub renders them when you open the file there.

## Still missing from the binder

- Screenshots for the wireframes section (`07-design.md` lists each one) and, if you make one, a task board.
- Usability session results (`docs/usability-sessions.md`), once the sessions are run.
- The 6.1 CUAD label spot-check.
- Your confirmation of ambiguity-log entries 9–18 and the risk-log ratings.

## Items to confirm or fill in (25)

- `02-business-case.md`: [CONFIRM: monthly cost of the Lightsail server, if you want to report it. It is not recorded in the repo.]
- `05-planning-and-schedule.md`: [CONFIRM: when work on the project actually started, and when the brief froze (end of Week 2).]
- `05-planning-and-schedule.md`: [CONFIRM: whether work began before 12 Sep.]
- `05-planning-and-schedule.md`: [CONFIRM: which.]
- `05-planning-and-schedule.md`: [CONFIRM: what work happened in that period, such as the 7 Oct video, the 28 Oct sitrep and the Lightsail migration, and add bars if needed.]
- `05-planning-and-schedule.md`: [CONFIRM: dates for usability sessions, managerial video recording and final video.]
- `05-planning-and-schedule.md`: [Matt: add screenshot if you create one.]
- `06-requirements.md`: [CONFIRM: that a test covers type scoping specifically]
- `06-requirements.md`: [CONFIRM: keyword path covered]
- `06-requirements.md`: [CONFIRM: no key was ever committed, or it was rotated and logged]
- `06-requirements.md`: [CONFIRM]
- `07-design.md`: [CONFIRM: highlight placement on screen]
- `08-development-and-testing.md`: [CONFIRM: the README still says "about 50" tests; the real count is 63.]
- `08-development-and-testing.md`: [CONFIRM: update if sessions happen before 12/8.]
- `09-handoff-plan.md`: [CONFIRM: per-agreement cost has not been measured; estimate from that run is about two cents per contract.]
- `09-handoff-plan.md`: [CONFIRM: no scripted rollback or database backup exists in `deploy/lightsail/`. Risk 13 in the risk log says "deploy and rollback are scripted"; only deploy is. Either add a backup step or change the wording.]
- `09-handoff-plan.md`: [CONFIRM: whether I offer a post-semester support window; as a student project there is none promised.]
- `10-admin-manual.md`: [CONFIRM: a new user with role Administrator does not automatically get "Staff status" or "Superuser status"; the demo seeding sets both. To let a new administrator open `/admin/`, tick both boxes on the user's page.]
- `10-admin-manual.md`: [CONFIRM: no CSV or print export exists in the app.]
- `10-admin-manual.md`: [CONFIRM: confirm that automatic identification runs once per agreement; the code skips an agreement that already has automatic findings, but an agreement where the AI failed has none for the AI provisions, and whether a restart retries it was not tested.]
- `10-admin-manual.md`: [CONFIRM: whether Calder wants OCR added; that is future work.]
- `12-conclusions.md`: [CONFIRM: update this paragraph with the results if the sessions happen before 8 Dec.]
- `13-appendices.md`: [CONFIRM]
- `13-appendices.md`: [Matt: decide which prompt/response pairs to include. Candidates: the prompt that produced the playbook selection and the matching response; the threshold note drafting; the code walkthrough; the binder sections 08, 09, 10, 11 and this appendix. Paste each as:]
- `13-appendices.md`: [CONFIRM: model name and version]

## Known inconsistency to settle

`docs/playbook-selection.md` and `docs/evaluation-ai-2026-09-17.md` give uncapped liability as 26% found and
75% of flags wrong; `docs/verification.md`, the slides and the binder use 30% and 71%. Use one pair everywhere,
or say which run each comes from.

# 3. Scope Statement

Scope comes from Project Brief v1 (Section 8), as amended by Change Notice 1 (9 Sep 2026).

## In scope (required baseline)
- Intake: vendor, agreement type, business unit, needed-by date, document (PDF or plain text, up to 20 MB).
- Text extraction and clause segmentation.
- Identification of whether each playbook provision is present, with the supporting text and a confidence indicator.
- Ten playbook provisions: uncapped liability, cap on liability, notice period to stop renewal, auto-renewal, termination for convenience, change of control, assignment restriction, insurance requirement, governing law, audit rights.
- Flag generation, then review: accept, dismiss or escalate, each with a reason.
- Disposition: cleared, cleared with conditions, escalated.
- Four roles with role-based access, and an attributable record of every decision.
- Reports for Procurement and Legal.
- Deployed at a public URL with seed data and a login for each role.
- Verification per brief Section 6: a check set of 40 contracts, two numbers per category, 10 modified agreements, a threshold note.
- Handoff documents: README, runbook, known-issues list, playbook maintenance notes.
- A manual identification path that works with the AI off.

## Change Notice 1
- Removed from required: comparison to standard positions, deviation characterization, gap detection.
- The AI identifies presence only. It does not extract values or describe deviations.
- Reporting question changed to "which provisions come up most often".
- Recorded as change #1 in `docs/change-log.md`. The model fields for deviations and gaps were kept for stretch work, as the notice asked.
- Sponsor advice, followed: build the application with manual identification first, then add the AI.

## Decisions I made inside scope
- Ten categories rather than twelve. Exclusivity and warranty duration were dropped (change #2).
- The playbook applies per agreement type (change #3). Section 8 lists this as stretch; I built it.
- Sponsor feedback on 17 Sep led to highlight-to-tag identification (change #4).

## Stretch
- Built: per-agreement-type playbooks; clause search; reviewer notes; keywords an administrator can add.
- Not built: standard positions and deviation characterization; gap detection; playbook versioning with re-evaluation; clause-level comment threads between Requester and Reviewer; vendor history; bulk intake.

## Out of scope (brief Section 8)
- Negotiation, redlining, or generating contract language.
- E-signature; vendor master data; integration with live Calder systems.
- Mobile apps; multi-tenancy; non-English agreements.
- Legal advice. The system flags and a person decides.
- A chat interface over a contract, and any AI disposition of a flag without a person (brief Section 5).

## Deliberately not built, and known gaps
- Scanned PDFs: no OCR. They are marked "Could not read document" and wait for a person.
- No email notifications.
- A finished review cannot be reopened. A revised contract is a separate agreement.
- Full list: `docs/known-issues.md`.

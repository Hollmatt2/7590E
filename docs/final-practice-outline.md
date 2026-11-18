# Final practice presentation: outline (Wed 11/18, starts 6:00 pm per the 11/17 notice, 15 minutes)

A run-through of the final video. Srinivasan's feedback after 9/17 was that you needed to make more decisions,
so the middle of the talk is your decisions, each with the reason and the evidence. He may also open any file
in the repo and ask you to explain it (brief section 12.2).

Timings add up to 15 minutes. The live demo runs on https://calder.100-59-211-221.nip.io (demo logins:
requester, reviewer, approver; password in /home/hollmatt1/calder-demo-password.txt).

---

## 1. The problem (1 min)

- Calder signs 200+ vendor agreements a year. Legal sees about 40.
- Last spring: three uncapped indemnification clauses signed, and one auto-renewal missed by 11 days.
- What they asked for: a first pass that says which agreements need an attorney and why. Their warning: if it
  misses something real, people stop trusting it.

## 2. What the system does, as a live demo (4 min)

Show one agreement going through the whole flow. Use three browser windows (normal, incognito, a second browser)
so you stay logged in as all three roles.

1. **Requester** uploads a contract: vendor, type, business unit, needed-by date. Shows "My submissions".
2. **Reviewer** opens the work queue, then the review page. Point at a highlighted finding and its confidence.
   Accept one, dismiss one with a reason, escalate one.
3. **Manual path**: on the identification screen, highlight words in a clause and tag the provision. This is
   Srinivasan's 9/17 feedback (mark up text directly), built the same evening.
4. **Approver** gives the outcome: cleared with conditions. Show the History record.
5. **Reports** page: what is waiting at each stage, review times, most frequent provisions.

Say once: the system never decides. It points at clauses, and a person makes and signs every call.

## 3. My decisions (5 min)

Five decisions, each as *what I chose / what I rejected / why*. These are already recorded in the ambiguity log
and the change log under your name.

1. **Advise, don't block.** Software can't stop a manager signing a PDF from email, so claiming to block would be
   false. Status is visible, and reports show who went ahead without review. (Ambiguity log entry 1.)
2. **Ten provisions, not twelve.** Each had to connect to a Calder problem and have enough CUAD examples to
   measure. Dropped exclusivity and warranty duration. Four high severity: uncapped liability, cap on liability,
   auto-renewal, notice period. (docs/playbook-selection.md, change log row 2.)
3. **Rule or AI per provision, chosen by measurement.** Both methods ran on the same 40 contracts. AI won on 8 of
   10. Example: governing law, AI found 90% with 5% wrong flags; the text rule had 60% wrong flags. Insurance
   stays on rules (finds more); audit rights stays on rules (tie, and rules are free).
   (docs/evaluation-ai-2026-09-17.md.)
4. **Show everything, mark low confidence.** Below 0.9 is marked "check carefully" and listed last, never hidden.
   Below 0.9, three flags in four are wrong; above it, about one in eleven. (docs/threshold-note.md.)
5. **Works with the AI off.** The manual tagging path keeps every step working if the AI is down or switched off.

Optional sixth, if asked about hosting: **moved from Railway to my own Lightsail server on 11/3** after Railway
went down and the project's data was lost. Same app, now in Docker behind Caddy with HTTPS. Trade-off: I run
the server myself.

## 4. How well it works, honestly (2.5 min)

- **Reliable:** governing law, auto-renewal, notice period (88% found). The notice period is the clause behind
  the missed renewal.
- **Useful with checking:** assignment, change of control, termination for convenience, cap on liability,
  insurance, audit rights.
- **Not reliable:** uncapped liability, about 30% found and 71% of flags wrong. It is Calder's first problem, so
  I kept it in and marked it rather than drop it. Until it improves, Legal reads every liability section.
- **Modified agreements test:** 10 Bonterms / Common Paper agreements changed on purpose. When an assignment
  clause was reversed to favor the vendor, the system still flagged it but couldn't tell it had been reversed.
  That is why every flag shows the exact words. (docs/verification.md.)

## 5. What's left and what I'd do next (1.5 min)

Be straight about these. He said challenges are the point.

- **Usability sessions:** not run yet, and that is on me. Plan: two or three 20-minute sessions with people
  outside the project (task list in docs/usability-sessions.md) before the final video, with what they found and
  anything I change written into the binder. [Confirm the dates you will say out loud.]
- **Harder PDFs:** feedback (a) from 9/17. Status: scanned PDFs have no text layer, so the system marks them
  "Could not read the document" and they wait in their own queue for a person, instead of being guessed at.
  There is no text recognition (OCR) yet; it is listed in docs/known-issues.md. Next step if time allows.
- **Improve uncapped liability:** the biggest gap that matters to Calder.
- **Decisions that belong to Calder:** whether review becomes required before signing (a policy, not software),
  and whether they accept more wrong flags in exchange for fewer misses.

## 6. Questions (1 min buffer)

Files he might open, and the one-line answer for each:

- `core/models.py`: the seven database tables (agreement, provision, flag, decision and so on).
- `core/reading.py`: reads the PDF with pdfplumber and splits it into clauses. Bad PDFs are marked "read failed".
- `core/ai_identify.py`: sends clauses to Claude Haiku, gets back present / quote / confidence, and checks the
  quote really appears in the clause.
- `core/rules.py`: the text rules for insurance and audit rights.
- `core/review.py`: the rules for decisions, such as nobody reviewing their own submission.

Your study guides cover each file in more depth: docs/study-guide-1-web-app.md and
docs/study-guide-2-pipeline.md.

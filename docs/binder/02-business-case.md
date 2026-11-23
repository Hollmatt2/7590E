# 2. Business Case

## The problem, from the brief
- Calder signs more than 200 vendor agreements a year.
- Legal sees about 40. A regional manager signs the rest.
- Three business units signed agreements with uncapped indemnification.
- One auto-renewal had a 90-day notice window nobody tracked. It was caught 11 days too late.
- Contract review is unmanaged: no queue, no record of what was reviewed, no turnaround data, no written standard.
- Legal has two attorneys and cannot add headcount.

## Value created
- **Triage.** The system points a reviewer to the provisions that matter (uncapped liability, liability cap, auto-renewal, renewal notice period, and six more) and shows the exact clause text. A reviewer can act without rereading the agreement.
- **A durable record.** Every accept, dismiss, escalate and disposition is stored with who made it and why. It can be retrieved later.
- **A queue.** Agreements wait in a visible state. Requesters can see status, outcome and conditions.
- **Reporting.** Procurement can see how many agreements are in review, how long each stage waits, and which provisions come up most often.
- **A written playbook.** Ten provisions, each with a severity, an identification method, and the evidence for that method (`docs/playbook-selection.md`). The standard Calder lacked now exists in writing.
- **Measured accuracy.** The brief's client said a tool that misses things loses trust. The accuracy is reported per category, so Legal knows which findings to rely on and which to check.

## What the value depends on
- The system finds about 63% of labeled clauses across its eight AI categories, and 30% for uncapped liability. It cannot yet replace Legal reading liability sections.
- It identifies a provision's topic, not which way the obligation runs. A reviewer must read the quoted words.
- Calder has not decided whether review is required before signing. The system advises. It does not block (ambiguity log, question 1).

## Cost
- No project budget was set. Running costs I can state: AI evaluation of 40 contracts with Haiku 4.5 cost $0.88 (`docs/evaluation-ai-2026-09-17.md`).
- [CONFIRM: monthly cost of the Lightsail server, if you want to report it. It is not recorded in the repo.]
- No dollar figure for time saved is claimed. The brief gives no data to support one.

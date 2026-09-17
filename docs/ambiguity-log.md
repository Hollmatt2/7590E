# Ambiguity log

Graded (brief, section 10). For each open question: the options considered, the decision, the reasoning,
and the consequence for the design. The decisions and reasoning are Matt's.

"What the app does now" records the temporary behavior built on 2026-09-14 so the app could run. It is a
starting point, not a decision.

## 1. Advisory or gating
Does a pending review block the Requester, or only inform them?
- What the app does now: advisory. The requester only sees the status.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

## 2. Playbook mutability
When an Administrator changes a standard position, what happens to completed reviews: re-run, mark stale, or leave alone?
- What the app does now: leaves them alone. Nothing is re-run.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

## 3. Playbook scope
One organization-wide standard per provision, or different standards per agreement type?
- What the app does now: one playbook for every agreement type.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

## 4. Low-confidence handling
Suppress, warn, or a separate queue? Ties to the threshold note.
- What the app does now: warn. AI findings below 0.5 confidence (the `AI_LOW_CONFIDENCE` setting) are
- Options considered: hide findings below the threshold; send them to a separate queue; show them, marked, ordered last.
- Decision: show every finding, mark the low-confidence ones "check carefully", and list them last (2026-09-17).
- Reasoning: Calder's stated fear is a real problem the system stays silent about, because that is what stops
  people trusting it. Hiding a finding is exactly that failure, and a separate queue is a queue nobody has time
  to work. Marking keeps the reviewer's attention ordered without the system deciding for them.
- Consequence for the design: `AI_LOW_CONFIDENCE` (0.9 since 2026-09-17, see `docs/threshold-note.md`) only
  affects display, never whether a finding is saved.
  The review page marks those findings and sorts them last: about three in ten AI findings, holding most of
  the wrong ones.

## 5. Document retention
Is the uploaded agreement kept after disposition, and for how long? What does the record look like once it is gone?
- What the app does now: keeps every file indefinitely.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

## 6. Note visibility
Can a Requester see reviewer deliberation, or only outcomes?
- What the app does now: requesters see the status, the outcome and any conditions, but not the findings,
  decisions or reasons.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

## 7. Dismissal semantics
Is a dismissal a judgment about this contract alone, or a signal the system carries forward?
- What the app does now: this contract alone.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

## 8. Definition of done
Is a review complete when every flag has a disposition, or when the Reviewer says it is?
- What the app does now: the outcome can be recorded only after every finding has a decision.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

## Others found while building

### 9. Can a Reviewer approve an agreement they submitted? (brief, section 3)
- What the app does now: no. Nobody reviews an agreement they submitted.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

### 10. Is Approver a separate role, or a permission some Reviewers hold? (section 3)
- What the app does now: four separate roles.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

### 11. What does a user see without permission: hidden, or visible but locked? (section 3)
- What the app does now: links are hidden; opening the address directly gives a "403 Forbidden" page.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

### 12. Is escalation a state or a separate queue? (section 4)
- What the app does now: a status, shown as its own section of the work queue. Only the approver finishes it.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

### 13. Can a completed review be reopened, and what happens to the earlier record? (section 4)
- What the app does now: it cannot be reopened.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

### 14. How does a revised resubmission relate to the original agreement? (section 4)
- What the app does now: it is a separate agreement with no link to the original.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

### 15. If one finding is escalated, must the whole agreement be escalated?
- What the app does now: yes.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

### 16. Who may submit agreements?
- What the app does now: any logged-in user, not only requesters.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

### 17. Which file types are accepted?
- What the app does now: PDF and plain text, up to 20 MB. Scanned PDFs cannot be read.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

### 18. What happens to automatic findings a person removes before review?
- What the app does now: they are deleted and do not appear in the record.
- Options considered:
- Decision:
- Reasoning:
- Consequence for the design:

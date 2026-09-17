# Ambiguity log

Graded (brief, section 10). For each open question: the options considered, the decision, the reasoning,
and the consequence for the design. The decisions and reasoning are Matt's.

"What the app does now" records the temporary behavior built on 2026-09-14 so the app could run. It is a
starting point, not a decision.

## 1. Advisory or gating
Does a pending review block the Requester, or only inform them?
- What the app does now: advisory. The requester only sees the status.
- Options considered: advisory, so the requester sees the status and decides; gating, so a pending review
  blocks them from proceeding; advisory now with gating once there is a purchasing integration.
- Decision: advisory (2026-09-17).
- Reasoning: the app cannot stop a regional manager signing a PDF that arrived in their email, which is how
  Calder got into this. Claiming to gate would be claiming control the system does not have. What the app can
  do is make the status and the outcome visible, and give Procurement the numbers to enforce a policy that
  Calder, not the software, owns.
- Consequence for the design: statuses are informative rather than blocking; no agreement is ever locked from
  the requester's side; the reports exist partly so Procurement can see who is proceeding without review.
  Gating would need the purchase-order integration that section 8 puts out of scope.

## 2. Playbook mutability
When an Administrator changes a standard position, what happens to completed reviews: re-run, mark stale, or leave alone?
- What the app does now: leaves them alone. Nothing is re-run.
- Options considered: leave finished reviews alone; mark them as reviewed under an older playbook; re-run
  them against the new one.
- Decision: leave them alone (2026-09-17).
- Reasoning: a decision was made in a context, and the record has to keep that context or it stops being an
  audit record. Re-running rewrites history and could reopen closed agreements; marking stale is honest but
  adds machinery nobody asked for while the playbook is still changing weekly.
- Consequence for the design: each flag copies the severity in force when it was raised rather than reading
  the playbook later, so changing a severity never rewrites past reviews. Playbook versioning with
  re-evaluation is in the stretch backlog (brief, section 8).

## 3. Playbook scope
One organization-wide standard per provision, or different standards per agreement type?
- What the app does now: one playbook for every agreement type.
- Options considered: one organization-wide playbook; a separate playbook per agreement type; one playbook
  where only the severity varies by type.
- Decision: per agreement type, implemented as scope on each provision (2026-09-17).
- Reasoning: a data processing addendum and a logistics contract do not carry the same risks, and flagging
  insurance on a SaaS subscription trains reviewers to ignore flags. Keeping one list of provisions, each
  marked with the types it applies to, gets the accuracy without five playbooks to maintain and measure.
- Consequence for the design: `Provision.agreement_types` (empty means every type), set on the administrator
  screen and in `seed/playbook.csv`. Automatic identification and the manual screen both offer only the
  provisions that apply to that agreement's type. Starting mapping: insurance on professional services,
  licensing and logistics; audit rights on software subscriptions, data processing addenda and logistics;
  the other eight on every type. Evaluation still measures categories, not types, since the CUAD corpus has
  no Calder agreement types.

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
- Options considered: keep the document forever; delete it a fixed time after the outcome; delete it as soon
  as the review finishes.
- Decision: the app can delete documents on a schedule, and the period is an administrator setting that
  starts at 0, meaning keep (2026-09-17). Calder has not stated a policy, so the system does not invent one.
- Reasoning: deleting a vendor agreement by default would destroy the evidence behind a recorded decision,
  which is worse for Calder than storing a public contract too long. But a real retention policy is normal in
  procurement, so the mechanism has to exist before Legal asks for it, not after.
- Consequence for the design: `Configuration.document_retention_days` on the administrator screen, and
  `python manage.py purge_documents` deletes only the file, never the record. The agreement page then says
  the document was deleted on a date and that the record remains. Findings quote their source text, so a
  review stays readable without the file.

## 6. Note visibility
Can a Requester see reviewer deliberation, or only outcomes?
- What the app does now: requesters see the status, the outcome and any conditions, but not the findings,
- Options considered: show requesters everything, including reviewer notes and findings; show them the
  outcome and any conditions only.
- Decision: requesters see status, outcome and conditions. Findings and reviewer notes are internal
  (2026-09-17).
- Reasoning: the brief's role table gives a Requester the outcome and any conditions, and a review that a
  requester reads over the shoulder stops being candid. What a requester needs is what to do next, which the
  conditions say.
- Consequence for the design: `show_findings` in the agreement view is true only for staff roles; the notes
  and history sections follow the same flag, and the review pages are behind a role check.

## 7. Dismissal semantics
Is a dismissal a judgment about this contract alone, or a signal the system carries forward?
- What the app does now: this contract alone.
- Options considered: a dismissal is about this contract only; dismissals are counted and reported but change
  nothing automatically; dismissals carry forward and suppress that provision in future.
- Decision: this contract only (2026-09-17).
- Reasoning: "not an issue here" is not "never flag this again". Carrying dismissals forward would quietly
  stop the system reporting something real, which is the exact failure Calder described. If a rule is wrong
  often enough to matter, the fix is to change the rule deliberately and re-measure it, not to let the queue
  drift.
- Consequence for the design: a decision writes a row against one flag and nothing else; no feedback loop
  touches identification. Counting dismissals per provision in the reports is an obvious next step and would
  give the evidence for changing a rule on purpose.

## 8. Definition of done
Is a review complete when every flag has a disposition, or when the Reviewer says it is?
- What the app does now: the outcome can be recorded only after every finding has a decision.
- Options considered: a review is done when every finding has a decision; done when the reviewer says so;
  done when every finding has a decision, with a way to dismiss several at once.
- Decision: every finding has a decision (2026-09-17).
- Reasoning: it makes the record complete by construction. Nobody can close an agreement while a finding sits
  there that no one looked at, and "I decided not to look" is not something you want to discover in an audit
  six months later. The cost is clicks on a noisy contract, which is a reason to improve precision rather
  than to loosen the rule.
- Consequence for the design: `record_disposition` refuses an outcome while any flag is open, and the review
  page says how many are left. A bulk dismiss with one shared reason stays on the list as a usability
  improvement, to be tested in the usability sessions.

## Others found while building

### 9. Can a Reviewer approve an agreement they submitted? (brief, section 3)
- What the app does now: no. Nobody reviews an agreement they submitted.
- Options considered: allow it, since a small team may have nobody else free; forbid it.
- Decision: forbid it (2026-09-14, drafted from the app's behavior; confirm).
- Reasoning: separation of duties. The person who wants the contract signed has an interest in it clearing,
  and a record showing the requester cleared their own agreement is worth nothing to Legal. Calder has two
  attorneys but also a procurement team, so somebody else is always available.
- Consequence for the design: `can_review` returns False when the agreement's submitter is the current user,
  whatever their role. An administrator with a genuine conflict has to hand it to another reviewer, which is
  the outcome we want anyway.

### 10. Is Approver a separate role, or a permission some Reviewers hold? (section 3)
- What the app does now: four separate roles.
- Options considered: four roles as the brief lists them; three, with Approver as a permission some Reviewers
  hold.
- Decision: keep four (2026-09-14, drafted; confirm).
- Reasoning: the brief allows three if it can be justified, and the argument for merging is that Calder has
  one Associate General Counsel, so the Approver role has one holder. The argument against is stronger here:
  final disposition on escalated items is exactly the boundary Legal cares about, and a role makes that
  boundary visible in the record rather than hidden in a permission flag.
- Consequence for the design: `User.role` has four values; `REVIEW_ROLES` covers reviewer and approver, and
  only the approver can finish an escalated agreement. Collapsing to three later would be a data migration,
  not a redesign.

### 11. What does a user see without permission: hidden, or visible but locked? (section 3)
- What the app does now: links are hidden; opening the address directly gives a "403 Forbidden" page.
- Options considered: hide what a user cannot use; show it disabled with an explanation.
- Decision: hide the links, and refuse the address with 403 Forbidden (2026-09-14, drafted; confirm).
- Reasoning: showing a requester a Work queue link they cannot open teaches them the tool is not for them.
  Hiding keeps each role's screen to what that role does. The permission check lives on the server either
  way, so hiding is presentation, not protection.
- Consequence for the design: the navigation is built per role in `base.html`; every view carries its own
  `role_required` check, so typing an address gives 403 rather than a page.

### 12. Is escalation a state or a separate queue? (section 4)
- What the app does now: a status, shown as its own section of the work queue. Only the approver finishes it.
- Options considered: escalation as a status on the agreement; escalation as a separate queue with its own
  list and rules.
- Decision: a status, shown as its own section of the work queue (2026-09-14, drafted; confirm).
- Reasoning: the agreement is still the unit of work, and a second queue would mean two places to look and
  two things to keep in step. A status with its own section in the queue gives the approver the same view
  without splitting the model.
- Consequence for the design: `Agreement.Status.ESCALATED`, `allowed_outcomes` limits an escalated agreement
  to cleared or cleared with conditions, and `can_review` gives escalated agreements to approvers only.

### 13. Can a completed review be reopened, and what happens to the earlier record? (section 4)
- What the app does now: it cannot be reopened.
- Options considered: allow reopening, keeping the earlier record; allow it and replace the record; forbid it.
- Decision: forbid reopening for now (2026-09-14, drafted; confirm).
- Reasoning: the value of the record is that it cannot be edited after the fact. A revised contract is a new
  agreement, not a rewrite of the old review. The honest cost is a reviewer who records the wrong outcome and
  cannot correct it, which a usability session may well raise; the answer would be a correcting entry, never
  an edit.
- Consequence for the design: statuses move forward only, and dispositions are add-only rows. If reopening is
  added later it will be a new disposition on top of the old one, leaving both in the history.

### 14. How does a revised resubmission relate to the original agreement? (section 4)
- What the app does now: it is a separate agreement with no link to the original.
- Options considered: a resubmission is an unrelated agreement; a resubmission links to the original as a new
  version.
- Decision: unrelated for now, and worth fixing (2026-09-14, drafted; confirm).
- Reasoning: it is the one place where the current design loses something real. Calder's reviewers will ask
  what changed since the last draft, and today they have to find the earlier agreement by name. The work is a
  link between agreements and a way to show the earlier review, which is stretch alongside vendor history.
- Consequence for the design: nothing in the schema stops it later; adding a nullable `supersedes` link to
  Agreement would be one migration. Recorded in the known-issues list so it is not discovered in December.

### 15. If one finding is escalated, must the whole agreement be escalated?
- What the app does now: yes.
- Options considered: one escalated finding escalates the agreement; the reviewer chooses the outcome
  regardless of individual findings.
- Decision: one escalated finding escalates the agreement (2026-09-14, drafted; confirm).
- Reasoning: escalation means "somebody senior has to see this". Letting a reviewer clear an agreement that
  contains an escalated finding would make escalation advisory, and the point of the flag is that it is not.
- Consequence for the design: `allowed_outcomes` returns only Escalated while any flag is escalated, and the
  approver then decides the agreement as a whole.

### 16. Who may submit agreements?
- What the app does now: any logged-in user, not only requesters.
- Options considered: only requesters submit; any logged-in user submits.
- Decision: any logged-in user (2026-09-14, drafted; confirm).
- Reasoning: at Calder the person who needs an agreement signed might be a regional manager, a department
  head, or an attorney who received it directly. Restricting intake to one role would push people back to
  email, which is the behaviour the system exists to replace. Review permissions stay strict; intake does not
  need to be.
- Consequence for the design: the intake view requires a login and nothing more, and every agreement records
  who submitted it. Because nobody reviews their own submission, a reviewer who submits one simply cannot
  review it.

### 17. Which file types are accepted?
- What the app does now: PDF and plain text, up to 20 MB. Scanned PDFs cannot be read.
- Options considered: PDF only; PDF and plain text; add Word documents; add scanned PDFs through text
  recognition.
- Decision: PDF and plain text, up to 20 MB (2026-09-14, drafted; confirm).
- Reasoning: PDF is what vendors send. Plain text is accepted because the corpus ships that way and the brief
  calls switching to it a defensible scoping decision. Word documents would mean another parser for a format
  Calder rarely receives from vendors, and text recognition for scans is a project of its own with its own
  accuracy problem underneath this one.
- Consequence for the design: the intake form checks the extension, the size, and that a PDF really starts
  with %PDF. A scan is detected by having almost no text and is reported as unreadable rather than processed
  into nonsense. Listed in known issues.

### 18. What happens to automatic findings a person removes before review?
- What the app does now: they are deleted and do not appear in the record.
- Options considered: delete removed findings; keep them with a "removed" status so the record shows what
  the automatic methods produced.
- Decision: delete them for now, and treat it as a known gap (2026-09-14, drafted; confirm).
- Reasoning: the identification screen exists so a person can clear out obvious noise before review, and a
  reviewer does not want dozens of dead findings in the record of a contract. The cost is that the record no
  longer shows everything the rules and the model produced, which is exactly what the evaluation work needs
  to be honest about. The evaluation measures the methods directly against CUAD, which is why this is
  tolerable.
- Consequence for the design: removal deletes the flag, and only flags with decisions are protected from
  deletion. Keeping them with a status would be a small change if a usability session shows reviewers want
  to see what was thrown away.

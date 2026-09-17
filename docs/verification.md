# Verification (brief, section 6)

Where each of the four fixed requirements stands, and where the evidence is.

## 6.1 Check set
- 40 CUAD contracts in `seed/check_set.txt`, chosen by `evaluate_identification --make-check-set 40`: contracts
  were added until every playbook category had at least 8 contracts with a labeled clause, then the rest at
  random. Every category ended with at least 12.
- Spot-check a handful of labels against the Labeling Handbook and note what surprised you: **not done**.

  Notes:

## 6.2 Two numbers per category
- Text rules: `docs/evaluation-rules-2026-09-14.md` (eight categories) and `docs/evaluation-rules-2026-09-17.md`
  (the text pass under the ten-category playbook, including the keyword experiment).
- AI step: `docs/evaluation-ai-2026-09-17.md`, all twelve categories then in the playbook, Claude Haiku 4.5, $0.88.
- Which categories the system handles reliably, which it does not, and why:

  **Reliable enough to act on.** Governing law (90% found, 5% of flags wrong), notice period to stop renewal
  (88%, 24%), auto-renewal (86%, 25%). Each is announced by wording a drafter has little freedom over: a
  choice of law, a number of days before an expiry, a term that renews.

  **Useful with checking.** Assignment restriction (62%, 9%), change of control (60%, 32%), termination for
  convenience (60%, 44%), cap on liability (46%, 28%), insurance by text rule (41%, 22%), audit rights by
  text rule (32%, 26%). These are real provisions with many shapes; the system surfaces most contracts that
  contain one, and a reviewer confirms.

  **Not reliable.** Uncapped liability (30% found, 71% of flags wrong), and it is one of Calder's two stated
  problems. Kept in the playbook, marked, and named as a limitation rather than hidden.

  **The explanation for the difference.** The categories that work are defined by what a clause *says*. The
  categories that fail are defined by what a clause *does to another clause*: uncapped liability is a
  carve-out from a cap, so its wording follows whatever the cap said, and the same sentence is a carve-out in
  one contract and boilerplate in another. Frequency matters too, but less: audit rights has 68 labeled
  clauses in the check set and still scores 32%, while notice period has 17 and scores 88%.

  The keyword experiment supports this. A word list for uncapped liability found 0 of 20 labeled clauses
  (`docs/playbook-selection.md`), which is what you would expect for a category with no shared phrasing.

## 6.3 Small independent check
- 10 deliberately modified standard agreements in `seed/modified_agreements/`: **not started**. The scoring
  command (`evaluate_modified`) and the instructions are ready.

## 6.4 Threshold note
- `docs/threshold-note.md`: **written 2026-09-17**, from the check-set run. Threshold 0.9, marking only;
  nothing is suppressed. To be revisited after the modified-agreement check.

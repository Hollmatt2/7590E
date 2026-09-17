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
- **Done 2026-09-17.** Ten standard-form agreements from Bonterms and Common Paper, each changed on purpose,
  in `seed/modified_agreements/`, with `answer_key.csv` recording every provision present and what was
  changed. Scored with `python manage.py evaluate_modified`, which runs the same text rules and AI step the
  app runs. Table: `docs/evaluation-modified-2026-09-17.md`.

### What was changed

| File | Change |
|---|---|
| `cloud-terms-delaware.txt` | Non-renewal notice cut from 30 days to 7; the uncapped-claims carve-out deleted, so every claim is capped |
| `csa-free-assignment.txt` | Mutual assignment restriction replaced with a one-sided clause letting the provider assign freely |
| `psa-no-insurance.txt` | The whole insurance obligation removed |
| `psa-five-day-termination.txt` | Termination for convenience cut from 30 days' notice to 5 |
| `dpa-no-audit.txt` | The customer's audit right removed and replaced with an express denial |
| `dpa-restricted-audit.txt` | Audits restricted to once every three years on 90 days' notice |
| `nda-no-change-of-control.txt` | The change-of-control exception to the assignment ban removed |
| `nda-auto-renewing.txt` | An auto-renewal with a 45-day non-renewal notice inserted |
| `sla-uncapped-liability.txt` | An uncapped liability carve-out inserted |
| `sla-with-audit-right.txt` | An audit right inserted |

### Does performance hold?

Mostly yes, and the place it fails is the place CUAD said it would.

- **Holds or improves** on the provisions defined by their own wording. Governing law 7 of 7, renewal term 3
  of 3, notice period 3 of 3, assignment restriction 5 of 5, termination for convenience 5 of 5 (against 63%
  on CUAD). Inserted provisions were found: the auto-renewal and notice period written into an NDA, and the
  audit right written into an SLA.
- **Does not hold** for uncapped liability: 1 of the 4 files that contain it. On CUAD it was 30%. The
  inserted carve-out in `sla-uncapped-liability.txt` ("not subject to the limitations of liability in the
  Cloud Terms and is unlimited") was missed even though it is about as explicit as that provision gets.
- **Change of control**: 2 of 4, similar to CUAD's 60%.
- **Audit rights** (text rule): 1 of 2. The rule wants an audit word near "books", "records" or "accounts",
  and the restricted-audit DPA says "audits, including inspections by Customer", so the rule misses it.

### Three findings worth reporting

1. **The system reads topic, not direction.** In `csa-free-assignment.txt` the assignment restriction was
   replaced by a clause that lets the provider assign freely, with no consent and no notice. The system still
   flagged assignment restriction. It saw that the contract talks about assignment; it did not notice that the
   protection had been inverted. A reviewer reading the quoted words would catch it in seconds, which is the
   argument for every finding carrying its source text.
2. **Removals are handled better than inversions.** Where a protection was deleted outright (insurance, the
   audit right, the uncapped-claims carve-out), the system did not flag it: insurance 0 false flags across 9
   files, audit rights 0 across 8.
3. **The cap is identified, but the quote moves.** Cap on liability was flagged in all 4 files that contain
   it, but never with the sentence the answer key records: the model quotes the definition of the cap rather
   than the clause that imposes it. Presence is right; "the exact words" is a judgment call between two
   sentences that both show the provision. The answer key records one quote per provision, which is stricter
   than a reviewer would be.

### Honest notes about this test

- Three false governing-law flags come from cover pages added when the files were made, which say
  "Governing Law: as set out in the Cloud Terms". No state is named, so the answer key counts that as absent,
  and the system flags it. Both readings are defensible, and it is a good example of a label being debatable.
- The AI step is not deterministic. Three runs of uncapped liability on the same ten files gave 0, 2 and 1 of
  4. Small counts move; the conclusion that this category is unreliable does not.
- Ten files is a small set, and the changes were made by the same person who chose the playbook. It is a check
  against memorization, not a second opinion.

## 6.4 Threshold note
- `docs/threshold-note.md`: **written 2026-09-17**, from the check-set run. Threshold 0.9, marking only;
  nothing is suppressed. To be revisited after the modified-agreement check.

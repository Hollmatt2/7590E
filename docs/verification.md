# Verification (brief, section 6)

Where each of the four fixed requirements stands, and where the evidence is.

## 6.1 Check set
- 40 CUAD contracts in `seed/check_set.txt`, chosen by `evaluate_identification --make-check-set 40`: contracts
  were added until every playbook category had at least 8 contracts with a labeled clause, then the rest at
  random. Every category ended with at least 12.
- Spot-check a handful of labels against the Labeling Handbook and note what surprised you: **not done**.

  Notes:

## 6.2 Two numbers per category
- Text rules: `docs/evaluation-rules-2026-09-14.md`.
- AI step: not built yet.
- Which categories the system handles reliably, which it does not, and the best explanation for the
  difference (Matt): **not written**.

## 6.3 Small independent check
- 10 deliberately modified standard agreements in `seed/modified_agreements/`: **not started**. The scoring
  command (`evaluate_modified`) and the instructions are ready.

## 6.4 Threshold note
- `docs/threshold-note.md`: **not written**; needs the AI step's results.

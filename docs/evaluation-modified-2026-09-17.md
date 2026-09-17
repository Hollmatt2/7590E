# Modified-agreement evaluation, 2026-09-17

10 deliberately modified standard agreements (brief, section 6.3), listed in `seed/modified_agreements/answer_key.csv`. Method: the text rules for the categories that have one, and the AI step for the categories the playbook gives it, which is what the deployed app does.

| Category | Files containing it | Flagged | Flagged at the right words | Files without it | Flagged anyway |
|---|---|---|---|---|---|
| Anti-Assignment | 5 | 5 | 5 | 5 | 1 |
| Audit Rights | 2 | 1 | 1 | 8 | 0 |
| Cap On Liability | 4 | 4 | 0 | 6 | 1 |
| Change Of Control | 4 | 2 | 2 | 6 | 1 |
| Governing Law | 7 | 7 | 7 | 3 | 3 |
| Insurance | 1 | 1 | 1 | 9 | 0 |
| Notice Period To Terminate Renewal | 3 | 3 | 3 | 7 | 0 |
| Renewal Term | 3 | 3 | 3 | 7 | 1 |
| Termination For Convenience | 5 | 5 | 5 | 5 | 1 |
| Uncapped Liability | 4 | 1 | 1 | 6 | 0 |

## Per file
- `cloud-terms-delaware.txt`: expected Anti-Assignment, Cap On Liability, Change Of Control, Governing Law, Notice Period To Terminate Renewal, Renewal Term, Termination For Convenience; flagged Anti-Assignment, Cap On Liability, Governing Law, Notice Period To Terminate Renewal, Renewal Term, Termination For Convenience
- `csa-free-assignment.txt`: expected Cap On Liability, Governing Law, Notice Period To Terminate Renewal, Renewal Term, Uncapped Liability; flagged Anti-Assignment, Cap On Liability, Change Of Control, Governing Law, Notice Period To Terminate Renewal, Renewal Term
- `dpa-no-audit.txt`: expected Governing Law; flagged Governing Law, Termination For Convenience
- `dpa-restricted-audit.txt`: expected Audit Rights; flagged Governing Law
- `nda-auto-renewing.txt`: expected Anti-Assignment, Change Of Control, Governing Law, Notice Period To Terminate Renewal, Renewal Term, Termination For Convenience; flagged Anti-Assignment, Change Of Control, Governing Law, Notice Period To Terminate Renewal, Renewal Term, Termination For Convenience
- `nda-no-change-of-control.txt`: expected Anti-Assignment, Governing Law, Termination For Convenience; flagged Anti-Assignment, Governing Law, Termination For Convenience
- `psa-five-day-termination.txt`: expected Anti-Assignment, Cap On Liability, Change Of Control, Governing Law, Insurance, Termination For Convenience, Uncapped Liability; flagged Anti-Assignment, Cap On Liability, Governing Law, Insurance, Termination For Convenience
- `psa-no-insurance.txt`: expected Anti-Assignment, Cap On Liability, Change Of Control, Governing Law, Termination For Convenience, Uncapped Liability; flagged Anti-Assignment, Cap On Liability, Change Of Control, Governing Law, Renewal Term, Termination For Convenience, Uncapped Liability
- `sla-uncapped-liability.txt`: expected Uncapped Liability; flagged Cap On Liability, Governing Law
- `sla-with-audit-right.txt`: expected Audit Rights; flagged Audit Rights, Governing Law

# Playbook maintenance

The playbook is the list of provisions the system looks for. The Administrator role owns it (brief,
section 3).

## What an entry holds
- **Name**: what reviewers see, such as "Cap on liability".
- **CUAD category**: the matching CUAD label. The text rules (`core/rules.py`) and the evaluation use it.
- **Default severity**: low, medium or high. New findings for the provision start at this severity.
- **Definition**: what counts as the provision. By default, CUAD's own description of the category.
- **Standard position** and **required**: kept for stretch work since Change Notice 1; not used.

## Changing the playbook
`seed/playbook.csv` is the source of truth.
1. Edit the CSV: add, remove or change rows.
2. Run `python manage.py load_playbook`. The deployed site does this every time it starts.
3. Check the evidence: `python manage.py count_categories` and `python manage.py evaluate_identification`.
4. Record the change and the reason in `docs/change-log.md`.

An administrator can also edit entries in the admin screens at `/admin/`. The next `load_playbook` run
overwrites those edits, so copy them into the CSV.

Removing a row from the CSV does not delete the provision. Delete it in `/admin/`; that is only possible
while no finding uses it.

## Finished reviews
Changing the playbook does not re-run earlier reviews. Their findings and decisions stay as they were.
(Ambiguity log, question 2.)

## Adding a text rule
If a provision can be found with a pattern, add the pattern to `RULES` in `core/rules.py`, add a typical
sentence to `RuleTests` in `core/test_auto.py`, and measure it with `evaluate_identification`. Test a
changed rule on contracts outside the check set, or the score will look better than it is.

# Playbook maintenance

The playbook is the list of provisions the system looks for. The Administrator role owns it (brief,
section 3).

## What an entry holds
- **Name**: what reviewers see, such as "Cap on liability".
- **CUAD category**: the matching CUAD label. The text rules (`core/rules.py`) and the evaluation use it.
- **Default severity**: low, medium or high. New findings for the provision start at this severity.
- **Method**: how the system looks for it automatically: `rules` (a text rule in `core/rules.py`) or `ai`
  (the AI step). This is the brief's rules-versus-model split (section 9). Choose it per provision from the
  evaluation results.
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

## Keywords (added 2026-09-17)

Each provision can carry keywords: words or phrases searched in every clause, whatever the provision's
method is. They are for a category where a word list genuinely helps, and for an administrator who needs to
react to something without waiting for a developer.

Two ways to set them:

- **In the running site.** Log in as the administrator, open `/admin/`, choose Provisions, open the provision,
  and type one word or phrase per line in Keywords. It takes effect on the next agreement read.
- **In `seed/playbook.csv`.** Put them in the `keywords` column separated by semicolons, then run
  `python manage.py load_playbook`. The deployed site does this on every restart, so the CSV wins in the end:
  anything typed in the admin screen and not written into the CSV is overwritten on the next deploy.

How matching works: capital letters and spacing do not matter, and a word also matches the start of a longer
one, so "indemnif" finds "indemnification". A keyword finding is labelled "Playbook keyword" and never repeats
a finding the rules or the AI already made.

Measure before trusting: `python manage.py evaluate_identification --method rules` scores the text pass,
keywords included. The uncapped liability attempt on 2026-09-17 found none of the labeled clauses and every
flag it raised was wrong (`docs/playbook-selection.md`), which is why that category has no keywords.

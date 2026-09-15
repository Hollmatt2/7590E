# Change log

Every change to the project's scope or requirements, newest first. The sponsor asked for Change Notice 1 to be recorded here.

| # | Date | Source | What changed | Effect on this project |
|---|---|---|---|---|
| 1 | 2026-09-09 | Sponsor: Change Notice 1 (eLC mail), amending Brief v1 sections 2, 4, 5 and 8 | Comparison to standard positions, deviation characterization and gap detection moved from required to stretch. The AI component now only identifies whether each playbook provision is present, and returns the supporting text and a confidence indicator. The reporting question became "which provisions come up most often across submitted agreements". | Required workflow: intake, ingestion and segmentation, identification, flag generation, review, disposition, record, reporting. `core/models.py` updated 2026-09-14: flags default to a new "Provision found" kind; the deviation and gap kinds and the playbook's standard-position fields are kept for stretch work, as the sponsor asked; confidence may be empty on flags a person made by hand. Build order follows the sponsor's advice: the whole app with manual identification first, the AI second, and the manual path kept afterwards. |

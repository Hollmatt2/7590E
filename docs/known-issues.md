# Known issues

Written honestly, as the brief asks (section 11). Update it whenever something changes.

## Reading documents
- About 5% of clauses are cut by the 3,000-character limit instead of at a heading, mostly in long contracts
  whose headings follow no pattern the splitter knows (`docs/ingestion-trial-2026-09-14.txt`).
- Scanned PDFs have no text layer and cannot be read. The agreement is marked "Could not read document";
  there is no text recognition (OCR).
- An agreement that could not be read cannot be retried in the app. It has to be submitted again.
- One contract's text matched CUAD's own text for only 92% of its words (a Soupman franchise agreement).
  Not investigated.

## Identification
- The text rules miss 20–68% of labeled clauses, and 22–73% of their flags are wrong, depending on the
  category (`docs/evaluation-rules-2026-09-14.md`). They are not reliable on their own.
- The AI step (Claude Haiku 4.5 by default) looks for eight of the ten playbook categories; text rules cover
  insurance and audit rights. Measured on the 40-contract check set on 2026-09-17
  (`docs/evaluation-ai-2026-09-17.md`). Without an API key those eight categories wait for a person.
- The AI's confidence score is its own estimate. How well it predicts correctness has not been measured yet.
- Findings removed on the identification screen are deleted, so the record does not keep wrong automatic
  findings that were removed before review.
- Playbook keywords are only as good as the words chosen. They are searched literally, so a category whose
  clauses share no common phrasing (uncapped liability) gains nothing from them; see `docs/playbook-selection.md`.

## Review and record
- A finished review cannot be reopened.
- A finding's text and clause cannot be edited after it is added; it can only be dismissed with a reason.

## Operations
- On Railway, the website and the reading step run in one service. If the reading step stops, the whole
  service restarts.
- The app sends no email notifications.

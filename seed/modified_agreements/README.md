# Modified standard agreements (brief, section 6.3)

CUAD is public, and language models have probably seen it, so scores on CUAD may reflect memory as much
as ability. This folder holds 10 standard-form agreements changed on purpose, so the correct answers are
known because we made the changes.

## Making the set

1. Take 10 standard forms from the brief's section 7.2: Common Paper, Bonterms or oneNDA (cloud service
   agreements, NDAs, DPAs, SLAs, professional services agreements). Ten are already downloaded, unchanged,
   in `base/` (sources and licenses in `base/SOURCES.md`). Copy one into this folder before changing it.
2. Change each one deliberately, as the brief suggests: remove a protection, change a liability cap, shorten a
   notice period, insert an unusual assignment clause. Save each result here as a `.txt` or `.pdf` file.
3. For every playbook provision that is present in a file, add a row to `answer_key.csv`:
   - `file`: the file name
   - `cuad_category`: the CUAD category, exactly as in `seed/playbook.csv`
   - `expected_text`: the words that show the provision (copied from the file)
   - `note`: what you changed, if this provision was part of a change
   A category with no row for a file counts as absent from that file. So a removed protection is recorded
   by leaving its row out.
4. Run `python manage.py evaluate_modified`. The report goes to `docs/`.

Record the source of each base document (with its license) and every change in the `note` column, so the
test can be repeated.

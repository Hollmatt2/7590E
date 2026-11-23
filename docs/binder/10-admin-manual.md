# 10. Administrator manual (outline)

For the administrator role. In the live site you also have the same pages as a reviewer: Work queue, Reports, Submit an agreement and My submissions. The site shows button and menu names in capital letters; this manual writes them as they are in the page text.

Screens you use are in Django's built-in admin at `/admin/` (add `/admin/` to the site address). Only a user with the Administrator role can open it. Log out with the Log out button at the top right.

## 1. Log in
1. Go to the site address and select Log in.
2. Enter your username and password and select Log in.
3. Add `/admin/` to the address to open the admin screens.

## 2. Manage users and roles
Roles: Requester, Reviewer, Approver, Administrator.

Add a user:
1. In `/admin/`, under Users, select Add user.
2. Enter a username and password, then save.
3. On the next page, find the section "Calder role" and choose the role. Add the email if you want it recorded. Save.

Change a role: open the user in Users, change the role in "Calder role", Save.

Remove access: on the user's page, clear the Active box and Save. Do not delete users who have made decisions: their names are part of the record.

Notes:
- A user needs the Administrator role to be treated as an administrator by the app. [CONFIRM: a new user with role Administrator does not automatically get "Staff status" or "Superuser status"; the demo seeding sets both. To let a new administrator open `/admin/`, tick both boxes on the user's page.]
- Nobody reviews an agreement they submitted.
- There is no self-service sign-up or password reset page. An administrator sets a new password from the user's page.

## 3. Playbook provisions
Open Provisions. Each row is one provision the system looks for. Fields:
- Name: what reviewers see.
- CUAD category: the matching label used by the rules and the evaluation.
- Default severity: Low, Medium or High. New findings start at this level.
- Method: "Text rule" or "AI model". Choose from the evaluation results (`docs/evaluation-*.md`).
- Agreement types: comma-separated codes (`software`, `services`, `licensing`, `logistics`, `dpa`, `other`). Empty means every type. A provision that does not apply is not looked for and is not offered on the identify screen.
- Keywords: one word or phrase per line, searched in every clause. Takes effect on the next agreement read. A keyword finding is labeled "Playbook keyword".
- Definition: what counts as the provision. The AI step uses it.
- Standard position and Required: not used.

Cautions:
- `seed/playbook.csv` is the source of truth. The site reloads it every time it starts, so edits made here are overwritten at the next deploy unless you also put them in the CSV (`docs/playbook-maintenance.md`).
- Changing the playbook does not re-run finished reviews.
- A provision can be deleted only while no finding uses it.
- Test a change before relying on it: `evaluate_identification` (`docs/playbook-maintenance.md`).

## 4. Thresholds and configuration
Open Configuration (one row; it cannot be added to or deleted).
- AI low confidence: AI findings below this value are marked "Low confidence: check carefully" and listed last on the review page. Nothing is hidden. The current value is 0.9 (`docs/threshold-note.md`). Lowering it marks fewer findings; raising it marks more. It takes effect on the next page load, including for agreements already in review.
- Document retention days: 0 keeps every uploaded file. Set a number of days and run `python manage.py purge_documents --dry-run`, then `python manage.py purge_documents`, on the server (`docs/deployment-runbook.md`). It deletes the file only. The agreement, findings, decisions and outcome stay, and the agreement page records the date the file went.

## 5. Reports
Select Reports in the top menu.
- Agreements waiting, by stage: count, median days waiting and longest wait for each stage. The line below shows how many reviews are finished and the median days from submission to outcome.
- Provisions found most often: for each provision, times found, number of agreements, and how many findings were Accepted, Dismissed and Escalated. A provision that is often dismissed is producing wrong flags.

There is no export. [CONFIRM: no CSV or print export exists in the app.]

## 6. When the AI is down or switched off
- The app keeps working. If the AI step cannot run (no key, key rejected, rate limit, connection or service error), the reason is written to the log and the agreement waits in the Work queue under "Waiting for identification". Provisions with the text-rule method are still found.
- Reviewers add the rest on the Identify provisions screen by highlighting words and choosing the provision (chapter 11).
- If the key has expired or is wrong, set a new `ANTHROPIC_API_KEY` on the server and restart (`deploy/lightsail/README.md`). Agreements already waiting are not re-run by the AI. [CONFIRM: confirm that automatic identification runs once per agreement; the code skips an agreement that already has automatic findings, but an agreement where the AI failed has none for the AI provisions, and whether a restart retries it was not tested.]
- To run without the AI on purpose, set `AUTO_IDENTIFY=rules`.
- Logs: `ssh -i ~/.ssh/lightsail-bgcraft.pem ubuntu@100.59.211.221 docker logs --tail 50 calder-web-1`.

## 7. Scanned PDFs and unreadable files
- A PDF with no text layer (a scan) cannot be read. The system has no OCR.
- The agreement is marked "Could not read document" and appears in the Work queue under "Could not read the document". The agreement page shows the reason.
- It cannot be retried in the app. Ask the requester to submit a text-based PDF or a .txt file as a new agreement. [CONFIRM: whether Calder wants OCR added; that is future work.]
- Accepted files: PDF or .txt, with a size limit set by `MAX_UPLOAD_MB`.

## 8. Routine checks
After every deployment, run the list in `docs/deployment-runbook.md` ("Check after every deployment"): the home page loads over https, each role can log in, the Work queue moves new agreements from "Not read yet" to "Waiting for identification", and `/admin/` is styled.
If an agreement stays "Not read yet", the reading step has stopped. Read the logs.

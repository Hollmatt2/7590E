# 11. User manual (outline)

For requesters, reviewers and approvers. The site shows button and menu names in capital letters; this manual writes them as they appear in the page text. The page title of each screen is in quotes.

Demo logins: `requester`, `reviewer`, `approver` (password from your administrator).

## What each role can do

| | Requester | Reviewer | Approver |
|---|---|---|---|
| Submit an agreement | yes | yes | yes |
| My submissions | yes | yes | yes |
| Work queue and Reports | no | yes | yes |
| Open any agreement | only your own | any | any |
| See findings, notes and history | no (status and outcome only) | yes | yes |
| Identify provisions | no | yes | yes |
| Decide findings and record an outcome | no | In-review agreements | In-review and escalated agreements |

You cannot review an agreement you submitted yourself.

## 1. Log in and out
1. Select Log in, enter your username and password, select Log in.
2. Your name and role show at the top. Select Log out when done.
3. A requester lands on "My submissions". A reviewer or approver lands on "Work queue".

## 2. Requester: submit an agreement
1. Select Submit an agreement in the top menu.
2. Fill in the form: Vendor, Agreement type, Business unit, Needed by, and the Document (a PDF or .txt file; scanned PDFs cannot be read).
3. Select Submit. A message confirms it is waiting to be read.
   - The needed-by date cannot be in the past. Files that are not PDF or .txt, are too large, or are not really PDFs are refused with a message.
4. Select My submissions to follow it. The Status column shows where it is:
   - Submitted, Reading document: the system is reading it. This takes seconds to a minute.
   - Waiting for identification, In review: a reviewer is working on it.
   - Escalated: the approver has it.
   - Cleared, Cleared with conditions: finished. Open the agreement to see the outcome and any conditions you must meet.
   - Could not read document: the file was a scan or damaged. Submit a text-based PDF as a new agreement.
5. You see the status and outcome. You do not see findings or reviewer notes.

## 3. Reviewer or approver: find work
1. Select Work queue. Agreements are grouped under: Waiting for identification, In review, Escalated, Could not read the document, Not read yet. The earliest "Needed by" date is first.
2. Select a vendor name to open the agreement page. It shows the details, outcome, findings, notes, history and clauses.
3. To check a word, use "Search this agreement" on the agreement page and select Search. It finds the exact words you type, in any capitalization, not the idea behind them. Select Clear to return.

## 4. Reviewer or approver: identify provisions
An agreement "Waiting for identification" has had the text rules and AI run where they could, and needs a person to finish.
1. Open the agreement and select "Identify provisions in this agreement".
2. The screen "Identify provisions" lists the clauses on the left and the findings so far on the right, each with who or what found it (Text rule, Playbook keyword, AI model, Marked by a person).
3. To add a finding, highlight the words in one clause. A box appears: choose the provision under "This is" and select Add finding. (The form on the right does the same: choose Provision, Clause and Supporting text, then Add finding. The text must appear in the chosen clause.) A selection that crosses two clauses is ignored.
4. To drop a wrong automatic finding, select Remove under it.
5. When done, select "Finish identification and send to review". The agreement moves to In review and the findings become part of the record.

## 5. Reviewer or approver: review and record the outcome
1. Open an agreement that is In review and select "Review the findings and record the outcome".
2. For each finding you see the provision, severity, clause number, how it was found, confidence for AI findings, and the clause with the supporting words highlighted. Findings marked "Low confidence: check carefully" are listed last. Read them with extra care; the AI is wrong on most of them.
3. Choose Accept, Dismiss or Escalate, write a Reason (required), and select Record decision. Reasons are kept. A later decision does not remove an earlier one.
4. "Add a finding identification missed": if you see a provision the system did not flag, choose Provision, Clause and Supporting text, and select Add finding. Then decide it like the others.
5. Notes: write an internal note and select Add note. Requesters never see notes. Notes cannot be edited or deleted; a correction is another note.
6. "Outcome for the agreement": the form appears only after every finding has a decision. Choose Cleared, Cleared with conditions, or Escalated. Cleared with conditions needs the Conditions text. Select Record outcome.
   - If any finding was escalated, only Escalated is offered.
   - A finished review cannot be reopened.
7. A system finding says which provision is present, not which way it favors Calder. Read the highlighted words. A contract that returns no findings is not proven clean.

## 6. Approver: escalated agreements
1. In Work queue, open an agreement under Escalated.
2. Select "Review the findings and record the outcome". Review the findings and the reviewer's notes and history.
3. Record the outcome: Cleared or Cleared with conditions. Select Record outcome.

## 7. Reports (reviewer and approver)
Select Reports for waiting agreements by stage and the provisions found most often, with how many were Accepted, Dismissed and Escalated. Chapter 10, section 5, explains the columns.

## 8. If something goes wrong
- "Forbidden" page: you do not have that role, or you are trying to review your own submission.
- An agreement stays under "Not read yet": tell the administrator. The reading step may have stopped.
- No findings on an agreement you expected to have some: the AI may have been unavailable. Use the clause search and "Add a finding identification missed".
- No email notifications are sent. Check the Work queue or My submissions.

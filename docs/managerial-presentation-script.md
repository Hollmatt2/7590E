# Managerial storytelling presentation: video script

A draft for the 10/7 presentation, sent in as a video. The audience is Calder's two sponsors: the Director of
Procurement, who wants throughput, and the Associate General Counsel, who wants accuracy. Speak to them as the
client, not as a professor grading code. No stack, no file names on screen unless asked.

About 9 minutes at a normal speaking pace. Lines in **[brackets]** are what to show on screen. Every number comes
from a real run and the source is named in the notes at the end, in case you are asked.

Put it in your own words before recording. Where a line says "I decided", it is a decision recorded under your
name in the logs; if you would now decide differently, change the line and tell me so the logs match.

---

## 1. The problem, in Calder's words (about 1 minute)

**[Slide: "200 agreements a year. Legal sees 40."]**

Calder signs more than two hundred vendor agreements a year. Legal sees about forty of them. The rest get signed
by a regional manager who scrolled to the signature block.

Last spring that cost you twice. Three business units signed agreements with uncapped indemnification. And one
agreement renewed itself because nobody tracked a ninety-day notice window. You caught it eleven days too late.

You told us you are not asking to replace your attorneys. You asked for a first pass that says which forty of
those two hundred need an attorney, and why. And you gave one warning: if the tool misses something real,
people stop trusting it, and you are worse off than before.

That warning drove most of my decisions, so I will come back to it.

## 2. What changes for each of you (about 1.5 minutes)

**[Screen: the live app, logged in as the requester, submitting a contract]**

For a regional manager, the change is small on purpose. They upload the agreement, pick the vendor, the type,
their business unit, and when they need it signed. Then they can see where it stands on one page.

**[Screen: the reviewer's work queue, then a review page with highlighted findings]**

For Legal, the change is in what arrives. The system reads the contract, splits it into clauses, and flags ten
kinds of provision. Each flag shows the exact words in the contract that triggered it, highlighted. Your reviewer
accepts, dismisses or escalates each one, and every one of those needs a written reason.

**[Screen: an escalated agreement, then the outcome options]**

Anything escalated goes to an approver, who decides the outcome: cleared, cleared with conditions, or escalated.
The requester sees the outcome and any conditions.

**[Screen: the Reports page]**

For Procurement, the reports page shows what is waiting at each stage, how long reviews take, and which
provisions turn up most often across everything submitted.

One thing it does not do: it never decides anything. It points at clauses. A person makes every call, and every
call is recorded with who made it and why.

## 3. The decisions I made, and why (about 3 minutes)

**[Slide: the five decisions as a list]**

The brief left a lot open on purpose. Here are the five decisions that matter most to you.

**First: the system advises; it does not block.** I could have made it hold up a requester until Legal signs
off. I decided against that, because the software cannot actually stop a manager signing a PDF that arrived by
email. That is how the problems last spring happened. Claiming to block would be claiming control it does not
have. Instead, it makes the status visible, and the reports show Procurement who is going ahead without a review.
Enforcing that is a Calder policy, not a software feature.

**Second: ten provisions, chosen from your own story.** The contract dataset I tested on labels forty-one kinds
of clause. I kept ten. Each one had to pass two tests: does it connect to a problem Calder has described, and are
there enough labeled examples to measure how well the system finds it. The four I rated high severity are the
ones behind your two failures: uncapped liability and caps on liability, auto-renewal and the notice period to
stop it. I dropped exclusivity and warranty duration. You never raised either, and they measured worst.

**Third: for each provision, a simple text rule or the AI, decided by measurement.** I tested both methods on the
same forty contracts against lawyers' labels. The AI was better on eight of the ten. For governing law, for
example, the AI found 90 percent of the clauses and was wrong on 5 percent of its flags, while the text rule was
wrong on 60 percent. Insurance stays on the text rule because the rule finds more of them, and for you a miss
costs more than a wrong flag. Audit rights stays on the rule because the two tied and the rule is free.

**Fourth: nothing is ever hidden.** The AI gives every finding a confidence score. I could have hidden the
low-confidence ones to make the review page cleaner. I decided not to, because a hidden finding is exactly the
silent miss you warned about. Instead, anything below 0.9 is marked "check carefully" and listed last. I put the
line at 0.9 because that is where the score starts to mean something: below it, three flags in four are wrong;
above it, about one in eleven.

**Fifth: the system still works with the AI switched off.** If the AI service is down, or Calder decides not to
use it, a person can go through the clauses and tag provisions by highlighting the words. The record and the
reports work the same either way.

## 4. How well it works, honestly (about 1.5 minutes)

**[Slide: three groups, "Reliable", "Useful with checking", "Not reliable"]**

I will not give you one accuracy number, because it would hide the part you most need to know.

Three provisions are reliable enough to act on: governing law, auto-renewal, and the notice period to stop a
renewal. That last one is the clause behind the renewal you caught eleven days late, and the system finds 88
percent of them.

Six are useful with a reviewer checking: assignment, change of control, termination for convenience, the cap on
liability, insurance, and audit rights.

One is not reliable, and it is uncapped liability, which is your first stated problem. The system finds about a
quarter to a third of those clauses, and most of its flags are wrong. These clauses are usually written as
exceptions to a liability cap, worded differently in every contract, so neither the AI nor a keyword list picks
them up well. I kept it in, marked, rather than drop it to make the averages look better. Until it improves,
Legal should read the liability section of every agreement themselves.

I also tested ten standard agreements that I changed on purpose. The system held up on most provisions. One
finding matters for you: when I rewrote an assignment clause so it favored the vendor instead of protecting
Calder, the system still flagged "assignment", but it could not tell the protection had been reversed. A reviewer
reading the highlighted words would see it in seconds. That is why every flag shows the exact text.

## 5. What real users told me (about 1 minute)

**[Fill in after the usability sessions. The brief requires them before this presentation.]**

I ran [number] sessions with [roles, not names: for example, "a procurement analyst" and "a classmate on
another team"]. I gave them goals, not instructions, and watched.

The main thing I saw was [what they did]. Because of that, I [changed X / decided not to change X because Y].

[A session that changed nothing still counts. Say what you saw and why you left it alone.]

## 6. What is next, and what I need from you (about 1 minute)

**[Slide: "Next" and "Your call"]**

Next, I want to improve uncapped liability, since it is the gap that matters most to you, and finish testing
with harder PDF formats, like scanned and badly formatted documents.

There are two decisions that belong to Calder rather than to me:

- Whether to make review a required step before signing. The software can report who skipped it, but only a
  Calder policy can require it.
- Whether to accept the current trade-off: more wrong flags for your reviewers to dismiss, in exchange for fewer
  missed clauses. I have set it up that way because of what you told me, but it is your attorneys' time being
  spent.

Thank you.

---

## Notes for you, not for the video

- **Sources for every number.** Governing law 90% / 5% and rule 60% wrong, notice period 88%:
  `docs/evaluation-ai-2026-09-17.md` and `docs/playbook-selection.md`. The 0.9 line and "three in four" and
  "one in eleven": `docs/threshold-note.md`. Reliable / useful / not reliable groups and the assignment
  reversal: `docs/verification.md`. Advisory, not blocking: ambiguity log entry 1.
- **Recording without the live site.** Railway is down right now. You can record the screen parts from a local
  copy instead: `/home/hollmatt1/calder-backup-demo.sh` runs the app on the laptop with the demo logins. Tell me
  if you want me to bring the live site back first.
- **Citing AI help.** The syllabus asks for AI-generated writing to be cited with the prompt and response in an
  appendix. This script was drafted by Claude from the project's logs.

# Managerial storytelling presentation: video script

The 10/7 presentation, recorded and sent in as a video (Dr. Srinivasan asked for it this way on 10/23). Upload it to
the eLC dropbox "Managerial Presentation_10_07_2026". The audience is Calder's two sponsors: the Director of
Procurement, who wants throughput, and the Associate General Counsel, who wants accuracy. Speak to them as the
client, not as a professor grading code. No stack, no pipeline diagram, no file names.

About 10 minutes at a normal speaking pace. It follows the final-practice slides
(`/home/hollmatt1/Projects/calder-review/docs/final-practice-slides.html`) in the same order, so you can record with
them on screen. Lines in **[brackets]** say which slide or screen to show. Skip slide 8 (Questions); it lists code
files, which this audience does not want.

Put it in your own words before recording. Where a line says "I decided", it is a decision recorded under your
name in the logs; if you would now decide differently, change the line and tell me so the logs match.

---

## 1. Opening (about 20 seconds)

**[Slide 1: title]**

I'm Matt Holliday. This is the vendor agreement review assistant I built for Calder Industrial Supply. I'll cover
the problem, show you what the system does, walk through the five decisions behind it, tell you how well it
works, and say what's left.

## 2. The problem, in Calder's words (about 1 minute)

**[Slide 2: The problem]**

Calder signs more than two hundred vendor agreements a year. Legal sees about forty of them. The rest get signed
by a regional manager who scrolled to the signature block.

Last spring that cost you twice. Three business units signed agreements with uncapped indemnification. And one
agreement renewed itself because nobody tracked a ninety-day notice window. You caught it eleven days too late.

You told us you are not asking to replace your attorneys. You asked for a first pass that says which agreements
need an attorney, and why. And you gave one warning: if the tool misses something real, people stop trusting it,
and you are worse off than before.

That warning drove most of my decisions, so I will come back to it.

## 3. What changes for each of you (about 2 minutes)

**[Slide 3: What it does. Hold it for one sentence, then switch to the live site.]**

Here is the whole path an agreement takes: someone submits it, the system reads it and points out the clauses
that matter, a reviewer checks each one, an approver gives the outcome, and everything is recorded.

**[Screen: logged in as the requester, submitting an agreement]**

For a regional manager, the change is small on purpose. They upload the agreement, pick the vendor, the type,
their business unit, and when they need it signed. Then they can see where it stands on one page. They don't
wait for anything; the reading happens in the background.

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

## 4. The decisions I made, and why (about 3 minutes)

**[Slide 4: My decisions. Go one row at a time.]**

The brief left a lot open on purpose. Here are the five decisions that matter most to you.

**First: the system advises; it does not block.** I could have made it hold up a requester until Legal signs
off. I decided against that, because the software cannot actually stop a manager signing a PDF that arrived by
email. That is how the problems last spring happened. Claiming to block would be claiming control it does not
have. Instead, it makes the status visible, and the reports show Procurement who went ahead without a review.
Enforcing that is a Calder policy, not a software feature.

**Second: ten provisions, chosen from your own story.** The contract dataset I tested on labels forty-one kinds
of clause. I kept ten. Each one had to pass two tests: does it connect to a problem Calder has described, and are
there enough labeled examples to measure how well the system finds it. Four are rated high severity, and they are
the ones behind your two failures: uncapped liability and caps on liability, auto-renewal and the notice period to
stop it. I dropped exclusivity and warranty duration. You never raised either, and they measured worst.

**Third: for each provision, a simple text rule or the AI, decided by measurement.** I tested both methods on the
same forty contracts against lawyers' labels. The AI was better on eight of the ten. For governing law, for
example, the AI found 90 percent of the clauses and was wrong on 5 percent of its flags, while the text rule was
wrong on 60 percent. Insurance and audit rights stay on text rules: for insurance the rule finds more of them,
and for you a miss costs more than a wrong flag; for audit rights the two tied and the rule costs nothing to run.

**Fourth: nothing is ever hidden.** The AI gives every finding a confidence score. I could have hidden the
low-confidence ones to make the review page cleaner. I decided not to, because a hidden finding is exactly the
silent miss you warned about. Instead, anything below 0.9 is marked "check carefully" and listed last. I put the
line at 0.9 because that is where the score starts to mean something: below it, three flags in four are wrong;
above it, about one in eleven.

**Fifth: the system still works with the AI switched off.** If the AI service is down, or Calder decides not to
use it, a person can go through the clauses and tag provisions by highlighting the words. The record and the
reports work the same either way.

## 5. How well it works, honestly (about 1.5 minutes)

**[Slide 5: How well it works]**

I will not give you one accuracy number, because it would hide the part you most need to know.

Three provisions are reliable enough to act on: governing law, auto-renewal, and the notice period to stop a
renewal. That last one is the clause behind the renewal you caught eleven days late, and the system finds 88
percent of them.

Six are useful with a reviewer checking: assignment, change of control, termination for convenience, the cap on
liability, insurance, and audit rights.

One is not reliable, and it is uncapped liability, which is your first stated problem. The system finds about 30
percent of those clauses, and 71 percent of its flags are wrong. These clauses are usually written as exceptions
to a liability cap, worded differently in every contract, so neither the AI nor a keyword list picks them up well.
I kept it in, marked, rather than drop it to make the averages look better. Until it improves, Legal should read
the liability section of every agreement themselves.

I also tested ten standard agreements that I changed on purpose. One finding matters for you: when I rewrote an
assignment clause so it favored the vendor instead of protecting Calder, the system still flagged "assignment",
but it could not tell the protection had been reversed. A reviewer reading the highlighted words would see it in
seconds. That is why every flag shows the exact text.

## 6. What's left, and what I need from you (about 1.5 minutes)

**[Slide 6: What's left, and next]**

Four things are still open.

First, I have not yet tested it with people outside the project. I will run two or three sessions before the
final version, giving people goals rather than instructions and watching where they get stuck.
**[If you have run sessions by the time you record, replace this with: how many, their roles (not names), the
main thing you saw, and what you changed or chose not to change and why.]**

Second, scanned documents. If an agreement is a scanned image rather than a real PDF, the system says it could
not read the document and puts it in front of a person. It does not try to read scanned text yet.

Third, uncapped liability, which I covered. It is the biggest gap that matters to Calder.

Fourth, hosting. In late October the hosting service I started on went down, so I moved the system to a server
I run myself. It has been up since November 3. The trade-off is that keeping it running is now my job.

And there are two decisions that belong to Calder rather than to me:

- Whether to make review a required step before signing. The software can report who skipped it, but only a
  Calder policy can require it.
- Whether to accept the current trade-off: more wrong flags for your reviewers to dismiss, in exchange for fewer
  missed clauses. I have set it up that way because of what you told me, but it is your attorneys' time being
  spent.

## 7. In short (about 30 seconds)

**[Slide 7: In short]**

To sum up. Calder signs more than two hundred agreements a year, Legal sees about forty, and real risks were
signed without anyone seeing them. The system reads every agreement, points at ten kinds of provision with the
exact words, and a person decides. I chose rules or AI for each provision by measuring both on forty contracts.
It is reliable on governing law, auto-renewal and the renewal notice period. It is not yet reliable on uncapped
liability, and it tells you so. Next come the user sessions, scanned documents, and uncapped liability.

Thank you.

---

## Notes for you, not for the video

- **Sources for every number.** 200+, ~40, 3, 11: the project brief. Governing law 90% / 5% and rule 60% wrong,
  notice period 88%: `docs/evaluation-ai-2026-09-17.md` and `docs/playbook-selection.md`. The 0.9 line, "three in
  four" and "one in eleven": `docs/threshold-note.md`. Reliable / useful / not reliable groups, uncapped liability
  30% found and 71% wrong, and the assignment reversal: `docs/verification.md`. Advisory, not blocking: ambiguity
  log entry 1. Hosting move on 11/3: `deploy/lightsail/` (the risk log
  still describes Railway and needs an entry for the outage).
- **Recording.** The live site is https://calder.100-59-211-221.nip.io (Lightsail). The demo logins are the same
  ones as for the final practice; the password is in `/home/hollmatt1/calder-demo-password.txt`. Use the same
  three-window setup as `/home/hollmatt1/calder-demo-script-1118.md` for the screen parts.
- **How to record.** Zoom works: start a meeting by yourself, share your screen, click Record, and Zoom saves the
  video when you end the meeting (it shows the folder it saved to).
- **Citing AI help.** The syllabus asks for AI-generated writing to be cited with the prompt and response in an
  appendix. This script was drafted by Claude from the project's logs and slides.

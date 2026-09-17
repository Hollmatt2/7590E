# Threshold note

Brief section 6.4. Decisions made 2026-09-17 by Matt Holliday, from the check-set run of Claude Haiku 4.5
on 40 CUAD contracts (`docs/evaluation-ai-2026-09-17.md`, answers saved in `data/evaluations/ai-2026-09-17.json`).

## What the evidence shows

The AI returned 243 findings across the eight categories it handles. Their confidence scores are not spread
evenly: 172 sit at 0.9 or above, and only 9 fall below 0.5.

| Confidence band | Findings | Of those, wrong |
|---|---|---|
| 0.9 and above | 162 located in the contract text | 14 (9%) |
| Below 0.9 | 66 | 50 (76%) |

Moving the bar changes both numbers together, measured across the eight AI categories:

| Bar | Labeled clauses found | Flags raised | Flags wrong |
|---|---|---|---|
| Show everything | 165 of 260 (63%) | 228 | 64 (28%) |
| 0.5 | 164 (63%) | 220 | 57 (26%) |
| 0.8 | 161 (62%) | 196 | 36 (18%) |
| 0.9 | 149 (57%) | 162 | 14 (9%) |

Reading that: going from "trust everything" to "trust only 0.9 and above" removes 50 wrong flags and loses 16
real clauses.

## 1. Where the threshold sits, and why

**The confidence score does not decide whether a finding is shown. It decides whether the finding is marked
"check carefully" and sorted to the bottom of the review page. The line is 0.9.**

Nothing is hidden, because a suppressed finding is exactly the failure the client described. So the only
question is where the mark earns its place, and 0.9 is where the score starts predicting something. Below it,
three flags in four are wrong: the mark is a real warning. At or above it, one in eleven is wrong.

The 0.5 default the system started with marked 9 findings out of 243, under 4%, and left most of the wrong
flags unmarked and sitting at the top of the page. It looked like a safeguard and was not one.

The threshold is the `AI_LOW_CONFIDENCE` setting, so changing it is a deployment setting, not a code change.

## 2. Which is worse for Calder: a wasted reviewer hour, or a silent miss

**A miss is worse, and it is not close.**

Calder said it in their own words: "If it misses something real, people stop trusting it, and then we are
worse off than before we had it. Nobody double-checks a tool they think is reliable." The system exists
because 160 of their 200 agreements a year are signed by a regional manager who scrolled to the signature
block. A wrong flag costs a reviewer the time to read one clause and dismiss it, and the dismissal is recorded.
A miss puts an uncapped indemnity into a signed contract, and nobody finds out until it is claimed against.

That asymmetry is why the low-confidence behaviour is marking rather than suppression, and why insurance stays
on a text rule that finds more (41%) rather than the AI that is cleaner but finds less (26%).

The argument has a limit, and it is worth being honest about it: noise has a cost too, but it is a cost paid
by an attentive reviewer who sees a bad flag and gets to say so, not by the company signing a contract nobody
read. Between a reviewer's hour and an unlimited liability, Calder chose the hour.

## 3. What the threshold means in practice

- The app shows every finding. About three in ten of the AI's findings arrive marked "check carefully", and
  those contain most of what is wrong.
- The system finds about 63% of the clauses the expert labels say are there, across the eight AI categories.
  That number is the one that matters, and it is not near 100%.
- It varies enormously by category: governing law 90%, renewal notice 88%, auto-renewal 85%, assignment 62%,
  change of control 64%, termination for convenience 63%, cap on liability 46%, uncapped liability 30%.
- So roughly a third of what the labels call a provision does not reach a reviewer as an automatic finding.
  For uncapped liability, Calder's own stated problem, it is closer to two thirds.
- Text rules cover the other two categories (insurance 41% found, audit rights 32%), and a reviewer can add
  any finding by hand on the identification and review screens.
- Every agreement page now has a clause search. Typing words finds every clause containing them, exactly,
  every time. That is a genuine backstop, with one honest limit: it matches words, not meaning. The keyword
  experiment for uncapped liability found 0 of 20 labeled clauses, because those clauses are carve-outs
  written dozens of different ways (`docs/playbook-selection.md`). Search is how a reviewer checks a specific
  suspicion, not how the system covers a category.

## 4. What I would tell the Associate General Counsel

> Rely on it to decide what to read, not to decide what is safe.
>
> When it flags something at high confidence, it is right about eleven times in twelve, and it shows you the
> exact words so you can check in seconds. That part is worth your time.
>
> It finds roughly six in ten of the provisions our test labels say are there, and fewer than that on uncapped
> liability, which is the term that hurt us. So a contract that comes back with nothing found is not a
> contract that is clean. It is a contract this system had nothing to say about.
>
> If you want certainty about a particular phrase, the search box on the agreement page is exact: it will find
> every clause containing the words you type, every time. What it cannot do is tell you the idea is absent,
> because the clause you are looking for may not use your words.
>
> And one caveat on the numbers themselves: they come from a public contract set the model may have seen in
> training. The modified-agreement test (brief section 6.3) is what will tell us whether these numbers hold on
> contracts it has never seen. Until that is done, treat them as an upper bound.

## What would change the threshold

- The modified-agreement results. If confidence predicts correctness less well on unseen contracts, 0.9 is
  re-argued on those numbers.
- Reviewer experience. If reviewers report that the marked findings are worth reading after all, the line
  moves down; if they ignore everything below it, the line is doing its job.
- A category moving between methods, since the threshold only applies to AI findings.

---

Decisions by Matt Holliday, 2026-09-17. The measurements were produced by the project's own
`evaluate_identification` command; the tables above were computed from its saved answers with Claude's help.

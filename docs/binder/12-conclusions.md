# 12. Conclusions and Final Thoughts

## What worked
- **Build first, then add the AI.** I had a deployed, working application on 15 Sep, the same day the AI step went in. The manual path became the fallback the brief asks for.
- **Per-category measurement.** Reporting found and wrong-flag rates per category showed which categories the system handles and which it does not. The choice of method per provision followed the numbers. The AI beat the text rules on 8 of 10 categories. Insurance and audit rights stayed on rules.
- **Marking low confidence instead of hiding it.** Below 0.9, 76% of findings were wrong. At 0.9 and above, 9% were. The mark gives reviewers a usable warning, and nothing is suppressed.
- **Showing the clause text.** On the modified agreements the system flagged an assignment clause whose protection I had reversed. It saw the topic and not the direction. Because the quoted words are shown, a reviewer would catch it.
- **Written logs.** The ambiguity, change and risk logs made each decision traceable.

## What did not work
- **Uncapped liability.** The system finds 30% of labeled clauses and 71% of its flags are wrong. On my modified agreements it found 1 of 4. This is one of Calder's two stated problems. A keyword list found 0 of 20 labeled clauses. My best explanation is that the clause is a carve-out from a cap and is worded differently in every contract. Until it improves, Legal should read every liability section.
- **Overall recall.** About 63% across the eight AI categories. A contract with no findings is not shown to be clean.
- **Topic, not direction.** The system does not tell whether a clause helps or hurts Calder.
- **Usability sessions are late.** The brief requires them before the managerial presentation (7 Oct). I planned two by 26 Sep and did not run them. I have no user observations yet. [CONFIRM: update this paragraph with the results if the sessions happen before 8 Dec.]
- **Source control was late.** The brief requires it from Week 2. The repository was created on 15 Sep. It is recorded in the risk log.
- **No schedule kept.** I had no plan or task board during the semester. The binder schedule is reconstructed.
- **Open items.** The 6.1 label spot-check is not done. Scanned PDFs cannot be read. Hosting moved after a Railway outage; the runbook still describes Railway.
- **Technical presentation feedback** was that I needed to make more decisions. My response was to record decisions with their evidence in the logs and to build the highlight-to-tag screen the same day.

## What is next
In order:
1. Run the usability sessions and record what I observed and changed.
2. Record the managerial video and the final video.
3. Improve uncapped liability, the largest gap that matters to Calder.
4. Add text recognition (OCR) for scanned PDFs, and test more difficult PDFs (sponsor feedback, 17 Sep).
5. Stretch work from the brief and Change Notice 1: standard positions and deviation characterization, gap detection. Gap detection depends on better identification, because each missed provision would become a false gap.

Decisions that belong to Calder: whether review is required before signing, and whether it accepts more wrong flags in exchange for fewer misses.

## Handoff
Another team could pick this up from the README, seed data, runbook, known-issues list and playbook maintenance notes. The runbook needs updating for Lightsail.

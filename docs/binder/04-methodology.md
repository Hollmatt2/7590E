# 4. Methodology

## What I did
I worked alone and did not use Scrum or any other named framework. There were no sprints, no standups and no task board. The approach was incremental and driven by measurement, using the brief and its change notice as the plan.

1. **Read the brief for what was undecided.** The brief says the ambiguities are left open on purpose. I kept an ambiguity log: question, options, decision, reasoning, consequence. It has 18 entries, the brief's 8 plus 10 found while building (`docs/ambiguity-log.md`).
2. **Control changes in writing.** Change Notice 1 and my own scope decisions went into a change log (4 entries). Risks went into a risk log (12 entries).
3. **Build the application first, with manual identification.** Change Notice 1 advised this: intake, segmentation, a screen where a person marks which provisions a contract contains, flag generation, queue, disposition, audit record, reporting, roles, deployed. I built it that way (work dated 12-14 Sep, deployed 15 Sep).
4. **Add the AI second.** The fields the manual screen collects became the fields the model returns. The AI step was added on 15 Sep. The manual path stayed, and is the answer to what happens when the AI is down.
5. **Decide each provision by measurement.** I ran text rules and the AI on the same 40 CUAD contracts and compared found and wrong-flag rates per category. The method with the better result for Calder's concern was chosen for each category. Insurance stayed on rules because rules found more (41% against 26%) and Calder's stated fear is a miss.
6. **Check against memorization.** I modified 10 standard agreements on purpose and ran the system on them.
7. **Handle sponsor feedback as it came.** After the technical presentation I built the highlight-to-tag screen the same day (change #4).

## AI-assisted development
- Claude Code wrote most of the code. The provenance log lists each module as AI-generated, substantially modified, or hand-written.
- Claude also drafted most documents, including the evaluation tables, under my direction. I made the decisions recorded in the logs and review what ships.
- To keep understanding of the code, I had two study guides written (`docs/study-guide-1-web-app.md`, `docs/study-guide-2-pipeline.md`) and walked the files before the technical presentation. The brief warns about volume without comprehension.

## Why it fit
- **Solo team.** There was no one to coordinate with, so sprint ceremonies would have added overhead and no benefit. Logs gave me the record a team would have had.
- **Uncertain requirements.** The brief was incomplete on purpose and changed once. Small changes with a written decision for each suited that.
- **Sponsor contact limited to office hours and email.** I could not ask questions continuously. The ambiguity log let me decide, record the reason, and revisit.
- **Technical risk in the AI step.** Building the working application first meant a poor model result would still leave a complete system (the sponsor's reason as well).
- **Measurable quality target.** The brief grades honest measurement. Per-category evaluation produced the evidence for each decision.

## What the approach lacked
- No schedule or task tracking during the semester. The schedule in section 5 is reconstructed from commits and dated documents.
- Source control started on 15 Sep. The brief required Week 2. The work of 12-14 Sep went in as one import commit.
- No outside user testing yet, although the brief requires it before the managerial presentation (section 12).

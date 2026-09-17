# Which provisions the playbook covers, and why

Change Notice 1 requires 8 to 12 provision categories, "selected and justified", and names the two
questions that drive the choice: does Calder's stated problem touch the category, and are there enough
labeled examples in the corpus to measure anything.

**Decision: ten categories.** Two of the brief's suggestions, exclusivity and warranty duration, are scoped
out. The evidence is CUAD's own labels (how common each category is across its 510 contracts) and the
evaluation runs on the 40-contract check set: text rules on 2026-09-14
(`docs/evaluation-rules-2026-09-14.md`) and Claude Haiku 4.5 on 2026-09-17
(`docs/evaluation-ai-2026-09-17.md`).

"Found" is recall: of the clauses the expert labels say exist, how many the method flagged. "Wrong" is the
false-flag rate: of the flags the method raised, how many matched no labeled clause.

## The ten, and why each one is here

| Provision | Severity | Found by | Why it is in the playbook |
|---|---|---|---|
| Uncapped liability | High | AI | Calder's first stated failure: business units signed agreements with uncapped indemnification. 23 labeled clauses in the check set. The weakest category we keep (26% found, 75% wrong); see the caveat below. |
| Cap on liability | High | AI | The other half of the same problem: a cap that exists is the protection Calder thought it had. The most common liability label in the corpus (54% of contracts, 69 clauses in the check set). AI: 48% found, 28% wrong. |
| Notice period to stop renewal | High | AI | Calder missed a 90-day non-renewal window by 11 days. This is the exact clause that window comes from. AI: 88% found, 24% wrong, against the rule's 47% and 27%. |
| Auto-renewal | High | AI | The other half of the renewal problem: the term that renews itself if nobody acts. AI: 86% found, 25% wrong, against the rule's 67% and 48%. |
| Termination for convenience | Medium | AI | How Calder gets out of an agreement that is not working. Both methods are weak here; the AI is the better of the two (60% found, 44% wrong, against 33% and 73%). |
| Change of control | Medium | AI | A distributor's supply can be disrupted when a vendor is acquired. Similar recall either way (60% and 63%), but the AI raises far fewer wrong flags (32% against 58%). |
| Assignment restriction | Medium | AI | Decides whether a vendor can hand the contract to someone else. Common enough to measure well (73% of contracts, 50 clauses). AI: 62% found, 9% wrong, the cleanest result after governing law. |
| Insurance requirement | Medium | Text rule | Standard procurement control for an industrial distributor with four distribution centers. The rule finds more than the AI (41% against 26%), and Calder's stated fear is a miss, not noise, so recall decides it. |
| Governing law | Low | AI | Present in 86% of contracts, so a reviewer expects to see it recorded, but it rarely changes a decision. The AI is the strongest here: 90% found, 5% wrong, against the rule's 80% and 60%. |
| Audit rights | Low | Text rule | Useful to record, rarely urgent. The two methods tie on recall (32%), so the free, instant one wins. |

## What was scoped out, and why

- **Exclusivity.** Calder never raised exclusive dealing, and a distributor buying industrial supplies is
  not the usual setting for it. The AI got 46% of its flags wrong. Scoped out deliberately; the definition
  stays in the backlog.
- **Warranty duration.** The rarest of the twelve in the corpus (15% of contracts) and the worst measured
  result (37% found, 67% wrong). Calder never raised it.

Both are in the stretch backlog rather than deleted work: adding either back is one row in
`seed/playbook.csv`.

## Which agreement types each provision applies to

Ambiguity log question 3 was decided on 2026-09-17: the playbook is scoped per agreement type. Eight of the
ten provisions apply to every type. Two do not:

- **Insurance requirement**: professional services, licensing, logistics. Physical and service work carries
  insurance obligations; flagging insurance on a SaaS subscription trains reviewers to ignore flags.
- **Audit rights**: software subscriptions, data processing addenda, logistics. These are the agreements where
  usage, data handling and delivery are the things Calder would audit.

## Severity

Severity orders a reviewer's attention; it is not a legal judgment.

- **High** is reserved for the four provisions behind Calder's two stated failures: the liability pair and
  the renewal pair.
- **Medium** covers provisions that change what the agreement is worth, but that Calder has not been hurt by.
- **Low** covers provisions a reviewer wants recorded rather than acted on.

A flag copies the severity in force when it is raised, so changing this table does not rewrite past reviews.

## Text rule or AI, category by category

Section 9 of the brief asks for this split to be made deliberately. The rule is: use the text rule where it
matched or beat the AI on the number that matters for that category, and use the AI everywhere else.

- Two categories stay on text rules. Insurance, because the rule finds more (41% against 26%) and a miss
  costs Calder more than a wrong flag. Audit rights, because the two tie and the rule is free and instant.
- Eight are on the AI, either because it beat the rule on both numbers (governing law, notice period,
  auto-renewal, assignment restriction, termination for convenience), because it raised far fewer wrong
  flags at similar recall (change of control), or because no rule can judge them (the liability pair).

The split is not permanent. Any category can move with one row change, and the evaluation command scores
both methods on the same contracts.

## Two things to say plainly

**Uncapped liability is the weakest category and the one Calder cares about most.** The AI finds a quarter of
the labeled clauses and three of every four flags it raises are wrong. It stays in the playbook, because
dropping the client's stated problem to improve the average would leave Calder worse off than before, but the
review page marks its low-confidence findings and the threshold note has to say plainly that this category
cannot be relied on yet. The next step under consideration is a third method, "a person marks it", so the
system never claims to have checked a provision it cannot check.

**Calder said "uncapped indemnification"; CUAD has no indemnification label.** Its 41 categories include cap
on liability and uncapped liability, which cover the money consequence, but not indemnification as such. That
is a gap in the provided corpus, recorded here as a scoping observation rather than worked around, as the
brief's section 7.4 asks. Measuring an indemnification category would mean labeling contracts ourselves,
which the brief rules out.

## The keyword experiment (2026-09-17)

An administrator can now add keywords to any playbook provision, and they are searched whatever the
provision's method is. The first thing tried was uncapped liability, the category the AI is weakest at.

Three phrase sets were scored on the same 40-contract check set:

| Keywords | Labeled clauses | Found | Flags raised | Wrong |
|---|---|---|---|---|
| Carve-out wording ("nothing in this agreement shall exclude or limit", "shall not limit", …) | 20 | 0 (0%) | 8 | 8 (100%) |
| Carve-out wording plus "gross negligence" and "willful misconduct" | 20 | 3 (15%) | 26 | 23 (88%) |
| Broad ("nothing in this", "shall not apply to", "without limit", "unlimited") | 20 | 3 (15%) | 175 | 172 (98%) |

**Decision: no keywords for uncapped liability.** Reading the labeled clauses explains the result. They are
carve-outs from a liability cap, written dozens of ways: liability for death or personal injury, for breach of
confidentiality, for indemnities, for gross negligence. What makes them the category is what the sentence
does to the cap, not any phrase they share. That is a judgment, so it belongs with the AI or a person, not a
word list.

The capability stays. It makes the text pass something an administrator can maintain without a developer,
which the handoff requirements need, and any keywords added are scored by the same evaluation command.

## What would change this decision

- The modified-agreement check (brief section 6.3). If accuracy drops on contracts the model has never seen,
  the method split is re-decided on those numbers, not the CUAD ones.
- A rule written for a category that currently has none. The rules were written before the check set was
  chosen; a new rule has to be scored on different contracts to be believed.
- Anything Calder says next. The playbook exists to hold their positions, not ours.

---

Drafted by Claude at Matt's request on 2026-09-17 from the evaluation results, then reviewed by Matt. The
decisions above are the ones he will defend; the severity table in particular is a judgment he should confirm
before the binder.

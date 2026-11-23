# 1. Executive Summary

**Project:** Vendor Agreement Review Assistant for Calder Industrial Supply (fictional client). MIST 7590E, Fall 2026. Solo team: Matt Holliday. Sponsor: Dr. Nikhil Srinivasan, who plays both the Director of Procurement and the Associate General Counsel.

**Problem.** Calder signs more than 200 vendor agreements a year. Legal sees about 40. Last spring three business units signed agreements with uncapped indemnification, and one auto-renewal was caught 11 days too late. Calder asked for a first pass that says which agreements need an attorney, and why. It did not ask to replace its attorneys.

**What I built.** A Django 6 / Python 3.14 / Postgres web application with four roles (Requester, Reviewer, Approver, Administrator). A requester uploads an agreement. The system reads the text, splits it into clauses, and identifies which of ten playbook provisions are present. Each finding shows the exact clause text and a confidence score. A reviewer accepts, dismisses or escalates each finding with a reason. The agreement is then cleared, cleared with conditions, or escalated. Every decision is recorded. A reports page shows what is waiting, how long reviews take, and which provisions appear most often.

**How identification works.** Claude Haiku 4.5 identifies eight of the ten provisions. Text rules identify the other two (insurance, audit rights). A person can identify any provision by hand by highlighting words in a clause. The manual path stays in the application permanently, so the system still works when the AI is off.

**Scope change.** Change Notice 1 (9 Sep) cut the required scope to presence identification. Standard-position comparison and gap detection moved to stretch. I did not build them.

**How well it works.** I measured it on a 40-contract set from CUAD, per category, and on 10 standard agreements I modified on purpose.
- Reliable: governing law (90% found, 5% of flags wrong), notice period to stop renewal (88%, 24%), auto-renewal (86%, 25%).
- Not reliable: uncapped liability (30% found, 71% of flags wrong). This is one of Calder's two stated problems. I kept it in the playbook, marked, and report it as a limitation.
- Across the eight AI categories the system finds about 63% of the clauses the expert labels say exist. A contract with no findings is not shown to be clean.
- Findings below 0.9 confidence are marked "check carefully" and listed last. Nothing is hidden.

**Status on 23 Nov 2026.**
- Deployed at https://calder.100-59-211-221.nip.io on an AWS Lightsail server since 3 Nov. It moved from Railway after a Railway outage.
- Not done: usability sessions with outside users, the 6.1 label spot-check, the recorded managerial presentation, the binder, and the final video (all due by 8 Dec).

**AI use.** Claude (Claude Code) wrote most of the code and drafted the documentation under my direction. The provenance log lists each module. I review and own everything that ships.

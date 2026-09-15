# Risk log

Graded (syllabus). One row per risk. "Seen so far" records what has actually happened. Likelihood, impact,
response and status are Matt's to set and keep current. The brief requires a committed API key to be
rotated and recorded here (section 9).

| # | Risk | Seen so far | Likelihood | Impact | Response | Status |
|---|---|---|---|---|---|---|
| 1 | PDF text extraction fails on some contracts (brief §9 warning) | 30 of 30 CUAD PDFs read; median 98% of words match CUAD's text (2026-09-14) | | | | |
| 2 | Clause splitting misses section headings | 5% of clauses cut by length, mostly in 4 long contracts | | | | |
| 3 | Wrong flags make reviewers stop trusting the system (brief §1) | 22–73% of text-rule flags wrong, by category | | | | |
| 4 | No AI provider or key chosen yet | none on the development laptop as of 2026-09-14 | | | | |
| 5 | The AI service is down or slow | not built yet; manual identification is the fallback | | | | |
| 6 | An API key or secret is committed to the repository | none; the secret key was moved to an environment variable before the first commit | | | | |
| 7 | One person does all building, documentation and presentations | solo team since 8/27 | | | | |
| 8 | AI-written code that I cannot explain (brief §12.2, §12.3) | most modules are AI-generated (see the provenance log) | | | | |
| 9 | CUAD scores reflect what models memorized (brief §6.3) | modified-agreement test not started | | | | |
| 10 | A deployment setting mistake exposes the site | Deployed 2026-09-15. The first check from outside found debug mode on and the development secret key in use, because the Railway variables had not been set: logins could have been forged, and data was stored in a file inside the container that every redeploy wipes. Fixed the same day through the Railway CLI (new secret key, debug off, a private demo password, a Postgres database) and checked again from outside: debug pages gone, login cookie marked secure. An upload volume was added the same day. | | | | |
| 11 | Source control started late (brief §9 requires Week 2) | repository created 2026-09-15 (github.com/Hollmatt2/7590E); the work of 9/12–9/14 went in as its first commit that day | | | | |
| 12 | Usability sessions not done before 10/7 | not scheduled | | | | |

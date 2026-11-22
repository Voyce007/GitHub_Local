# Storyboard — discovery loop 1 (for review)

The interactive version, with real run data, a simulation replay and review
buttons, is `docs/storyboard.html`. The numbers below come from
`python -m ontokit simulate` on the fictional sample batch.

| # | Stage | Frame | What the reviewer should look at |
|---|---|---|---|
| 1 | Input | **An evidence batch arrives.** 10 files with a manifest that records provenance, date and system hint for each. | Are these the extract types you will have? Is the 5-year staleness threshold right? |
| 2 | A · Intake | **A citable source index is built.** 1 stale file (2019) can be cited but cannot raise a grade to B. | Should some files (e.g. ones with personal data) be refused, or routed to local models? |
| 3 | B · Propose | **Four persona agents read in parallel.** 159 proposals, one per source, each with a verbatim quote. | Is the split of responsibilities right? |
| 4 | C · Validate | **The validator rejects invented quotes, out-of-scope kinds and self-confirmation.** | Is two retries enough? Should rejected proposals be kept for audit? |
| 5 | D · Steward | **Aliases are resolved** only where a source says so: CustHub = CH = Customer Hub = CRM, and so on. | Stated aliases only, or fuzzy matching with human review? |
| 6 | D · Steward | **Contradictions are kept, not resolved.** 3 found: CustomerType values, PaymentStatus values, the Customer Number issuer. Also flagged: homonym and synonym candidates. | Should stale sources automatically lose? (Currently: a human always decides.) |
| 7 | E · Grade | **Every element is graded by rule.** A 0 · B 26 · C 54 · D 9 · X 3 | Is "two independent files = B" the right bar? |
| 8 | F · Reference | **Reference-model gaps become grade-D assumptions** (Person, Organisation, Product, …), never as-is fact. | Is this the right part of the reference model for your first domain? |
| 9 | G · Unknowns | **The unknowns register: 23 items, 7 high priority**, each with a named owner. Evidence requests show how many elements they would move to grade A. | Are the questions answerable in one reply? Jira straight away, or after review? |
| 10 | H · Gates | **Phases 1–3 are provisional.** Every failure is covered by an open unknown, and nothing is above B. | What should stop a provisional phase from going further? |
| 11 | I · Human gate | **Each element is routed to its approver** from the decision-rights table. Live mode never fills in decisions. | Will approvers accept "approve-provisional"? Batch by grade, by domain or by system? |
| 12 | J · Publish | **The loop publishes the ontology, inventory, glossary, unknowns, gate report and stand-in SQL** for the PoC. | Is LinkML acceptable as the source of truth? Do you want synthetic data and mock APIs too? |
| 13 | Next loop | **Answers and real code context go into loop-02, and grades rise** (planned, not simulated). | Which system's code or schema can you get first? |

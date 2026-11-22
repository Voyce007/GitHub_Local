# Storyboard — discovery loops 1 and 2 (for review)

The interactive version is `docs/storyboard.html`. It has the flow diagram
with all three loops, the real run data, a step-by-step simulation replay
for each loop, and review buttons. The numbers below come from
`python -m ontokit simulate` on the fictional, industry-agnostic sample
("Example Group": customers, products and orders, plus the Finance and Risk
functions).

```
① validator → agent (inner)   ② deferred → unknowns (inner)   ③ answers + new code → next loop (outer)
```

| # | Stage | Frame | For the reviewer |
|---|---|---|---|
| 1 | Input | **An evidence batch arrives.** 12 files from Sales, Finance, Risk and IT. | Are these the extract types your group functions will have? |
| 2 | A | **A citable source index is built.** One stale 2019 document can be cited but cannot raise a grade to B. | Should some files be refused, or routed to local models? |
| 3 | B | **Four persona agents read in parallel** and write one proposal per source. | Do Finance and Risk need specialist agents? |
| 4 | C ① | **The validator sends back** invented quotes, out-of-scope kinds and self-confirmation. | Is two retries enough? |
| 5 | D | **Aliases are resolved** where a source states them: CustHub = CH = CRM, LedgerOne = ERP = GL. | Stated aliases only, or fuzzy matching too? |
| 6 | D | **3 contradictions are kept** (customer types, order statuses, Customer Number issuer), along with the homonym "Account" (Customer vs GL account). | Expected Sales vs Finance conflicts? |
| 7 | E | **Grades: A 0 · B 31 · C 96 · D 5 · X 3.** | Is "two independent files" the right bar for B? |
| 8 | F | **Reference gaps become grade-D assumptions:** Person, Organisation, Channel and 2 relationships. | Which group functions come next? |
| 9 | G | **Unknowns: 20 items, 8 high priority**, each with an owner. These start loop ③. | Answerable in one reply? |
| 10 | H | **Phases 1–3 are provisional.** | What should stop a provisional phase? |
| 11 | J ② | **Each element is routed to its approver.** Deferred items stay open. | Batch by grade, by domain or by system? |
| 12 | K | **Publish**, including stand-in SQL for each system (Risk shown). | LinkML as the source of truth? |
| 13 | ③ Loop 2 | **Answers come back:** SME answers (authority 3) and a CustHub schema export (authority 2), with 12 files carried forward. | Is a session note good enough as an SME answer? |
| 14 | I | **Change register: 3 contradictions resolved, with superseded versions kept, 19 elements graded up, 4 unknowns closed.** | Should grade-downs block a new baseline? |
| 15 | Loop n | **When to stop iterating:** the exit checklist for a domain baseline, after which phase 10 change control takes over. | Who decides to stop: the board or the domain owner? |

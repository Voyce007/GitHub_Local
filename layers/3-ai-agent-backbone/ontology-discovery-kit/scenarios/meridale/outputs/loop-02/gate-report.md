# Gate report — loop-02

## Phase 1: Enterprise scope and architecture discovery — **PROVISIONAL**

Exit gate: Enterprise scope and architectural context are agreed.  
Discovery mode: provisional · 3 of 16 in-scope elements below grade B

| Criterion | Result | Failing | Covered by unknowns |
|---|---|---|---|
| P1.1 Every manifest file is ingested and citable | pass | — | — |
| P1.2 Every candidate system has a role or an open unknown | pass | — | — |
| P1.3 Every candidate system cites at least one source | pass | — | — |
| P1.4 An unknowns register has been produced | pass | — | — |

## Phase 2: Business concepts and domain modelling — **PROVISIONAL**

Exit gate: Shared business concepts and definitions are approved.  
Discovery mode: run · 26 of 33 in-scope elements below grade B

| Criterion | Result | Failing | Covered by unknowns |
|---|---|---|---|
| P2.1 Every concept has a definition | pass | — | — |
| P2.2 A synonym register exists | pass | — | — |
| P2.3 Every contradiction has an open unknown | pass | — | — |
| P2.4 Key concepts present: Customer, Product, Order | pass | — | — |

## Phase 3: Entity and relationship modelling — **PROVISIONAL**

Exit gate: Conceptual model is validated by business and architecture stakeholders.  
Discovery mode: run · 84 of 103 in-scope elements below grade B

| Criterion | Result | Failing | Covered by unknowns |
|---|---|---|---|
| P3.1 Every candidate entity has at least one attribute | provisional | ENT-12, ENT-14 | ENT-12, ENT-14 |
| P3.2 Entities are traced to a concept, are link tables, or are flagged for review | provisional | ENT-02, ENT-12, ENT-14 | ENT-02, ENT-12, ENT-14 |

## Human gate

Mode: **simulated** — decisions were filled in by the simulator, not by people.

| Approver | Decisions |
|---|---|
| Enterprise Architecture Authority | approve-provisional: 16 |
| Business Domain Owner | approve-provisional: 33 |
| Domain Owner and Data Architecture Authority | approve-provisional: 29, note-assumption: 5 |
| Data Architecture Authority | approve-provisional: 69 |
| Design Authority | approve-provisional: 8 |

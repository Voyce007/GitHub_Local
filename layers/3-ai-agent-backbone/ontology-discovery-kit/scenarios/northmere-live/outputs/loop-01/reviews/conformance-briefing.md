# Conformance briefing: Northmere, loop-01

Prepared by the Conformance agent (read-only). Inputs I read: `model.json`, `gates.json`,
`unknowns.json`, `approvals.yaml`, `sources.json`, the 12 input files under
`inputs/loop-01/`, and `config/evidence_grades.yaml`, `playbook.yaml` and `decision_rights.yaml`.
I changed no grades, gate results, approvals or elements. All 199 decisions in `approvals.yaml`
are still `pending`, which is the expected state.

## 1. Headline

- **No gate fully passes, and none fails.** Phases 1, 2 and 3 are all **provisional**. This loop uses documents only, so provisional is the best result available.
- **No grade-A elements.** That is correct for a loop with documents only (the ceiling is B). Grades are 47 B, 141 C, 8 D and 3 X across 199 elements.
- **Citation spot-check:** I checked 18 citations on 15 elements, covering all four proposing agents and all five file types. 13 citations give real support. **5 are weak** (section 3).
- **Grading:** I found nothing that breaks the configured rules. Two grades are generous in substance and one contradiction is incomplete (section 4).
- **Decomposition:** every entity and calculation has a domain, with one data defect. `ENT-13 Party` is assigned `"Customer"`, but the domain key is `customer`. As a result it is missing from every domain summary, even though `unassigned` is empty (section 5).

## 2. Gate results in plain language

### Phase 1: Enterprise scope and architecture discovery (provisional; 14 elements in scope, 3 below B)
- **Passed:** all 12 manifest files are ingested and citable (P1.1). Every system cites a source (P1.3). The unknowns register exists (P1.4). Six of the seven systems (TAXCORE, CitizenPortal, RevenueWarehouse, EmployerGateway, NumberHub, ChildcarePortal) and the five main flows into and out of TAXCORE are grade B.
- **Provisional:** P1.2. `SYS-07 income-verify-svc` has no role. Its only evidence is a base-URL line in the ChildcarePortal config. It is covered by **U-15**, and an answer to U-15 makes P1.2 pass. Two flows, `FLW-06` (ChildcarePortal to NumberHub) and `FLW-07` (ChildcarePortal to income-verify-svc), are C because their only source is that config file. Neither file says which way the data moves.
- **Failed:** nothing.

### Phase 2: Business concepts and domain modelling (provisional; 54 elements in scope, 52 below B)
- **Passed:** the synonym register exists (P2.2). Every recorded contradiction has an open unknown (P2.3). The key concepts set by `scenario.yaml` (Customer, Employment, NI Contribution, Childcare Account) are all present (P2.4). Note that `scenario.yaml` overrides the playbook's Customer/Product/Order list; that is intended.
- **Provisional:** P2.1. Seven concepts are used in the sources but never defined: CON-13 Employer Return, CON-15 Lower Earnings Limit, CON-16 Class 1 Contribution, CON-17 Expected Income, CON-18 Parent, CON-19 Eligibility Check and CON-20 Parent Payment. Answers to **U-08 to U-14** make P2.1 pass. The gate still cannot fully pass, because almost every concept and rule rests on a single source (usually the glossary or one procedures doc). Only RUL-13 and TAX-03 are B.
- **Failed:** nothing. One gap is not caught by P2.3: the two rules RUL-01 (NINO issued at first registration) and RUL-08 (NINO issued at age 16) also contradict each other on *when* the number is issued. Neither rule is marked as conflicting. U-05 covers this only indirectly, through who issues the number (IDN-02).

### Phase 3: Entity and relationship modelling (provisional; 95 elements in scope, 77 below B)
- **Passed:** every entity has attributes (P3.1). Every entity is traced to a concept or capability, or is flagged for review (P3.2). Eleven of the twelve evidenced entities are B. They are backed by the data dictionary (2022) and the batch-job catalogue (2024).
- **Provisional:** both criteria pass, but the gate is provisional because 77 elements are C, D or X. All 58 attributes are C (data dictionary only), as are eight of the nine identifiers. `IDN-02` is X (U-05) and `ENT-13 Party` is D (U-19). **U-04** (a TAXCORE schema export and a masked data sample) is the single action that would lift most of this phase: about 78 elements could move to A.
- **Failed:** nothing.

## 3. Citation spot-check (18 citations, 15 elements)

| # | Element (agent) | File type | Citation | Verdict |
|---|---|---|---|---|
| 1 | ENT-01 Person (da) | spreadsheet | data-dictionary l.2, batch-jobs l.2 | Supports |
| 2 | IDN-02 NINO (da) | doc | NI procedures l.12 vs TAXCORE overview l.14 | Supports the contradiction (see 4c) |
| 3 | REL-12 Child to Person (da) | spreadsheet | data-dictionary l.46 (nullable, no FK) | Supports |
| 4 | **REL-13 ChildcarePayment to ChildcareProvider (da)** | spreadsheet + wiki | data-dictionary l.51; glossary l.14 | **Citation concern** |
| 5 | **REL-15 NiRecord to NiContribution (da)** | spreadsheet | data-dictionary l.36, 37, 39 | **Citation concern** |
| 6 | CAP-02 Record Life Events (ea) | doc | capability-map l.10 | Supports |
| 7 | **DOM-01 Customer (ea)** | doc | capability-map l.9 (`- **Register Customer**:`) | **Citation concern** |
| 8 | SYS-05 NumberHub (ea) | doc | NI procedures l.7 | Supports |
| 9 | SYS-07 income-verify-svc (ea) | example-code | portal properties l.4 | Supports existence only (graded C, correct) |
| 10 | RUL-11 No contributions after death (ba) | doc | NI procedures l.18 | Supports the rule; domain looks wrong (section 5) |
| 11 | RUL-13 Quarterly reconfirmation (ba, eng) | doc + example-code | scheme guide l.12; properties l.5 | Supports. The flag shows the feature is on, and "quarterly" matches "every three months" |
| 12 | **RUL-17 Close accounts of deceased (ba)** | spreadsheet | batch-jobs l.12 (job title) | **Citation concern** |
| 13 | TAX-02 NiCategory (ba, da, eng) | doc + spreadsheet | NI procedures l.22; data-dictionary l.33 | Supports the contradiction |
| 14 | **CAL-11 PRC_CLOSE_DECEASED (eng)** | spreadsheet + example-code | batch-jobs l.12; SQL l.39, l.42 to 43 | **Citation concern** (for the NiRecord write) |
| 15 | RUL-26 NI thresholds and rates (eng) | example-code | SQL l.8 | Supports what the 2020 code did. Not evidence of current rates |
| 16 | INT-01 CUS-01 (eng) | spreadsheet + diagram | interface-catalogue l.2; current-state.mmd l.2 | Supports |
| 17 | EVT-01 NationalInsuranceNumberAllocated (eng) | spreadsheet | interface-catalogue l.4 (MQ message) | Supports |
| 18 | CON-14 Qualifying Year (ba) | doc | NI procedures l.17 | Supports (the rule line gives a working definition) |

**Citation concerns (5):**
- **REL-13**: graded B on two sources. Data-dictionary line 51 shows a `PROVIDER_REF` column with no FK. Glossary line 14 defines the *concept* Childcare Provider. It says nothing about the payment table or any key. The target entity does not exist in the model (U-16), so this B overstates the relationship.
- **REL-15**: no cited line states this relationship. The link (NI record as a yearly total of contributions, joined through employment to person and tax year) is the agent's inference from column names. Under the grade definitions this reads as D ("inferred without direct evidence"), not C.
- **DOM-01** (and DOM-02 to DOM-04 have the same pattern): the current evidence is a capability heading. The other source is the stale 2016 overview. That supports the existence of the capability, not a domain boundary. The C grade is fine, but these citations should not be read as evidence for the split.
- **RUL-17**: a batch job's *name* ("Close accounts of deceased") is cited as a business rule. It also duplicates RUL-16, RUL-21 and RUL-25.
- **CAL-11 and the cross-domain write on ENT-08 NiRecord (U-01)**: the batch catalogue (line 12) lists `TC_NI_RECORD` as a write target of PRC_CLOSE_DECEASED. The procedure source (SQL lines 42 to 43) only updates `TC_CHILDCARE_ACCOUNT.STATUS`. The SQL is a stale, simplified extract, so this is not a contradiction. But the write to NiRecord rests on one catalogue line. That makes "Customer writes NiRecord" weaker evidence than "Customer writes ChildcareAccount".

## 4. Grade audit

- **a. Grade ceiling:** no element is A. This complies with the rules.
- **b. Generous grades (no rule broken):**
  - REL-13 is B (see above).
  - RUL-26 is C, but it hardcodes 2020 thresholds (1048 and 758) from a file labelled "Simplified; not production source".
  - CAL-09 PRC_CHECK_ELIGIBILITY computes expected income as `SUM(GROSS_PAY) * 4` over all pay periods, with no date filter. Approvers should not read CAL-09, RUL-14 or RUL-19 as confirming how expected income is defined (U-11).
- **c. IDN-02 contradiction is incomplete:**
  - The "TAXCORE issues it" side contains only stale files: the 2016 overview (whose manifest note says it pre-dates the 2022 NumberHub carve-out) and the 2020 SQL.
  - The current 2024 batch catalogue (line 3, E-046) still lists job J020 PRC_ALLOCATE_NINO as running **daily** and writing TC_PERSON. It is cited on IDN-02 but is not counted on either side.
  - That is current evidence that TAXCORE still allocates or stores NINOs locally. The X grade is right, but the Data Architecture Authority should see this line when answering U-05.
- **d. Unknowns that may already be answerable:**
  - U-17 ("no entity for Qualifying Year"): it is held as the attribute `ATT-37 NiRecord.qualifyingYear` / `TAX-07`.
  - U-16 ("Childcare Provider"): it is referenced through `ATT-50` / `IDN-08 PROVIDER_REF`, with the master outside TAXCORE.
  - Both unknowns ask for an entity, while the evidence points to an attribute or an external reference.
- **Rule recommendations (for `config/`, not applied):**
  1. When a contradiction's variants are split between stale-only and current files, mark the stale-only variant as "likely superseded" in the unknown text. This would help the decider without resolving the conflict automatically.
  2. Count a relationship's sources only where a line states the link (an FK, a join, or a sentence). A column that merely exists should not count, so inferred relationships would grade D.
  3. Run the P2.3 contradiction check over rules as well as over properties of identifiers and taxonomies.

## 5. Decomposition check (TAXCORE into Customer, PAYE, National Insurance, Childcare)

- **Entities and calculations without a valid domain:**
  - `ENT-13 Party` has `domain: "Customer"` (the display name), not the key `customer`. It is missing from every domain summary, so it is in practice unassigned, yet `decomposition.unassigned` is `[]`. Fix this in the pipeline or reconcile step. I did not edit it.
  - All other entities (12) and all 11 calculations have a valid domain.
- **Ownership resting on vocabulary rather than write evidence:**
  - `ENT-03 Employer` is assigned to PAYE by vocabulary only ("no capability writes it"). The batch catalogue shows PRC_LOAD_RETURNS reading TC_EMPLOYER but nothing writing it. So something outside the known jobs, possibly EmployerGateway, maintains employers.
  - All other entities are assigned from writes in the batch catalogue. That is one current spreadsheet (2024), not system evidence, and it is the main thing U-04 and real batch-scheduler or procedure source would confirm.
  - At domain level the vocabulary-based share is highest in **Childcare** (13 elements assigned by vocabulary vs 7 by write or run evidence) and **National Insurance** (10 vs 5). PAYE has 5 vs 6 and Customer 2 vs 4. The rest follow their parent entity.
  - The four DOM elements are themselves only C.
- **Questionable assignments:**
  - `TAX-02 NiCategory` is placed in PAYE ("used by PayPeriod.niCategory"), but its codes are defined on `TC_NI_CONTRIBUTION` and its business source is the NI procedures.
  - `RUL-11` and `RUL-18` (no contributions after death) are placed in **Customer** by vocabulary, while the near-identical `RUL-23` is in National Insurance and the rule is enforced in PRC_CALC_NIC.
  - `RUL-21` (null) and `RUL-25` (childcare) cite the same SQL line but land in different domains.
- **Rules and concepts with no domain (outside the entity/calculation check, listed for completeness):**
  - CON-01, CON-15, CON-17, CON-18 and CON-20.
  - RUL-02, RUL-03, RUL-16, RUL-17 and RUL-21. RUL-16 is clearly Childcare.
- **Splits and cross-domain writes:**
  - The NI_NUMBER split (ENT-01/ATT-02, from Customer to NI, U-03) is well supported: the batch job J020 and the SQL both show NI Operations writing TC_PERSON.
  - The PersonChanged recommendation (U-01) is solid for ChildcareAccount. For NiRecord it rests on one catalogue line (section 3).

## 6. Briefings by approver role

Each section lists only that role's items. "Ev" means evidence lines / distinct files.

### 6.1 Enterprise Architecture Authority: 30 items (22 B, 8 C)
- **Systems (7):**
  - SYS-01 TAXCORE (B, 15 ev / 9 files)
  - SYS-02 CitizenPortal (B, 3/3)
  - SYS-03 RevenueWarehouse (B, 3/3)
  - SYS-04 EmployerGateway (B, 3/3)
  - SYS-05 NumberHub (B, 5/4)
  - SYS-06 ChildcarePortal (B, 4/4)
  - **SYS-07 income-verify-svc (C, 1/1)**: no role. Answer U-15 before approving.
- **Flows (7):**
  - FLW-01 to FLW-05 (all B, 2 to 3 files each)
  - **FLW-06** ChildcarePortal to NumberHub and **FLW-07** ChildcarePortal to income-verify-svc (C, 1/1 each, from a config URL only; the direction is not stated).
- **Domains (5), all C:**
  - DOM-01 Customer, DOM-02 PAYE, DOM-03 NI and DOM-04 Childcare (2 ev / 2 files each, one of them stale)
  - DOM-05 Reporting/MI (1/1)
  - Their evidence is capability headings plus the stale 2016 overview (citation concern on DOM-01). Approving them means accepting the four-domain boundary on business intent, not on system evidence.
- **Capabilities (11), all B:**
  - CAP-01 to CAP-11, from the 2025 capability map plus the batch catalogue (2 to 3 files each).
- **Joint decisions with domain owners:**
  - **U-01**: PersonChanged replacing PRC_CLOSE_DECEASED's cross-domain writes. It is well evidenced for ChildcareAccount and thin for NiRecord.
  - **U-03**: move NI_NUMBER from Customer to NI. Well evidenced.

### 6.2 Business Domain Owner: 65 items (2 B, 54 C, 7 D, 2 X)
- **Concepts (20):**
  - CON-01 to CON-12 and CON-14 are C (1 to 3 ev, mostly the 2024 glossary).
  - **D, undefined:** CON-13 Employer Return, CON-15, CON-16, CON-17, CON-18, CON-19 and CON-20. Defining them answers U-08 to U-14 and makes P2.1 pass.
  - **U-02**: is "Person" a synonym of Customer or a separate role? This affects CON-01 and ENT-01.
- **Rules (26):** RUL-13 quarterly reconfirmation is the only B. All others are C on one source each.
  - The RUL-01 vs RUL-08 NINO timing contradiction is not flagged; decide it alongside U-05.
  - There are duplicate pairs (RUL-11/18/23 and RUL-16/17/21/25, plus RUL-12/14/19 and RUL-20/24). Consider approving one canonical rule per pair.
  - RUL-01, RUL-02, RUL-03 and RUL-26 rest only on stale sources (2016 overview, 2020 SQL). Do not approve RUL-26's rates as current.
- **Taxonomies (8):**
  - TAX-03 ChildcareAccountStatus is B.
  - **TAX-01 EmploymentStatus is X** (U-06: is SUSPENDED in use?). The 2023 manual is newer than the 2022 dictionary.
  - **TAX-02 NiCategory is X** (U-07: is category V in use?). Its domain should probably be NI, not PAYE.
  - TAX-04 to TAX-08 are C.
- **Calculations (11), all C:**
  - CAL-01 to CAL-11 (1 to 3 ev, batch catalogue plus stale SQL).
  - CAL-09's income formula should not be treated as the definition of Expected Income.
  - CAL-11's NiRecord write is uncorroborated by the procedure text.

### 6.3 Domain Owner and Data Architecture Authority: 28 items (18 B, 9 C, 1 D)
- **Entities (13):**
  - ENT-01 to ENT-12 are B (2 to 3 files each: the data dictionary plus the batch catalogue; some also cite the stale SQL).
  - **ENT-13 Party is D** (reference model only, U-19). Its domain value is malformed (section 5).
  - ENT-03 Employer's domain rests on vocabulary only.
- **Relationships (15):**
  - B: REL-02, 03, 05, 08, 09 and 13.
  - **REL-13 is a citation concern.** It has no target entity, and the B is generous.
  - C: REL-01, 04, 06, 07, 10, 11, 12, 14 and 15. **REL-15** is inferred with no direct line (D in substance).
  - Cross-domain references (REL-07, REL-12, REL-14) are the dependencies the split must expose as queries (Get Person, Get Pay Period).
- **Joint decisions:**
  - U-01 and U-03 (with the EA Authority).
  - U-19 (does Party exist?).

### 6.4 Data Architecture Authority: 67 items (66 C, 1 X)
- **Attributes (58):** ATT-01 to ATT-58 are all C, each on one data-dictionary line (2022, current). They are structurally sound. All of them are blocked from B or A only by the missing schema export (**U-04**).
- **Identifiers (9):**
  - IDN-01, IDN-03 to IDN-09 are C.
  - **IDN-02 National Insurance Number is X** (9 ev / 7 files, U-05). When deciding, note the current 2024 batch job J020, which still writes TC_PERSON.NI_NUMBER daily (section 4c).
- **Open questions owned here:**
  - U-05 (who issues the NINO)
  - U-16 (Childcare Provider: likely external, referenced through ATT-50/IDN-08)
  - U-17 (Qualifying Year: held as ATT-37/TAX-07)

### 6.5 Design Authority: 9 items (5 B, 4 C)
- **Interfaces (8):**
  - INT-01 CUS-01, INT-02 PAY-01, INT-03 NIN-02, INT-04 CC-01 and INT-05 MI-01 are B (interface catalogue plus diagram).
  - INT-06 (TAXCORE JDBC), INT-07 (NumberHub API) and INT-08 (income-verify API) are C, each from one config line.
  - INT-06 shows ChildcarePortal connecting directly to the TAXCORE database. That is a direct coupling the Childcare carve-out must remove.
- **Event (1):** EVT-01 NationalInsuranceNumberAllocated is C (interface catalogue l.4, an MQ message). It is a good candidate for the canonical event contract.
- No PersonChanged event element exists yet. It is only a recommendation under U-01.

## 7. What moves the gates next loop
1. **U-04**: a TAXCORE schema export and a masked data sample. This would lift most of phase 3 (about 78 elements) and check the batch catalogue's write claims.
2. **Real procedure source or a scheduler export.** This would confirm or refute PRC_CLOSE_DECEASED writing TC_NI_RECORD, and settle the domain basis for the split.
3. **Owner answers** to U-08 to U-15 (definitions and income-verify-svc). These make P1.2 and P2.1 pass.
4. **Owner answers** to U-02, U-05, U-06 and U-07. These clear the X grades and the Person homonym.

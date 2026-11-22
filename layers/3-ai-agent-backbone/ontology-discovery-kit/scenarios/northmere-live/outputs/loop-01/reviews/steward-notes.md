# Steward notes — northmere-live, loop-01

Ontology Steward review of `work/loop-01/model.json` (199 elements, 7 flags), `unknowns.json`
(U-01..U-19), `target_domains.yaml` and `outputs/loop-01/agent-notes.md`. All file references are
relative to `inputs/loop-01/`. These are recommendations for the human gate; nothing here
approves, rejects, resolves or reassigns anything.

---

## Merge review

### System alias merges (`system_lookup`)

| System | Merged names | Supporting source | Assessment |
|---|---|---|---|
| SYS-01 TAXCORE | the Core, TC, TAXCORE (the Core) | docs/taxcore-system-overview.md line 7 ("also called 'the Core' or 'TC'"); diagrams/current-state.mmd line 2 | Sound. |
| SYS-01 TAXCORE | `taxcore-db` | code-examples/childcare-portal.properties line 2 (`jdbc:db2://taxcore-db.internal.example:50000/TAXCORE`) | **Inferred, not stated.** Supported by the hostname and the database name TAXCORE in the JDBC path, and DB2 matches overview line 7. Probably right; confirm with the Engineering Lead. |
| SYS-01 TAXCORE | `TC_` | manifest `table_prefix` | Not a system name, it is a table prefix. Harmless for lookup but should not appear as an alias in published outputs. |
| SYS-02 CitizenPortal | online account, CP | overview line 9; diagram line 2 | Sound. |
| SYS-03 RevenueWarehouse | MI warehouse, RW | overview line 10; diagram line 6 | Sound. |
| SYS-04 EmployerGateway | employer filing, EG | docs/paye-operations-manual.md line 7; diagram line 3 | Sound. |
| SYS-05 NumberHub | NI allocation, NH, `numberhub` | docs/national-insurance-procedures.md line 7; diagram line 4; properties line 3 (hostname) | Sound, with one **homonym risk**: "NI allocation" is NumberHub's nickname, but the same sentence refers to "the TAXCORE allocation module" it replaced, and the capability CAP-06 is "Allocate NI Number". Any future source saying "NI allocation" in a pre-2022 context may mean the TAXCORE module, not NumberHub. Recommend the merge stands, but that pre-2022 uses of "NI allocation" are not auto-attributed to SYS-05. |
| SYS-06 ChildcarePortal | parent account, CC | childcare-scheme-guide.md line 7; diagram line 5 | Sound. "CC" also prefixes interface CC-01 and the column CC_ACCOUNT_ID; the alias lookup should only ever match it as a system node, not as a substring. |
| SYS-07 income-verify-svc | income-verify | properties line 4 (hostname) | Sound but weak: one config line only. |

No merge looks wrong. The two hostname-based merges (`taxcore-db`, `income-verify`) are inferences and should be marked as such.

### Near-duplicates the deterministic merge missed (candidates, not merges)

1. **TAX-07 `QualifyingYear` and TAX-08 `NI Qualifying Year Flag`** are the same code list on the same
   column, `TC_NI_RECORD.QUALIFYING` (taxcore-data-dictionary.csv line 38), proposed once by DA and once by
   Engineering under different names. Codes are identical (Y=Yes, N=No). Candidate merge. DA also notes it
   may be a boolean rather than a taxonomy at all.
2. **Rule clusters that state one rule several times** (sources differ, rule is the same):
   - *No NI contributions after death*: RUL-11 (national-insurance-procedures.md line 18), RUL-18 and RUL-23
     (both taxcore_procedures.sql line 12 — the same line produced two rules, one from BA and one from
     Engineering). They are also assigned to **different domains** (RUL-11 and RUL-18 to Customer, RUL-23 to
     National Insurance). The rule governs a National Insurance calculation; Customer is a vocabulary
     artefact of the word "death".
   - *Close the childcare account when the holder dies*: RUL-16 (childcare-scheme-guide.md line 15),
     RUL-17 (taxcore-batch-jobs.csv line 12), RUL-21 and RUL-25 (both taxcore_procedures.sql lines 42-43).
     Four elements; three have no domain, RUL-25 is Childcare.
   - *Income limit 100,000*: RUL-14 (guide line 13 + sql line 26) and RUL-19 (sql line 26).
   - *Top-up is 25%*: RUL-20 and RUL-24 (both sql line 36).
   - *Three-monthly reconfirmation*: RUL-04 (business-capability-map.md line 18), RUL-13 (guide line 12 +
     properties line 5) and RUL-22 (properties line 5).
   Recommend the gate treats each cluster as one rule with several pieces of evidence (the documented
   statement plus its implementation), so that grades reflect corroboration rather than being split.
3. **RUL-01 and RUL-08 are a contradiction, not two rules.** RUL-01 "issued at first registration"
   (overview line 14, 2016) and RUL-08 "issued at age 16" (NI procedures line 12, 2023) describe the same
   rule with different timing and issuer. Only IDN-02 carries a conflict; the rules carry none. Recommend
   they are linked to U-05.
4. **Concepts that are realised but were flagged as unrealised**:
   - CON-14 *Qualifying Year* is realised by ATT-37 `NiRecord.qualifyingYear` (dictionary line 38) as a
     per-tax-year flag on NiRecord, not as an entity. U-17 can be reframed (see below).
   - CON-12 *Top-up Payment* is realised by ATT-52 `ChildcarePayment.topUpAmount` (dictionary line 53,
     "Government top-up"), a column on the payment row rather than an entity. U-18 can be reframed.
   - CON-20 *Parent Payment* matches ATT-51 `ChildcarePayment.parentAmount` (dictionary line 52, "Parent
     payment") and the CC-01 payload. ENT-11 ChildcarePayment probably realises both Parent Payment and
     Top-up Payment.
5. **Roles that may be one role**: CON-18 *Parent* (guide lines 7-8, 12-13) and "account holder" (guide
   line 15); REL-08 ChildcareAccount → Person is annotated by DA as the account holder. Candidate synonym;
   SME question (added under U-14).
6. **Person / Customer / Party**: CON-01 Customer (aliases Taxpayer, Citizen, Person), ENT-01 Person and
   ENT-13 Party (grade D, reference ontology) overlap. TC_CHILD.PERSON_ID (line 46, "if registered") shows
   a TAXCORE Person can be a child who is not necessarily a customer. U-02 and U-19 should be asked together.
7. **Interfaces**: INT-06 ChildcarePortal-TAXCORE-JDBC and INT-04 CC-01 both connect ChildcarePortal to
   TAXCORE. They are *not* duplicates (REST vs direct DB2), but should be reviewed together: the JDBC link
   may be how CC-01 is actually implemented, or a second, undocumented path.

### Domain-assignment anomalies found while reviewing merges

- **TAX-02 NiCategory is assigned to PAYE** (domain_basis "used by PayPeriod.niCategory"), although
  target_domains.yaml lists "ni category" as a National Insurance keyword and the code list is documented
  in national-insurance-procedures.md line 22. The column also appears on TC_NI_CONTRIBUTION (line 33).
  Recommend: National Insurance owns the code list; PAYE carries the value as received in the employer
  return (TC_PAY_PERIOD.NI_CATEGORY, line 29). For the Director of National Insurance and Director of
  Employer Taxes to confirm.
- **CON-01 Customer has no domain** (null), while ENT-01 Person is Customer. Probably a gap in vocabulary
  scoring rather than a real question.
- CON-15 Lower Earnings Limit, CON-17 Expected Income, CON-18 Parent, CON-20 Parent Payment, RUL-02, RUL-03,
  RUL-16, RUL-17, RUL-21 have no domain. RUL-02 and RUL-03 are IT-governance rules (overview lines 19-20)
  and arguably belong outside the business ontology; RUL-02 is however directly relevant to the
  decomposition (see below).

---

## Contradictions

### C-1. Issuer and timing of the National Insurance Number (IDN-02, RUL-01 vs RUL-08; U-05)
- *TAXCORE, at first registration*: docs/taxcore-system-overview.md line 14 (architecture overview,
  2016-09-12, stale) and code-examples/taxcore_procedures.sql line 18 (`NEXT VALUE FOR SEQ_NINO`, example
  code, 2020-07-01, stale).
- *NumberHub, at age 16*: docs/national-insurance-procedures.md lines 7 and 12 (process doc, 2023-10-16) and
  spreadsheets/interface-catalogue.csv line 4 (NIN-02 NumberHub → TAXCORE, 2024-03-11).
- Most likely explanation: both TAXCORE sources pre-date the 2022 NumberHub carve-out (NI procedures line 7).
  **But** the 2024 batch-job catalogue (taxcore-batch-jobs.csv line 3) still schedules J020
  `PRC_ALLOCATE_NINO` *Daily*, writing TC_PERSON. Either J020 now only stores the number received over
  NIN-02, or it is a leftover that still generates numbers from SEQ_NINO. The second case would create two
  issuers and threaten RUL-09 (one number for life). The nullable NI_NUMBER (dictionary line 3) is
  consistent with "age 16".
- Recommendation: treat NumberHub as the current issuer pending confirmation; open a separate question on
  J020 (U-20 below).
- **Decider**: Data Architecture Authority, with the Director of National Insurance (NI Operations owns both
  NIN-02 and J020).

### C-2. EmploymentStatus values (TAX-01; U-06)
- *Live, Ceased*: docs/paye-operations-manual.md line 18 (process doc, 2023-04-03).
- *Live, Ceased, Suspended*: spreadsheets/taxcore-data-dictionary.csv line 20 (data dictionary, 2022-02-14).
- Both current. Most likely: SUS exists in the database but is not an operational status that staff set
  (legacy, or set only by a batch process), or the manual simplified the list. A data profile would settle
  it.
- **Decider**: Director of Employer Taxes (PAYE Operations), with a row count of `STATUS='SUS'` from the
  Engineering Lead.

### C-3. NiCategory values (TAX-02; U-07)
- *A, B, C, H, J, M, Z*: docs/national-insurance-procedures.md line 22 (process doc, 2023-10-16).
- *... plus V*: spreadsheets/taxcore-data-dictionary.csv line 33 (data dictionary, 2022-02-14).
- The dictionary is the older source, so V may have been withdrawn before the 2023 procedures, or the
  procedures list only categories staff assign. Note TC_PAY_PERIOD.NI_CATEGORY (line 29) has no code list,
  so the PAYE side may accept values the NI side does not.
- **Decider**: Director of National Insurance (NI Operations); evidence: distinct values of NI_CATEGORY in
  both tables.

### C-4. What PRC_CLOSE_DECEASED writes (CAL-11) — not currently recorded as a conflict
- *Writes TC_CHILDCARE_ACCOUNT and TC_NI_RECORD*: taxcore-batch-jobs.csv line 12 (job catalogue, 2024-08-01).
- *Writes TC_CHILDCARE_ACCOUNT.STATUS only*: taxcore_procedures.sql lines 39-43 (example code, 2020-07-01,
  stale, "simplified").
- Most likely: the procedure was extended after 2020, or the extract omitted the NI statement, or the
  catalogue entry is wrong. This matters because the NiRecord half of the proposed PersonChanged event
  (U-01) rests entirely on the catalogue line, with no column-level evidence (`columns: []`).
- **Decider**: Engineering Lead with Core Systems Operations, from current production source.

### C-5. How expected income is derived (RUL-12, RUL-14/19, CAL-09, SYS-07) — not recorded as a conflict
- *From PAYE employment records*: childcare-scheme-guide.md line 8 (2024), implemented as
  `SUM(GROSS_PAY) * 4` over TC_PAY_PERIOD (taxcore_procedures.sql lines 25-29, 2020, stale).
- *Possibly from income-verify-svc*: childcare-portal.properties line 4 (2025) — purpose not stated.
- Most likely: income verification moved, or is moving, out of TAXCORE into income-verify-svc after 2020;
  or income-verify-svc does something else entirely. Possible contradiction only.
- **Decider**: Director of Family Support, with the Enterprise Architecture Authority for SYS-07.

### C-6. Interface mechanism between ChildcarePortal and TAXCORE (INT-04 vs INT-06)
- *REST API*: interface-catalogue.csv line 5 (CC-01, 2024) and diagram line 5 (2025).
- *Direct DB2 JDBC*: childcare-portal.properties line 2 (2025).
- Most likely: both exist — the REST interface for parent payments, plus an undocumented shared-database
  dependency. The catalogue and diagram do not show it.
- **Decider**: Enterprise Architecture Authority with the ChildcarePortal team.

Not contradictions (recorded so nobody re-raises them): PAY-01 "Daily" (catalogue) vs "overnight" (PAYE
manual line 8); J310 running Daily vs the three-monthly reconfirmation (a daily job may process the accounts
that are due — confirm under U-24); J320 "Real time" vs "within one working day" (guide line 14).

---

## Revised unknowns

Existing U-ids kept; new candidates numbered U-20 onward as *proposed* additions (the Steward does not add
them to unknowns.json).

| ID | Revised question (answerable in one reply) | Ask |
|---|---|---|
| U-01 | When a death is recorded, which domains must react, and how? Specifically: (a) should Family Support close the childcare account itself on a "death recorded" notification from Customer; (b) does anything in the NI record change on death (the 2024 job catalogue says J330 writes TC_NI_RECORD, the 2020 code does not)? Would "DeathRecorded" (or a typed "LifeEventRecorded") be the right business event rather than a generic "PersonChanged"? | Directors of Customer Services, Family Support and National Insurance, with EA Authority |
| U-02 | Is every row in TC_PERSON a Customer, or does TC_PERSON also hold people who are not customers (e.g. a registered child, TC_CHILD.PERSON_ID, dictionary line 46)? If the latter, is "Person" the party and "Customer" a role? Answer together with U-19 (Party). | Director of Customer Services, Data Architecture Authority |
| U-03 | Today, does TAXCORE create NI_NUMBER or only store the number NumberHub sends over NIN-02? If it only stores it, is the proposed move of NI_NUMBER to National Insurance really "TAXCORE keeps a reference; NumberHub remains master"? | Director of National Insurance, EA Authority |
| U-04 | (Evidence) Provide a DB2 schema export of TAXCORE (all TC_ tables, keys, FKs, sequences incl. SEQ_NINO) and a masked sample with distinct-value counts for EMPLOYMENT.STATUS, NI_CATEGORY (both tables), CHILDCARE_ACCOUNT.STATUS, ELIGIBILITY_CHECK.OUTCOME. | Engineering Lead |
| U-05 | Who issues the NI number today and at what point (first registration or age 16)? Is anything other than NumberHub still able to issue one? | Director of National Insurance, Data Architecture Authority |
| U-06 | Is "Suspended" (SUS) a current employment status? If yes, who sets it and what does it mean; if no, are there rows still holding it? | Director of Employer Taxes |
| U-07 | Is NI category V current? If withdrawn, when, and do rows still carry it? Should TC_PAY_PERIOD.NI_CATEGORY use the same list? | Director of National Insurance |
| U-08 | Define a Class 1 contribution, and list any other contribution classes TAXCORE holds (only Class 1 appears: NI procedures line 8, TC_NI_RECORD.CLASS1_TOTAL). | NI Operations |
| U-09 | What is an eligibility check — one per account per reconfirmation, or one per run of J310? What triggers one? | Family Support |
| U-10 | Define an employer return: is it one file per employer per pay period (PAYE manual line 7, capability map line 11), and what is the "filing deadline" used for penalty review (RUL-07)? | PAYE Operations |
| U-11 | Define expected income: over what period, gross or net, from which records? Is `SUM(GROSS_PAY) * 4` over all pay periods (sql line 25, no date filter) the intended rule? | Family Support (with U-23) |
| U-12 | What is the lower earnings limit, where is its value held per tax year, and which procedure applies it to set TC_NI_RECORD.QUALIFYING? | NI Operations |
| U-13 | Is a parent payment exactly one TC_CHILDCARE_PAYMENT row (PARENT_AMOUNT) received over CC-01? | Family Support |
| U-14 | Is a "parent" the same as the "account holder" (guide line 15) — i.e. the Person on TC_CHILDCARE_ACCOUNT.PERSON_ID? Can an account have more than one parent? | Family Support |
| U-15 | What does income-verify-svc do, who owns it, what does ChildcarePortal send it and receive, and does it replace or supplement PRC_CHECK_ELIGIBILITY's income calculation? | EA Authority, ChildcarePortal team |
| U-16 | Where are childcare providers registered (PROVIDER_REF has no table in TAXCORE, dictionary line 51), and which system issues the provider reference? | Data Architecture Authority, Family Support |
| U-17 | *Reframed*: Qualifying year is held as the Y/N flag TC_NI_RECORD.QUALIFYING per person and tax year. Confirm that is the system of record and whether it should be modelled as an attribute (boolean) rather than an entity or a taxonomy (also resolves TAX-07/TAX-08). | Data Architecture Authority |
| U-18 | *Reframed*: Top-up payment appears to be TC_CHILDCARE_PAYMENT.TOPUP_AMOUNT on the parent's payment row, not a separate record. Confirm, and say where the top-up is actually paid out from (TAXCORE or ChildcarePortal). | Family Support |
| U-19 | Does the organisation have a Party concept above Person and Employer? Ask with U-02. | Director of Customer Services, Data Architecture Authority |
| **U-20** (new) | Is batch job J020 PRC_ALLOCATE_NINO (catalogue line 3, Daily, 2024) still running after the 2022 NumberHub carve-out? If so, what does it do now — generate from SEQ_NINO, or store the NIN-02 number? Is SEQ_NINO still in use? | Core Systems Operations, NI Operations |
| **U-21** (new) | Which TC_ tables does ChildcarePortal read or write over its direct JDBC connection (properties line 2), bypassing CC-01? | ChildcarePortal team, Engineering Lead |
| **U-22** (new) | What does ChildcarePortal call NumberHub for (properties line 3) — NI number lookup for parents, identity check, other? | ChildcarePortal team, NI Operations |
| **U-23** (new) | PRC_CHECK_ELIGIBILITY multiplies the sum of *all* pay periods, across all employments and tax years, by 4 (sql lines 25-30). Is this the production logic? It does not annualise any specific period. | Family Support, Engineering Lead |
| **U-24** (new) | J310 runs Daily but reconfirmation is every three months: does J310 check only accounts that are due, or every account every day? | Family Support |
| **U-25** (new) | PRC_CALC_NIC excludes every pay period of a person with a date of death (`DATE_OF_DEATH IS NULL`, sql line 12), including periods before death, whereas the rule says "after their recorded date of death" (NI procedures line 18). It also has no floor at zero for pay below the thresholds (1048 / 758) and applies the same rates regardless of NI category. Is the production procedure different? | NI Operations, Engineering Lead |
| **U-26** (new) | Which capability writes TC_PERSON.DATE_OF_DEATH? No job in the catalogue does (J010 writes TC_PERSON on registration; J330 only reads it). Is it CUS-01 from CitizenPortal, or a manual process? | Customer Services |
| **U-27** (new) | No job writes TC_EMPLOYER (J110 only reads it). Which process creates and maintains employers — EmployerGateway? | PAYE Operations |
| **U-28** (new) | MI-01 extracts "All modules" nightly to RevenueWarehouse (catalogue line 6). After decomposition, who provides the extract for each domain, and is Reporting/MI (DOM-05) an in-scope domain? | Data team, EA Authority |
| **U-29** (new) | Does RUL-02 (no module may change another module's tables without a Core Systems change request, overview line 19) still apply, and was J330's write into childcare and NI tables approved under it? | Core Systems, EA Authority |

---

## Evidence requests (ordered by how many elements they would confirm)

1. **TAXCORE schema export + masked data profile (U-04)** — confirms ~78 entity/attribute/identifier
   elements (ENT-01..12, ATT-01..58, IDN-01..09, REL-01..15) and resolves C-2, C-3 and the TAX-07/08 duplicate.
2. **Current production source of all eleven batch programs** (J010-J330; only five are in the 2020 extract)
   — confirms CAL-01..11, the rule clusters above (≈20 rules), the read sets used by the decomposition
   dependencies, and resolves C-4, U-20, U-23, U-25, U-26, U-27.
3. **ChildcarePortal integration description** (what goes over JDBC, NumberHub and income-verify-svc calls)
   — confirms INT-04, INT-06..08, FLW-04, FLW-06, FLW-07, SYS-07 and resolves C-5, C-6, U-15, U-21, U-22.
4. **NumberHub interface spec for NIN-02** — confirms INT-03, FLW-03, EVT-01, IDN-02 and the NI_NUMBER split.
5. **MI-01 extract specification** — confirms INT-05, FLW-05, DOM-05 and exposes RevenueWarehouse's
   table-level dependencies (U-28).
6. **NI reference values (lower earnings limit, thresholds, rates per tax year)** — confirms CON-15, RUL-10,
   RUL-26.

---

## Decomposition review

### Ownership — is it supported by write evidence?

| Entity | Proposed owner | Basis | Assessment |
|---|---|---|---|
| ENT-01 Person, ENT-02 Address | Customer | J010 writes both (batch line 2) | Supported. CUS-01 (CitizenPortal → TAXCORE, "Customer details; addresses") also writes customer data and is owned by Customer Services — corroborates. |
| ENT-03 Employer | PAYE | "no capability writes it; assigned by business vocabulary" | **Vocabulary only.** No writer in evidence (U-27). Probably PAYE, but the owner should confirm before it is graded. |
| ENT-04 Employment, ENT-06 PayPeriod | PAYE | J110 writes both; J120 writes PayPeriod | Supported. |
| ENT-05 TaxCode | PAYE | J130 | Supported. |
| ENT-07 NiContribution | NI | J210, PRC_CALC_NIC INSERT | Supported. |
| ENT-08 NiRecord | NI | J220 | Supported (J330's write is the cross-domain one). |
| ENT-09 ChildcareAccount, ENT-10 Child | Childcare | J300 | Supported. |
| ENT-11 ChildcarePayment | Childcare | J320 updates TOPUP_AMOUNT | Owner is right, but the evidence is partial: J320 only *updates* the top-up; the row (PARENT_AMOUNT, PROVIDER_REF, PAID_DATE) is created by the CC-01 inflow and possibly by the JDBC link (U-21). Both are Family Support systems, so ownership holds. |
| ENT-12 EligibilityCheck | Childcare | J310 | Supported. |

Capability-to-domain mapping uses the capability map's owner teams (business-capability-map.md lines 9-19)
and the catalogue's owner column, which agree in every row. Good.

### The NI Number split (ATT-02 NI_NUMBER from Person to National Insurance; U-03)

- The *direction* is supported: the number belongs to the NI capability "Allocate NI Number" (capability
  map line 14, owner NI Operations), and since 2022 it is created **outside TAXCORE by NumberHub**
  (NI procedures line 7; NIN-02 owned by NI Operations).
- The *evidence chosen* is weak. The split rests on J020/PRC_ALLOCATE_NINO writing TC_PERSON.NI_NUMBER, i.e.
  on a 2020 code extract (stale) and a 2024 catalogue line that may describe a zombie job (U-20). The current
  creator is NumberHub; TAXCORE's column is at most a received copy.
- The decomposition does not mention NumberHub at all. Its "Get National Insurance Number" query (NI
  domain, consumer Customer) is effectively NumberHub's service, and EVT-01 NationalInsuranceNumberAllocated
  (NIN-02, MQ, real time) already exists as the event Customer would react to.
- Recommendation: keep the split as proposed, but restate it as "National Insurance (NumberHub) masters the
  number; Customer holds a reference updated from NationalInsuranceNumberAllocated", and do not approve it
  until U-20 says whether J020 still generates numbers. If J020 still allocates from SEQ_NINO, that is a
  live double-issuer risk to RUL-09 and should be raised to the Director of National Insurance before any
  migration work.

### The PersonChanged event (CAL-11 / J330; U-01)

- The cross-domain write is real for ChildcareAccount: J330 sets TC_CHILDCARE_ACCOUNT.STATUS = 'CLO'
  (sql line 42), corroborated by the guide's rule (line 15) — but that rule is **Family Support's** rule.
- For NiRecord the write rests only on the catalogue (batch line 12) with no column and contradicts the 2020
  code (C-4). Do not design the NI reaction until C-4 is resolved.
- "Record Life Events" in the service catalogue has `changes: []` — the Customer command changes nothing in
  Customer's own data. J330 reads TC_PERSON and writes only other domains' tables. This suggests J330 is not
  Customer's "record a death" capability at all; it is a downstream reaction job, scheduled by Customer
  Services, that polls daily. The capability that actually records the death (writes DATE_OF_DEATH) is not
  in evidence (U-26).
- **"PersonChanged" is not a good business event.** It is CRUD-shaped and would fire on every address or
  correspondence-preference change, forcing Childcare and NI to filter. The evidence supports a specific
  business fact: a death was recorded (NI procedures line 18, guide line 15, capability map line 10).
  Recommend the owners consider **DeathRecorded** (or LifeEventRecorded with a type, given the capability
  also covers births and changes of circumstance), published by Customer when DATE_OF_DEATH is written.
  Childcare closes the account itself (RUL-16) and NI stops calculating (RUL-11) on that event.
- NI's other death dependency, PRC_CALC_NIC reading TC_PERSON.DATE_OF_DEATH (sql lines 11-12), is captured
  as the ni → customer read; it could be served by the same event instead of a per-run query.

### Missing or under-captured dependencies

1. **ChildcarePortal → TAXCORE DB2 over JDBC (INT-06)** — an undocumented shared-database consumer with
   unknown tables. This is the highest decomposition risk: splitting TAXCORE tables could break it silently.
   Not in unknowns.json (U-21 proposed). Not in `dependencies`.
2. **Childcare → National Insurance via NumberHub (FLW-06/INT-07)** — ChildcarePortal calls NumberHub
   directly. Not in `dependencies` (U-22).
3. **Childcare → income-verify-svc (FLW-07/INT-08)** — possibly a second source of expected income
   alongside the childcare → PAYE read through PRC_CHECK_ELIGIBILITY (C-5).
4. **Reporting/MI → all domains (MI-01)** — RevenueWarehouse takes "All modules" nightly (catalogue line 6).
   DOM-05 exists in the model but not in target_domains.yaml, so this consumer of every domain's tables is
   absent from the decomposition (U-28).
5. **PAYE → Customer (and NI) in Process Employer Returns** — J110 creates TC_EMPLOYMENT rows with a
   PERSON_ID (dictionary line 16) and RUL-05 requires each employment to link to one person, but the
   catalogue lists only TC_EMPLOYER as read. The person-matching read is not captured; ask with the program
   source (evidence request 2).
6. **Maintain NI Record → PAYE Employment** — J220 reads only TC_NI_CONTRIBUTION (keyed on EMPLOYMENT_ID,
   line 30) but writes TC_NI_RECORD keyed on PERSON_ID (line 36); it must resolve employment → person
   somewhere, and it needs the lower earnings limit (CON-15) from an unrecorded source.
7. **NI category** — PayPeriod.NI_CATEGORY (PAYE, line 29) feeds NiContribution.NI_CATEGORY (line 33) via
   PRC_CALC_NIC. The PAYE → NI read is captured, but the code-list ownership is mis-assigned (TAX-02, above).

### Other observations from agent-notes.md that are not yet owner questions

- J020 still scheduled after NumberHub replaced it (Engineering, DA notes) → U-20.
- ChildcarePortal JDBC and NumberHub calls, both missing from the interface catalogue and diagram (EA notes) → U-21, U-22.
- `SUM(GROSS_PAY) * 4` "looks questionable" (Engineering note on RUL-14) → U-23.
- PRC_CALC_NIC has no floor at zero and hard-coded rates (Engineering note on RUL-26) → U-25.
- J330 may affect NI records with no stated effect (BA note on RUL-17) → C-4 / U-01.
- Address has no declared primary key (DA note on ENT-02) → covered by U-04.
- Child.personId and ChildcarePayment.providerReference have no FK (DA notes) → U-02, U-16.

---

## Suggested SME sessions

1. **National Insurance (Director of National Insurance, NI Operations, Core Systems Operations)** — U-03,
   U-05, U-07, U-08, U-12, U-20, U-25, NiRecord part of U-01, C-4. Highest value: settles the NI Number split
   and the double-issuer risk.
2. **Childcare (Director of Family Support, ChildcarePortal team)** — U-09, U-11, U-13, U-14, U-15, U-16,
   U-18, U-21, U-22, U-23, U-24, childcare part of U-01. Settles the undocumented ChildcarePortal
   dependencies.
3. **Customer and life events (Director of Customer Services, Data Architecture Authority)** — U-01 (event
   design, with Family Support and NI attending the last 20 minutes), U-02, U-19, U-26, U-29.
4. **PAYE (Director of Employer Taxes, PAYE Operations)** — U-06, U-10, U-27, the TAX-02 code-list ownership
   question, and the person-matching read in J110.
5. **Architecture and data (EA Authority, Data Architecture Authority, Engineering Lead, Data team)** — U-04
   and evidence requests 1-5, U-17, U-28, TAX-07/08 duplicate, rule-cluster consolidation, hostname-based
   alias merges.

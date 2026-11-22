# Business glossary (candidate) — loop-01

| ID | Term | Definition | Synonyms | Realised by | Grade | Status |
|---|---|---|---|---|---|---|
| CON-11 | **Child** | A child named on a childcare account. | — | Child | C | approved (provisional) — simulated |
| CON-09 | **Childcare Account** | An account a parent uses to pay a registered childcare provider. | — | ChildcareAccount | C | approved (provisional) — simulated |
| CON-10 | **Childcare Provider** | A registered nursery, childminder or club that is paid from a childcare account. | — | — | C | approved (provisional) — simulated |
| CON-01 | **Customer** | A person who has a tax, National Insurance or childcare relationship with the agency. | Taxpayer, Citizen, Person | — | C | approved (provisional) — simulated |
| CON-03 | **Employer** | An organisation that pays employees and files PAYE returns. | — | Employer | C | approved (provisional) — simulated |
| CON-04 | **Employment** | A period during which a person is paid by an employer. | — | Employment | C | approved (provisional) — simulated |
| CON-07 | **NI Contribution** | An amount of National Insurance due for a pay period. | — | NiContribution | C | approved (provisional) — simulated |
| CON-08 | **NI Record** | A person's yearly contribution history, including qualifying years. | — | NiRecord | C | approved (provisional) — simulated |
| CON-02 | **National Insurance Number** | The lifelong reference that identifies a person for National Insurance. | NINO | National Insurance Number | C | approved (provisional) — simulated |
| CON-05 | **Pay Period** | One period of pay, such as a week or month, reported in an employer return. | — | PayPeriod | C | approved (provisional) — simulated |
| CON-06 | **Tax Code** | A code that tells the employer how much tax-free pay to allow for an employment. | — | TaxCode | C | approved (provisional) — simulated |
| CON-12 | **Top-up Payment** | The government contribution added to a parent's payment into a childcare account. | — | — | C | approved (provisional) — simulated |

## Classifications

| ID | Taxonomy | Values | Grade |
|---|---|---|---|
| TAX-01 | EmploymentStatus | {LIVE, CEASED} / {LIVE, CEASED, SUSPENDED} | X |
| TAX-02 | NiCategory | {A, B, C, H, J, M, Z} / {A, B, C, H, J, M, Z, V} | X |
| TAX-03 | ChildcareAccountStatus | OPEN, SUSPENDED, CLOSED | B |
| TAX-04 | CorrespondencePreference | POST, DIGITAL | C |
| TAX-05 | AddressType | RESIDENTIAL, CORRESPONDENCE | C |
| TAX-06 | QualifyingYear | YES, NO | C |
| TAX-07 | EligibilityOutcome | ELIGIBLE, NOT_ELIGIBLE | C |

## Business rules

| ID | Rule | Grade | Source |
|---|---|---|---|
| RUL-01 | No module may change another module's tables without a Core Systems change request. | C | docs/taxcore-system-overview.md |
| RUL-02 | Every release of TAXCORE requires a full regression test of all modules. | C | docs/taxcore-system-overview.md |
| RUL-03 | Every employment must be linked to exactly one employer and one person. | C | docs/paye-operations-manual.md |
| RUL-04 | A tax code must be issued before PAYE can be calculated for an employment. | C | docs/paye-operations-manual.md |
| RUL-05 | Employer returns received after the filing deadline are flagged for penalty review. | C | docs/paye-operations-manual.md |
| RUL-06 | A person must have exactly one National Insurance Number for life. | C | docs/national-insurance-procedures.md |
| RUL-07 | A tax year counts as a qualifying year when contributions reach the lower earnings limit. | C | docs/national-insurance-procedures.md |
| RUL-08 | Contributions must not be calculated for a person after their recorded date of death. | C | docs/national-insurance-procedures.md |
| RUL-09 | A parent must reconfirm eligibility every three months. | C | docs/childcare-scheme-guide.md |
| RUL-10 | A parent whose expected income exceeds 100,000 is not eligible. | C | docs/childcare-scheme-guide.md |
| RUL-11 | The top-up must be paid within one working day of the parent payment. | C | docs/childcare-scheme-guide.md |
| RUL-12 | A childcare account must be closed when the account holder dies. | C | docs/childcare-scheme-guide.md |

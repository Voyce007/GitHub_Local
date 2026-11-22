# Business glossary (candidate) — loop-01

| ID | Term | Definition | Synonyms | Realised by | Grade | Status |
|---|---|---|---|---|---|---|
| CON-11 | **Child** | A child named on a childcare account. | — | Child | C | proposed |
| CON-09 | **Childcare Account** | An account a parent uses to pay a registered childcare provider. | — | ChildcareAccount | C | proposed |
| CON-10 | **Childcare Provider** | A registered nursery, childminder or club that is paid from a childcare account. | — | — | C | proposed |
| CON-16 | **Class 1 Contribution** |  | — | — | D | proposed |
| CON-01 | **Customer** | A person who has a tax, National Insurance or childcare relationship with the agency. | Taxpayer, Citizen, Person | — | C | proposed |
| CON-19 | **Eligibility Check** |  | — | EligibilityCheck | D | proposed |
| CON-03 | **Employer** | An organisation that pays employees and files PAYE returns. | — | Employer | C | proposed |
| CON-13 | **Employer Return** |  | — | — | D | proposed |
| CON-04 | **Employment** | A period during which a person is paid by an employer. | — | Employment | C | proposed |
| CON-17 | **Expected Income** |  | — | — | D | proposed |
| CON-15 | **Lower Earnings Limit** |  | — | — | D | proposed |
| CON-07 | **NI Contribution** | An amount of National Insurance due for a pay period. | — | NiContribution | C | proposed |
| CON-08 | **NI Record** | A person's yearly contribution history, including qualifying years. | — | NiRecord | C | proposed |
| CON-02 | **National Insurance Number** | The lifelong reference that identifies a person for National Insurance. | NINO | National Insurance Number | C | proposed |
| CON-18 | **Parent** |  | — | — | D | proposed |
| CON-20 | **Parent Payment** |  | — | — | D | proposed |
| CON-05 | **Pay Period** | One period of pay, such as a week or month, reported in an employer return. | — | PayPeriod | C | proposed |
| CON-14 | **Qualifying Year** | A tax year in which contributions reach the lower earnings limit. | — | — | C | proposed |
| CON-06 | **Tax Code** | A code that tells the employer how much tax-free pay to allow for an employment. | — | TaxCode | C | proposed |
| CON-12 | **Top-up Payment** | The government contribution added to a parent's payment into a childcare account. | — | — | C | proposed |

## Classifications

| ID | Taxonomy | Values | Grade |
|---|---|---|---|
| TAX-01 | EmploymentStatus | {LIVE, CEASED} / {LIVE, CEASED, SUSPENDED} | X |
| TAX-02 | NiCategory | {A, B, C, H, J, M, Z} / {A, B, C, H, J, M, Z, V} | X |
| TAX-03 | ChildcareAccountStatus | OPEN, SUSPENDED, CLOSED | B |
| TAX-04 | CorrespondencePreference | POST, DIGITAL | C |
| TAX-05 | AddressType | RESIDENTIAL, CORRESPONDENCE | C |
| TAX-06 | EligibilityOutcome | ELIGIBLE, NOT_ELIGIBLE | C |
| TAX-07 | QualifyingYear | YES, NO | C |
| TAX-08 | NI Qualifying Year Flag | YES, NO | C |

## Business rules

| ID | Rule | Grade | Source |
|---|---|---|---|
| RUL-01 | National Insurance Number issued at first registration | C | docs/taxcore-system-overview.md |
| RUL-02 | Cross-module table change control | C | docs/taxcore-system-overview.md |
| RUL-03 | Full regression test per release | C | docs/taxcore-system-overview.md |
| RUL-04 | Quarterly childcare eligibility check | C | docs/business-capability-map.md |
| RUL-05 | Employment links to one employer and one person | C | docs/paye-operations-manual.md |
| RUL-06 | Tax code before PAYE calculation | C | docs/paye-operations-manual.md |
| RUL-07 | Late employer returns flagged for penalty review | C | docs/paye-operations-manual.md |
| RUL-08 | National Insurance Number issued at age 16 | C | docs/national-insurance-procedures.md |
| RUL-09 | One National Insurance Number for life | C | docs/national-insurance-procedures.md |
| RUL-10 | Qualifying year threshold | C | docs/national-insurance-procedures.md |
| RUL-11 | No contributions after death | C | docs/national-insurance-procedures.md |
| RUL-12 | Childcare eligibility based on expected income | C | docs/childcare-scheme-guide.md |
| RUL-13 | Quarterly eligibility reconfirmation | B | code-examples/childcare-portal.properties, docs/childcare-scheme-guide.md |
| RUL-14 | Childcare income limit | C | code-examples/taxcore_procedures.sql, docs/childcare-scheme-guide.md |
| RUL-15 | Top-up paid within one working day | C | docs/childcare-scheme-guide.md |
| RUL-16 | Close childcare account on death of account holder | C | docs/childcare-scheme-guide.md |
| RUL-17 | Close accounts of deceased persons | C | spreadsheets/taxcore-batch-jobs.csv |
| RUL-18 | No contributions after death (code) | C | code-examples/taxcore_procedures.sql |
| RUL-19 | Childcare income limit (code) | C | code-examples/taxcore_procedures.sql |
| RUL-20 | Top-up is 25% of parent payment | C | code-examples/taxcore_procedures.sql |
| RUL-21 | Close childcare account on death (code) | C | code-examples/taxcore_procedures.sql |
| RUL-22 | Quarterly eligibility reconfirmation (config) | C | code-examples/childcare-portal.properties |
| RUL-23 | NI contributions excluded for deceased persons | C | code-examples/taxcore_procedures.sql |
| RUL-24 | Childcare top-up rate | C | code-examples/taxcore_procedures.sql |
| RUL-25 | Close childcare accounts of deceased | C | code-examples/taxcore_procedures.sql |
| RUL-26 | NI contribution thresholds and rates | C | code-examples/taxcore_procedures.sql |

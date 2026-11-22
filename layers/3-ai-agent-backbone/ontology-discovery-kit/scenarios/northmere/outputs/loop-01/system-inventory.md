# Candidate system inventory — loop-01

Hypothesis built from documents and example code. Every row needs confirmation.

| ID | System | Aliases | Roles | Grade | Sources | Entities | Open unknowns |
|---|---|---|---|---|---|---|---|
| SYS-06 | **ChildcarePortal** | parent account, CC | processing: parent payments to childcare providers | B | 3 | — | — |
| SYS-02 | **CitizenPortal** | online account, CP | processing: customer self-service requests | B | 3 | — | — |
| SYS-04 | **EmployerGateway** | employer filing, EG | processing: employer returns for every pay period | B | 3 | — | — |
| SYS-07 | **income-verify-svc** | — | — | C | 1 | — | U-08 |
| SYS-05 | **NumberHub** | NI allocation, NH | system of record (candidate): National Insurance numbers | B | 4 | — | — |
| SYS-03 | **RevenueWarehouse** | MI warehouse, RW | reporting / analytics (candidate) | B | 3 | — | — |
| SYS-01 | **TAXCORE** | Core, TC | system of record (candidate): Customer; database: db2; data-holding application (candidate) | B | 7 | Person, Address, Employer, Employment, TaxCode, PayPeriod, NiContribution, NiRecord, ChildcareAccount, Child, ChildcarePayment, EligibilityCheck | U-04 |

## Data flows

| From | To | Labels | Grade |
|---|---|---|---|
| CitizenPortal | TAXCORE | CUS-01 | B |
| EmployerGateway | TAXCORE | PAY-01 employer returns | B |
| NumberHub | TAXCORE | NIN-02 | B |
| ChildcarePortal | TAXCORE | CC-01 parent payments | B |
| TAXCORE | RevenueWarehouse | MI-01 nightly | B |
| ChildcarePortal | NumberHub | runtime dependency (config) | C |
| ChildcarePortal | income-verify-svc | runtime dependency (config) | C |

## Interfaces

| ID | Mechanism | Source → Target | Payload | Grade |
|---|---|---|---|---|
| CUS-01 | REST API | CitizenPortal → TAXCORE | Customer details; addresses | B |
| PAY-01 | File (XML) | EmployerGateway → TAXCORE | Employer return | B |
| NIN-02 | MQ message | NumberHub → TAXCORE | National Insurance Number | B |
| CC-01 | REST API | ChildcarePortal → TAXCORE | Parent payment | B |
| MI-01 | File (CSV) | TAXCORE → RevenueWarehouse | All modules | B |

# Candidate system inventory — loop-01

Hypothesis built from documents and example code. Every row needs confirmation.

| ID | System | Aliases | Roles | Grade | Sources | Entities | Open unknowns |
|---|---|---|---|---|---|---|---|
| SYS-06 | **ChildcarePortal** | the parent account, parent account, CC, ChildcarePortal (parent account) | channel; childcare parent payment capture (candidate) | B | 4 | — | — |
| SYS-02 | **CitizenPortal** | the online account, online account, CP, CitizenPortal (online account) | channel; customer self-service (candidate) | B | 3 | — | — |
| SYS-04 | **EmployerGateway** | employer filing, EG, EmployerGateway (employer filing) | channel; employer return capture (candidate) | B | 3 | — | — |
| SYS-07 | **income-verify-svc** | income-verify | — | C | 1 | — | U-15 |
| SYS-05 | **NumberHub** | NI allocation, NH, NumberHub (NI allocation), numberhub | identifier issuer (candidate): National Insurance Number | B | 4 | — | — |
| SYS-03 | **RevenueWarehouse** | the MI warehouse, MI warehouse, RW, RevenueWarehouse (MI warehouse) | reporting / analytics (candidate) | B | 3 | — | — |
| SYS-01 | **TAXCORE** | the Core, TC, TC_, TAXCORE (the Core), taxcore-db | system of record (candidate): Customer; system of record (candidate): PAYE; system of record (candidate): National Insurance; system of record (candidate): Childcare; calculation engine (candidate): stored procedures run by overnight batch; identifier issuer (candidate): National Insurance Number; identifier issuer (candidate): Person Id; calculation engine (candidate): PAYE; calculation engine (candidate): NI contributions; calculation engine (candidate): batch jobs; calculation engine (candidate): stored procedures; database (candidate): DB2 | B | 9 | Person, Address, Employer, Employment, TaxCode, PayPeriod, NiContribution, NiRecord, ChildcareAccount, Child, ChildcarePayment, EligibilityCheck | U-04 |

## Data flows

| From | To | Labels | Grade |
|---|---|---|---|
| CitizenPortal | TAXCORE | Customer details; addresses | B |
| EmployerGateway | TAXCORE | Employer return | B |
| NumberHub | TAXCORE | National Insurance Number | B |
| ChildcarePortal | TAXCORE | Parent payment | B |
| TAXCORE | RevenueWarehouse | All modules | B |
| ChildcarePortal | NumberHub | NumberHub API call | C |
| ChildcarePortal | income-verify-svc | income-verify API call | C |

## Interfaces

| ID | Mechanism | Source → Target | Payload | Grade |
|---|---|---|---|---|
| CUS-01 | REST API | CitizenPortal → TAXCORE | Customer details; addresses | B |
| PAY-01 | File (XML) | EmployerGateway → TAXCORE | Employer return | B |
| NIN-02 | MQ message | NumberHub → TAXCORE | National Insurance Number | B |
| CC-01 | REST API | ChildcarePortal → TAXCORE | Parent payment | B |
| MI-01 | File (CSV) | TAXCORE → RevenueWarehouse | All modules | B |
| ChildcarePortal-TAXCORE-JDBC | JDBC (DB2) | ChildcarePortal → TAXCORE |  | C |
| ChildcarePortal-NumberHub-API | HTTPS API | ChildcarePortal → NumberHub |  | C |
| ChildcarePortal-IncomeVerify-API | HTTPS API | ChildcarePortal → income-verify-svc |  | C |

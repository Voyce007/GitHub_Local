# Candidate system inventory — loop-01

Hypothesis built from documents and example code. Every row needs confirmation.

| ID | System | Aliases | Roles | Grade | Sources | Entities | Open unknowns |
|---|---|---|---|---|---|---|---|
| SYS-02 | **CoreLedger** | Account Platform, CL | system of record (candidate): Account; database: DB2; data-holding application (candidate) | B | 7 | Account, AccountHolder | U-02 |
| SYS-01 | **CustHub** | Customer Hub, CRM, CH | system of record (candidate): Customer; data-holding application (candidate) | B | 6 | Customer, CustomerAddress, Address | U-03 |
| SYS-07 | **DataMart** | MI warehouse, DM | reporting / analytics (candidate) | B | 3 | — | — |
| SYS-08 | **mandate-svc** | — | — | C | 1 | — | U-10 |
| SYS-04 | **Mobile Banking** | MB | channel | B | 4 | — | — |
| SYS-03 | **ONB** | — | onboarding front end | B | 3 | — | — |
| SYS-06 | **PayRail** | Payments Platform, PR | processing: outbound customer payments; data-holding application (candidate) | B | 5 | PaymentInstruction | U-04 |
| SYS-05 | **Web Banking** | WB | channel | B | 2 | — | — |

## Data flows

| From | To | Labels | Grade |
|---|---|---|---|
| Mobile Banking | PayRail | PAY-01 payment instruction | B |
| Web Banking | ONB | application | C |
| ONB | CustHub | new application | C |
| CustHub | CoreLedger | CUST-ACC-01 | B |
| PayRail | CoreLedger | PaymentCompleted | B |
| CoreLedger | DataMart | MI-01 nightly | B |
| CustHub | DataMart | MI-02 nightly | B |
| Mobile Banking | CustHub | runtime dependency (config) | C |
| Mobile Banking | CoreLedger | runtime dependency (config) | C |
| Mobile Banking | mandate-svc | runtime dependency (config) | C |

## Interfaces

| ID | Mechanism | Source → Target | Payload | Grade |
|---|---|---|---|---|
| CUST-ACC-01 | MQ message | CustHub → CoreLedger | Customer Number; customer type; name | B |
| PAY-01 | REST API | Mobile Banking → PayRail | Payment instruction | B |
| PAY-EVT-02 | Event | PayRail → CoreLedger | PaymentCompleted | C |
| MI-01 | File (CSV) | CoreLedger → DataMart | Accounts; balances | B |
| MI-02 | File (CSV) | CustHub → DataMart | Customers | B |

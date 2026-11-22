# Candidate system inventory — loop-02

Hypothesis built from documents and example code. Every row needs confirmation.

| ID | System | Aliases | Roles | Grade | Sources | Entities | Open unknowns |
|---|---|---|---|---|---|---|---|
| SYS-01 | **CustHub** | Customer Hub, CRM, CH | system of record (candidate): Customer; data-holding application (candidate) | A | 8 | Customer, CustomerAddress, Address | U-07 |
| SYS-07 | **DataMart** | MI warehouse, DM | reporting / analytics (candidate) | B | 3 | — | — |
| SYS-02 | **LedgerOne** | ERP, GL, LO | system of record (candidate): Invoice; system of record (candidate): general ledger; database: postgresql; data-holding application (candidate) | B | 8 | LegalEntity, CostCentre, Account, Invoice, CustomerEntity | U-02 |
| SYS-03 | **OrderFlow** | OMS, Order Management System, OF | processing: customer orders; data-holding application (candidate) | B | 6 | OrderRequest, OrderLine | U-03 |
| SYS-05 | **Partner Portal** | PP | channel | B | 2 | — | — |
| SYS-06 | **RiskReg** | GRC platform, RR | system of record (candidate): Risk; data-holding application (candidate) | B | 4 | Risk, Control | U-04 |
| SYS-08 | **TaxEngine** | tax-engine | calculation: sales tax for every invoice line | B | 2 | — | — |
| SYS-04 | **Web Shop** | WS | channel | B | 4 | — | — |

## Data flows

| From | To | Labels | Grade |
|---|---|---|---|
| Web Shop | OrderFlow | ORD-01 order request | B |
| Partner Portal | CustHub | registration | C |
| CustHub | LedgerOne | CUST-FIN-01 | B |
| OrderFlow | LedgerOne | OrderFulfilled | B |
| LedgerOne | DataMart | MI-01 nightly | B |
| CustHub | DataMart | MI-02 nightly | B |
| RiskReg | DataMart | RISK-01 weekly | B |
| Web Shop | CustHub | runtime dependency (config) | C |
| Web Shop | LedgerOne | runtime dependency (config) | C |
| Web Shop | TaxEngine | runtime dependency (config) | C |

## Interfaces

| ID | Mechanism | Source → Target | Payload | Grade |
|---|---|---|---|---|
| CUST-FIN-01 | MQ message | CustHub → LedgerOne | Customer Number; customer type; name | B |
| ORD-01 | REST API | Web Shop → OrderFlow | Order request | B |
| ORD-EVT-02 | Event | OrderFlow → LedgerOne | OrderFulfilled | C |
| MI-01 | File (CSV) | LedgerOne → DataMart | Invoices; GL balances | B |
| MI-02 | File (CSV) | CustHub → DataMart | Customers | B |
| RISK-01 | File (CSV) | RiskReg → DataMart | Risks; controls | B |

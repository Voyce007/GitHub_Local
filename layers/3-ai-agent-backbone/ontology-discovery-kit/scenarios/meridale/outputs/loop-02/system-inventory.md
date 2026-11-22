# Candidate system inventory — loop-02

Hypothesis built from documents and example code. Every row needs confirmation.

| ID | System | Aliases | Roles | Grade | Sources | Entities | Open unknowns |
|---|---|---|---|---|---|---|---|
| SYS-08 | **CreditScore** | credit-score-svc | calculation: an external credit score for every new customer | B | 2 | — | — |
| SYS-04 | **FinCore** | ERP, GL, FC | system of record (candidate): Invoice; system of record (candidate): general ledger; data-holding application (candidate) | B | 8 | LegalEntity, CostCentre, Account, Invoice, CustomerEntity | U-01 |
| SYS-07 | **InsightHub** | MI warehouse, IH | reporting / analytics (candidate) | B | 3 | — | — |
| SYS-06 | **RiskVault** | GRC platform, RV | system of record (candidate): Risk; data-holding application (candidate) | B | 4 | Risk, Control | U-02 |
| SYS-05 | **Sales Desk** | — | channel | C | 1 | — | — |
| SYS-02 | **ServiceLink** | contracts system, SL | system of record (candidate): Client; data-holding application (candidate) | B | 5 | Client, ServiceContract | U-03 |
| SYS-03 | **ShopFront** | web store, online order platform, SF | processing: online orders for Meridale Direct; channel; processing: web orders; data-holding application (candidate) | B | 6 | OrderRequest, OrderLine | U-04 |
| SYS-01 | **TradeDesk** | Industrial CRM, TD | system of record (candidate): Customer; data-holding application (candidate) | A | 8 | Customer, CustomerAddress, Address | U-06 |

## Data flows

| From | To | Labels | Grade |
|---|---|---|---|
| ShopFront | FinCore | ORD-FIN-02 web orders | B |
| TradeDesk | FinCore | CUST-FIN-01 | B |
| ServiceLink | FinCore | CLI-FIN-03 daily file | B |
| FinCore | InsightHub | MI-01 nightly | B |
| TradeDesk | InsightHub | MI-02 nightly | B |
| RiskVault | InsightHub | RISK-01 weekly | B |
| ShopFront | TradeDesk | runtime dependency (config) | C |
| ShopFront | CreditScore | runtime dependency (config) | C |

## Interfaces

| ID | Mechanism | Source → Target | Payload | Grade |
|---|---|---|---|---|
| CUST-FIN-01 | MQ message | TradeDesk → FinCore | Customer Number; customer type; name | B |
| CLI-FIN-03 | File (CSV) | ServiceLink → FinCore | Client Ref; client name | B |
| ORD-FIN-02 | REST API | ShopFront → FinCore | Order request | B |
| INV-EVT-04 | Event | FinCore → InsightHub | InvoiceRaised | C |
| MI-01 | File (CSV) | FinCore → InsightHub | Invoices; GL balances | B |
| MI-02 | File (CSV) | TradeDesk → InsightHub | Customers; credit limits | B |
| RISK-01 | File (CSV) | RiskVault → InsightHub | Risks; controls | B |

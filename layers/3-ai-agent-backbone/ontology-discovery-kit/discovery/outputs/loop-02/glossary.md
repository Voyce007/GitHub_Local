# Business glossary (candidate) — loop-02

| ID | Term | Definition | Synonyms | Realised by | Grade | Status |
|---|---|---|---|---|---|---|
| CON-10 | **Control** | An activity that reduces the likelihood or impact of a risk. | — | Control | C | approved (provisional) — simulated |
| CON-08 | **Cost Centre** | A unit of the organisation to which costs are assigned for management reporting. | — | CostCentre | C | approved (provisional) — simulated |
| CON-01 | **Customer** | A party that buys, or has applied to buy, products or services from a group company. | Client, Account | Customer | C | approved (provisional) — simulated |
| CON-03 | **Customer Number** | The unique identifier for a customer, issued by LedgerOne when the first invoice is raised. | Customer ID, Debtor Number | Customer Number | C | approved (provisional) — simulated |
| CON-06 | **Invoice** | A request for payment issued by a legal entity to a customer. | — | Invoice | C | approved (provisional) — simulated |
| CON-07 | **Legal Entity** | A registered company within the group that can trade and raise invoices. | — | LegalEntity | C | approved (provisional) — simulated |
| CON-05 | **Order** | A customer's request to buy one or more products. | — | — | C | approved (provisional) — simulated |
| CON-02 | **Party** | A person or organisation the group has a relationship with. | — | — | C | approved (provisional) — simulated |
| CON-04 | **Product** | Something the group offers for sale, whether goods or services. | — | — | C | approved (provisional) — simulated |
| CON-09 | **Risk** | An uncertain event that could affect the group's objectives. | — | Risk | C | approved (provisional) — simulated |
| CON-11 | **Tax Code** | A code that determines how sales tax is applied to an invoice line. | — | — | C | approved (provisional) — simulated |

## Classifications

| ID | Taxonomy | Values | Grade |
|---|---|---|---|
| TAX-01 | CustomerType | INDIVIDUAL, SOLE_TRADER, COMPANY | B |
| TAX-02 | CreditStatus | PENDING, APPROVED, DECLINED, REFERRED | B |
| TAX-03 | OrderStatus | DRAFT, SUBMITTED, CONFIRMED, FULFILLED, CANCELLED | B |
| TAX-04 | RiskRating | LOW, MEDIUM, HIGH | B |
| TAX-05 | ControlType | PREVENTIVE, DETECTIVE | B |
| TAX-06 | AddressType | BILLING, DELIVERY | C |

## Business rules

| ID | Rule | Grade | Source |
|---|---|---|---|
| RUL-01 | A customer must pass a credit check before their first order is accepted. | C | loop-01/docs/customer-onboarding-process.md |
| RUL-02 | Every invoice must be raised by exactly one legal entity. | C | loop-01/docs/customer-onboarding-process.md |
| RUL-03 | A customer cannot be deleted while they have unpaid invoices. | C | loop-01/docs/customer-onboarding-process.md |
| RUL-04 | An order must reference exactly one customer. | C | loop-01/docs/order-to-cash-overview.md |
| RUL-05 | An order must not exceed the customer's credit limit. | C | loop-01/docs/order-to-cash-overview.md |
| RUL-06 | Every risk must have an owning cost centre. | C | loop-01/docs/risk-management-policy.md |
| RUL-07 | Every risk rated High must have at least one preventive control. | C | loop-01/docs/risk-management-policy.md |
| RUL-08 | Every control must be tested at least once a year. | C | loop-01/docs/risk-management-policy.md |
| RUL-09 | customerNumber must be 10 characters | C | loop-01/code-examples/CustomerRecord.java |
| RUL-10 | dateOfBirth is required for individuals | C | loop-01/code-examples/CustomerRecord.java |
| RUL-11 | an order must have at least one line | C | loop-01/code-examples/OrderStatus.java |

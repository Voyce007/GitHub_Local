# Business glossary (candidate) — loop-01

| ID | Term | Definition | Synonyms | Realised by | Grade | Status |
|---|---|---|---|---|---|---|
| CON-13 | **Control** | An activity that reduces the likelihood or impact of a risk. | — | Control | C | approved (provisional) — simulated |
| CON-11 | **Cost Centre** | A unit of the organisation to which costs are assigned for management reporting. | — | CostCentre | C | approved (provisional) — simulated |
| CON-08 | **Credit Limit** | The most the group will let a customer owe across all group companies. | — | — | C | approved (provisional) — simulated |
| CON-01 | **Customer** | A person or organisation that buys, or has applied to buy, from any company in the group. | Client, Account, Debtor | Customer | C | approved (provisional) — simulated |
| CON-03 | **Customer Number** | The group-wide identifier for a customer, used on every invoice. | Customer ID, Debtor Number | Customer Number | C | approved (provisional) — simulated |
| CON-09 | **Exposure** | The total a customer owes the group, plus accepted orders not yet invoiced. | — | — | C | approved (provisional) — simulated |
| CON-07 | **Invoice** | A request for payment issued by a legal entity to a customer. | — | Invoice | C | approved (provisional) — simulated |
| CON-10 | **Legal Entity** | A registered company within the group that can trade and raise invoices. | — | LegalEntity | C | approved (provisional) — simulated |
| CON-05 | **Order** | A customer's request to buy one or more products. | — | — | C | approved (provisional) — simulated |
| CON-02 | **Party** | A person or organisation the group has a relationship with. | — | — | C | approved (provisional) — simulated |
| CON-04 | **Product** | Something the group offers for sale, whether goods or services. | — | — | C | approved (provisional) — simulated |
| CON-12 | **Risk** | An uncertain event that could affect the group's objectives. | — | Risk | C | approved (provisional) — simulated |
| CON-06 | **Service Contract** | An agreement to maintain a customer's machines for a period. | — | ServiceContract | C | approved (provisional) — simulated |

## Classifications

| ID | Taxonomy | Values | Grade |
|---|---|---|---|
| TAX-01 | CustomerType | INDIVIDUAL, SOLE_TRADER, COMPANY, PUBLIC_BODY | B |
| TAX-02 | OrderStatus | {OPEN, SHIPPED, CANCELLED} / {BASKET, PLACED, PAID, SHIPPED, DELIVERED, CANCELLED} | X |
| TAX-03 | CreditStatus | {APPROVED, ON_HOLD, STOPPED} / {APPROVED, ON_HOLD, STOPPED, PROVISIONAL} | X |
| TAX-04 | RiskRating | LOW, MEDIUM, HIGH | B |
| TAX-05 | ControlType | PREVENTIVE, DETECTIVE | B |
| TAX-06 | AddressType | BILLING, DELIVERY | C |

## Business rules

| ID | Rule | Grade | Source |
|---|---|---|---|
| RUL-01 | A customer must have an approved credit status before their first order is accepted. | C | docs/customer-onboarding-standard.md |
| RUL-02 | Every invoice must be raised by exactly one legal entity. | C | docs/customer-onboarding-standard.md |
| RUL-03 | A customer cannot be deleted while they have unpaid invoices. | C | docs/customer-onboarding-standard.md |
| RUL-04 | An order must reference exactly one customer. | C | docs/order-to-cash-overview.md |
| RUL-05 | An order must not exceed the customer's credit limit. | C | docs/order-to-cash-overview.md |
| RUL-06 | Total exposure to a customer must be measured across all legal entities in the group. | C | docs/group-credit-policy.md |
| RUL-07 | A customer whose credit status is Stopped cannot place new orders in any operating company. | C | docs/group-credit-policy.md |
| RUL-08 | Credit limits above 250,000 GBP must be approved by the Group Credit Controller. | C | docs/group-credit-policy.md |
| RUL-09 | Every risk must have an owning cost centre. | C | docs/risk-management-policy.md |
| RUL-10 | Customer concentration risk must be reviewed every month. | C | docs/risk-management-policy.md |
| RUL-11 | Every risk rated High must have at least one preventive control. | C | docs/risk-management-policy.md |
| RUL-12 | customerNumber must be 10 characters | C | code-examples/CustomerRecord.java |
| RUL-13 | regNumber is required for companies | C | code-examples/CustomerRecord.java |
| RUL-14 | an order must have at least one line | C | code-examples/OrderRequest.java |

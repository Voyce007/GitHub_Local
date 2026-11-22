# Business glossary (candidate) — loop-01

| ID | Term | Definition | Synonyms | Realised by | Grade | Status |
|---|---|---|---|---|---|---|
| CON-04 | **Account** | A record of balances and transactions held for one or more customers in CoreLedger. | — | Account | C | approved (provisional) — simulated |
| CON-05 | **Current Account** | A product that provides day-to-day banking with a debit card and an overdraft option. | — | — | C | approved (provisional) — simulated |
| CON-01 | **Customer** | A party that holds or has applied for a product with the bank. | Client, Account Holder | Customer | C | approved (provisional) — simulated |
| CON-03 | **Customer Number** | The unique identifier for a customer, issued by ONB at application time. | Customer ID, CIF | Customer Number | C | approved (provisional) — simulated |
| CON-07 | **Mandate** | A standing authority for a third party to collect payments from an account. | — | — | C | approved (provisional) — simulated |
| CON-02 | **Party** | A person or organisation the bank has a relationship with. | — | — | C | approved (provisional) — simulated |
| CON-06 | **Payment** | An instruction to move money from a debit account to a beneficiary. | — | — | C | approved (provisional) — simulated |
| CON-08 | **Product Variant** | A particular configuration of a product, such as a Current Account with a premium fee tier. | — | — | C | approved (provisional) — simulated |

## Classifications

| ID | Taxonomy | Values | Grade |
|---|---|---|---|
| TAX-01 | CustomerType | {INDIVIDUAL, BUSINESS} / {INDIVIDUAL, SOLE_TRADER, COMPANY} | X |
| TAX-02 | KycStatus | PENDING, PASSED, FAILED, REFERRED | B |
| TAX-03 | PaymentStatus | {PENDING, COMPLETED, FAILED, CANCELLED} / {RECEIVED, VALIDATED, PENDING, COMPLETED, FAILED, CANCELLED} | X |
| TAX-04 | AddressType | HOME, CORRESPONDENCE | C |

## Business rules

| ID | Rule | Grade | Source |
|---|---|---|---|
| RUL-01 | A customer must pass KYC checks before an account can be opened. | C | docs/customer-onboarding-process.md |
| RUL-02 | Every account must have at least one account holder. | C | docs/customer-onboarding-process.md |
| RUL-03 | A customer cannot hold more than one Current Account of the same product variant. | C | docs/customer-onboarding-process.md |
| RUL-04 | A payment must not exceed the available balance of the debit account. | C | docs/payments-overview.md |
| RUL-05 | A payment must reference exactly one debit account. | C | docs/payments-overview.md |
| RUL-06 | customerNumber must be 10 characters | C | code-examples/CustomerRecord.java |
| RUL-07 | dateOfBirth is required for individuals | C | code-examples/CustomerRecord.java |

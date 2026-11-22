# Change register — loop-01 → loop-02

Playbook phase 10: every change since the previous baseline, for the approvers to review.

- Graded up: 21 · graded down: 0 · added: 3 · removed: 0
- Contradictions resolved: 3
- Unknowns closed: 7 · new: 0 · still open: 16

## Contradictions resolved

| ID | Element | Property | Now | Decided by | Superseded |
|---|---|---|---|---|---|
| TAX-02 | taxonomy OrderStatus | values | BASKET, PLACED, PAID, SHIPPED, DELIVERED, CANCELLED | answers/sme-answers-2026-12-10.md | OPEN, SHIPPED, CANCELLED |
| TAX-03 | taxonomy CreditStatus | values | APPROVED, PROVISIONAL, ON_HOLD, STOPPED | answers/sme-answers-2026-12-10.md | APPROVED, ON_HOLD, STOPPED |
| IDN-01 | identifier Customer Number | issued_by | FinCore | answers/sme-answers-2026-12-10.md | TradeDesk |

## Grade changes

| ID | Element | From | To | Why |
|---|---|---|---|---|
| ATT-07 | attribute Customer.createdTimestamp | C | A | confirmed by a real system artefact |
| ATT-06 | attribute Customer.creditLimit | B | A | confirmed by a real system artefact |
| ATT-05 | attribute Customer.creditStatus | B | A | confirmed by a real system artefact |
| ATT-01 | attribute Customer.customerNumber | B | A | confirmed by a real system artefact |
| ATT-02 | attribute Customer.customerType | B | A | confirmed by a real system artefact |
| ATT-03 | attribute Customer.fullName | B | A | confirmed by a real system artefact |
| ATT-04 | attribute Customer.regNumber | B | A | confirmed by a real system artefact |
| ATT-09 | attribute CustomerAddress.addressType | C | A | confirmed by a real system artefact |
| ATT-08 | attribute CustomerAddress.customerNumber | C | A | confirmed by a real system artefact |
| ATT-10 | attribute CustomerAddress.line1 | C | A | confirmed by a real system artefact |
| ATT-11 | attribute CustomerAddress.postcode | C | A | confirmed by a real system artefact |
| CON-01 | concept Customer | C | B | 2 independent current sources |
| CON-05 | concept Order | C | B | 2 independent current sources |
| ENT-01 | entity Customer | B | A | confirmed by a real system artefact |
| ENT-02 | entity CustomerAddress | C | A | confirmed by a real system artefact |
| IDN-01 | identifier Customer Number | X | A | confirmed by a real system artefact |
| REL-01 | relationship CustomerAddress → Customer | C | A | confirmed by a real system artefact |
| SYS-08 | system CreditScore | C | B | 2 independent current sources |
| SYS-01 | system TradeDesk | B | A | confirmed by a real system artefact |
| TAX-03 | taxonomy CreditStatus | X | B | 2 independent current sources (contradiction resolved by answers/sme-answers-2026-12-10.md) |
| TAX-02 | taxonomy OrderStatus | X | B | 2 independent current sources (contradiction resolved by answers/sme-answers-2026-12-10.md) |

## Added

- ATT-57 attribute Customer.updatedTimestamp (A)
- ATT-58 attribute CustomerAddress.line2 (A)
- ATT-59 attribute CustomerAddress.countryCode (A)

## Removed

- none

## Unknowns closed

- U-01 (loop-01): Is 'Account' a synonym of Customer, or a different concept (a role) that shares the name?
- U-02 (loop-01): Is 'Client' a synonym of Customer, or a different concept (a role) that shares the name?
- U-08 (loop-01): Sources disagree on the issued by of identifier 'Customer Number'. Which is correct today?
- U-09 (loop-01): Sources disagree on the values of taxonomy 'CreditStatus'. Which is correct today?
- U-10 (loop-01): Sources disagree on the values of taxonomy 'OrderStatus'. Which is correct today?
- U-12 (loop-01): Are these the same thing? 'OrderRequest' looks like 'Order' with a role suffix.
- U-14 (loop-01): What is 'credit-score-svc', who owns it, and does it master any data?

## Unknowns opened

- none

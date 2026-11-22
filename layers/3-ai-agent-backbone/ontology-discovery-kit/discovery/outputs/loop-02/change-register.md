# Change register — loop-01 → loop-02

Playbook phase 10: every change since the previous baseline, for the approvers to review.

- Graded up: 19 · graded down: 0 · added: 3 · removed: 0
- Contradictions resolved: 3
- Unknowns closed: 4 · new: 0 · still open: 16

## Contradictions resolved

| ID | Element | Property | Now | Decided by | Superseded |
|---|---|---|---|---|---|
| TAX-01 | taxonomy CustomerType | values | INDIVIDUAL, SOLE_TRADER, COMPANY | answers/sme-answers-2026-12-10.md | INDIVIDUAL, BUSINESS |
| TAX-03 | taxonomy OrderStatus | values | DRAFT, SUBMITTED, CONFIRMED, FULFILLED, CANCELLED | answers/sme-answers-2026-12-10.md | OPEN, FULFILLED, CANCELLED |
| IDN-01 | identifier Customer Number | issued_by | CustHub | answers/sme-answers-2026-12-10.md | LedgerOne |

## Grade changes

| ID | Element | From | To | Why |
|---|---|---|---|---|
| ATT-07 | attribute Customer.createdTimestamp | C | A | confirmed by a real system artefact |
| ATT-06 | attribute Customer.creditStatus | B | A | confirmed by a real system artefact |
| ATT-01 | attribute Customer.customerNumber | B | A | confirmed by a real system artefact |
| ATT-02 | attribute Customer.customerType | B | A | confirmed by a real system artefact |
| ATT-04 | attribute Customer.dateOfBirth | B | A | confirmed by a real system artefact |
| ATT-05 | attribute Customer.emailAddress | B | A | confirmed by a real system artefact |
| ATT-03 | attribute Customer.fullName | B | A | confirmed by a real system artefact |
| ATT-09 | attribute CustomerAddress.addressType | C | A | confirmed by a real system artefact |
| ATT-08 | attribute CustomerAddress.customerNumber | C | A | confirmed by a real system artefact |
| ATT-10 | attribute CustomerAddress.line1 | C | A | confirmed by a real system artefact |
| ATT-11 | attribute CustomerAddress.postcode | C | A | confirmed by a real system artefact |
| ENT-01 | entity Customer | B | A | confirmed by a real system artefact |
| ENT-02 | entity CustomerAddress | C | A | confirmed by a real system artefact |
| IDN-01 | identifier Customer Number | X | A | confirmed by a real system artefact |
| REL-01 | relationship CustomerAddress → Customer | C | A | confirmed by a real system artefact |
| SYS-01 | system CustHub | B | A | confirmed by a real system artefact |
| SYS-08 | system TaxEngine | C | B | 2 independent current sources |
| TAX-01 | taxonomy CustomerType | X | B | 2 independent current sources (contradiction resolved by answers/sme-answers-2026-12-10.md) |
| TAX-03 | taxonomy OrderStatus | X | B | 2 independent current sources (contradiction resolved by answers/sme-answers-2026-12-10.md) |

## Added

- ATT-45 attribute Customer.updatedTimestamp (A)
- ATT-46 attribute CustomerAddress.line2 (A)
- ATT-47 attribute CustomerAddress.countryCode (A)

## Removed

- none

## Unknowns closed

- U-06 (loop-01): Sources disagree on the issued by of identifier 'Customer Number'. Which is correct today?
- U-07 (loop-01): Sources disagree on the values of taxonomy 'CustomerType'. Which is correct today?
- U-08 (loop-01): Sources disagree on the values of taxonomy 'OrderStatus'. Which is correct today?
- U-12 (loop-01): What is 'tax-engine', who owns it, and does it master any data?

## Unknowns opened

- none

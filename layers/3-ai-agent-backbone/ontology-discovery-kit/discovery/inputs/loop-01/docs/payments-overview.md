# Payments Overview

Version 1.0 · June 2019 · Payments Architecture

## Summary

PayRail (the Payments Platform) processes all outbound customer payments.
Mobile Banking submits a payment instruction to PayRail over the PAY-01 API.
PayRail debits the account in CoreLedger (CL) and publishes a PaymentCompleted event.
Reporting extracts are sent nightly to the MI warehouse.

## Classifications

Payment status values: Pending, Completed, Failed, Cancelled.

## Rules

- A payment must not exceed the available balance of the debit account.
- A payment must reference exactly one debit account.

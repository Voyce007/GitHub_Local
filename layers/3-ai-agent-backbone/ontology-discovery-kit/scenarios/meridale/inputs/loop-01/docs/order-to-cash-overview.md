# Order-to-Cash Overview

Version 1.0 · May 2019 · Finance Systems

## Summary

ShopFront (the online order platform) processes all web orders.
ShopFront sends each order to FinCore over the ORD-FIN-02 interface for invoicing.
FinCore (GL) publishes an InvoiceRaised event when an invoice is created.
Reporting extracts are sent nightly to the MI warehouse.

## Classifications

Order status values: Open, Shipped, Cancelled.

## Rules

- An order must reference exactly one customer.
- An order must not exceed the customer's credit limit.

# Order-to-Cash Overview

Version 1.0 · June 2019 · Finance Systems

## Summary

OrderFlow (the Order Management System) processes all customer orders.
Web Shop submits each order to OrderFlow over the ORD-01 API.
OrderFlow sends fulfilled orders to LedgerOne (GL) and publishes an OrderFulfilled event.
Reporting extracts are sent nightly to the MI warehouse.

## Classifications

Order status values: Open, Fulfilled, Cancelled.

## Rules

- An order must reference exactly one customer.
- An order must not exceed the customer's credit limit.

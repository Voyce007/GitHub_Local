# Customer Onboarding Standard

Version 2.0 · February 2023 · Group Sales Operations

## Purpose

How each operating company sets up a new customer so that they can order and be invoiced.

## Systems involved

TradeDesk (also called the Industrial CRM or "TD") holds the customer record for Meridale Industrial.
ServiceLink (also called the contracts system) holds the client record for Meridale Services.
ShopFront (also called the web store) captures and fulfils online orders for Meridale Direct.
FinCore (also called the ERP or "the GL") raises invoices and maintains the general ledger.

## Process

1. The customer registers through a Channel (ShopFront or Sales Desk).
2. The operating company system creates the customer record and requests a credit check.
3. The Customer Number is issued by TradeDesk when the record is created.
4. TradeDesk sends the new customer to FinCore through the CUST-FIN-01 interface.
5. FinCore links the customer to the legal entity that will invoice them.

## Rules

- A customer must have an approved credit status before their first order is accepted.
- Every invoice must be raised by exactly one legal entity.
- A customer cannot be deleted while they have unpaid invoices.

## Classifications

Customer type values: Individual, Sole Trader, Company, Public Body.

# Customer Onboarding — Process Description

Version 3.1 · March 2022 · Sales Operations

## Purpose

Describes how a new customer is set up so that they can order products and be invoiced.

## Systems involved

CustHub (also called Customer Hub or "the CRM") holds the customer record.
LedgerOne (also called the ERP or "the GL") raises invoices and maintains the general ledger.
OrderFlow (also called OMS) captures and fulfils customer orders.

## Process

1. The customer registers through a Channel (Web Shop or Partner Portal).
2. CustHub creates the customer record and runs a credit check.
3. The Customer Number is issued by CustHub when the record is created.
4. CustHub sends the new customer to LedgerOne through the CUST-FIN-01 interface.
5. LedgerOne links the customer to the legal entity that will invoice them.

## Rules

- A customer must pass a credit check before their first order is accepted.
- Every invoice must be raised by exactly one legal entity.
- A customer cannot be deleted while they have unpaid invoices.

## Classifications

Customer type values: Individual, Business.

Credit status values: Pending, Approved, Declined, Referred.

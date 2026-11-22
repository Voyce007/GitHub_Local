# Customer Onboarding — Process Description

Version 3.1 · March 2022 · Operations Design

## Purpose

Describes how a new customer is onboarded for a Current Account.

## Systems involved

CustHub (also called Customer Hub or "the CRM") holds the customer record.
CoreLedger (also called the Account Platform) opens and maintains accounts.
The onboarding front end is referred to as ONB.

## Process

1. The applicant completes the application in a Channel (Mobile Banking or Web Banking).
2. ONB passes the application to CustHub, which creates the customer record.
3. The Customer Number is issued by CustHub when the record is created.
4. CustHub sends the new customer to CoreLedger through the CUST-ACC-01 interface.
5. CoreLedger opens the Current Account and links it to the customer.

## Rules

- A customer must pass KYC checks before an account can be opened.
- Every account must have at least one account holder.
- A customer cannot hold more than one Current Account of the same product variant.

## Classifications

Customer type values: Individual, Business.

KYC status values: Pending, Passed, Failed, Referred.

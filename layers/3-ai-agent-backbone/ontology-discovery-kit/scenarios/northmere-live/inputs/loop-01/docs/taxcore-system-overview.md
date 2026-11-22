# TAXCORE System Overview

Version 4.2 · September 2016 · Core Systems

## Summary

TAXCORE (also called "the Core" or "TC") holds the customer record and every PAYE, National Insurance and childcare record in one DB2 database.
All calculations run as stored procedures inside TAXCORE, scheduled by overnight batch jobs.
CitizenPortal (also called the online account) captures and fulfils customer self-service requests.
RevenueWarehouse (also called the MI warehouse) receives nightly extracts for reporting.

## Identifiers

The National Insurance Number is issued by TAXCORE when a person is first registered.
Every record in TAXCORE is keyed on the internal Person Id.

## Rules

- No module may change another module's tables without a Core Systems change request.
- Every release of TAXCORE requires a full regression test of all modules.

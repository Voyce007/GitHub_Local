# PAYE Operations Manual (extract)

Version 7.0 · April 2023 · PAYE Operations

## Overview

EmployerGateway (also called employer filing) captures and fulfils employer returns for every pay period.
Returns are loaded into TAXCORE overnight, where PAYE is calculated for each employment.

## Rules

- Every employment must be linked to exactly one employer and one person.
- A tax code must be issued before PAYE can be calculated for an employment.
- Employer returns received after the filing deadline are flagged for penalty review.

## Classifications

Employment status values: Live, Ceased.

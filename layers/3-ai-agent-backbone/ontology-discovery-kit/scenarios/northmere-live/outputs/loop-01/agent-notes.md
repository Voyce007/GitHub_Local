# Agent notes — loop-01

Observations the agents recorded alongside their findings. Reviewers should read these: they often hold the most useful judgment, such as undocumented dependencies or doubts about a source.

## Enterprise Architect agent (23)

- **system TAXCORE**: Source is a 2016 document (stale); it predates the 2022 NumberHub carve-out.
- **system TAXCORE**: Conflicts with docs/national-insurance-procedures.md lines 7 and 13 (NumberHub issues NINO; replaced TAXCORE allocation module in 2022). This 2016 source is stale; likely superseded. Question for EA Authority.
- **system TAXCORE**: States TAXCORE once had an NI allocation module, replaced by NumberHub in 2022.
- **system TAXCORE**: Data dictionary attributed to TAXCORE by manifest system_hint (table_prefix TC_). Tables cover person, address, employer, employment, tax code, pay period, NI contribution/record, childcare account/child/payment/eligibility.
- **system TAXCORE**: Batch job catalogue attributed to TAXCORE by manifest system_hint.
- **system TAXCORE**: Interface catalogue uses 'TC' as target here and 'TAXCORE' elsewhere; TC is a stated alias in the overview.
- **system TAXCORE**: Diagram node id TC.
- **system TAXCORE**: ChildcarePortal connects directly to the TAXCORE DB2 database over JDBC (shared-database dependency).
- **system CitizenPortal**: Diagram node id CP.
- **system RevenueWarehouse**: Diagram node id RW.
- **system EmployerGateway**: Diagram node id EG.
- **system NumberHub**: Same line says it replaced the TAXCORE allocation module in 2022.
- **system NumberHub**: Diagram node id NH.
- **system NumberHub**: ChildcarePortal backend calls a NumberHub API; this dependency is not in the interface catalogue or diagram.
- **system ChildcarePortal**: Diagram node id CC (not to be confused with interface id CC-01).
- **system income-verify-svc**: Unknown system: appears only in ChildcarePortal config. Not in the interface catalogue or the current-state diagram; no stated purpose. Name suggests income verification, possibly related to childcare eligibility (expected income) - question for SMEs.
- **flow MI-01 Nightly extract**: Source text does not name the sender explicitly; inferred TAXCORE from the document subject. Matches interface MI-01.
- **flow PAY-01 Employer returns**: Previous line names EmployerGateway as capturing the returns. Catalogue says Daily; manual says overnight.
- **flow ChildcarePortal -> TAXCORE database (JDBC)**: Runtime dependency from config; data direction not stated. Not in interface catalogue (which lists CC-01 as REST API). Possible undocumented shared-database integration.
- **flow ChildcarePortal -> NumberHub API**: Runtime dependency from config; data direction and payload not stated; undocumented in interface catalogue and diagram.
- **flow ChildcarePortal -> income-verify-svc API**: Runtime dependency from config; purpose not stated; undocumented elsewhere.
- **domain Childcare**: income-verify-svc placement is speculative (only seen in ChildcarePortal config).
- **capability Calculate NI Contributions**: SQL comment does not state an owner; owner_team copied exactly from the capability map / batch job catalogue for the same capability name.

## Business Analyst agent (43)

- **concept Customer**: Glossary lists Person as a synonym of Customer; TAXCORE keys every record on an internal Person Id (DA identifier) and other sources use 'person' for non-customers (e.g. a registered child). Whether Person is truly a synonym is an SME question.
- **concept National Insurance Number**: Also an identifier (DA scope); issuer is contested between TAXCORE (2016 overview) and NumberHub (2023 NI procedures).
- **concept Employer**: Employer Reference appears as the TC_EMPLOYER key in the data dictionary (DA identifier).
- **concept NI Contribution**: Data dictionary splits it into employee and employer contribution amounts (DA attributes).
- **concept Customer**: Mentions 'the customer record' held in TAXCORE; no definition. Source is stale (2016).
- **concept National Insurance Number**: Stale (2016) source; pre-dates the 2022 NumberHub carve-out.
- **rule National Insurance Number issued at first registration**: CONTRADICTS national-insurance-procedures.md line 12 (issued by NumberHub when a person reaches 16). This source is stale (2016) and pre-dates the 2022 NumberHub carve-out; the newer operational source is preferred but both are proposed as written. Issuer is also a DA identifier concern.
- **rule Cross-module table change control**: IT governance rule rather than a business-domain rule; stale (2016) source.
- **rule Full regression test per release**: IT delivery rule rather than a business-domain rule; stale (2016) source.
- **concept Employer Return**: Capability text describes 'each employer's pay and deductions return for every pay period'; not a glossary definition. No source defines Employer Return formally - gap for SME.
- **rule Quarterly childcare eligibility check**: Derived from a capability description (capability itself belongs to EA). Corroborates childcare-scheme-guide.md line 12.
- **concept Employer Return**: Employer returns are captured per pay period by EmployerGateway (system, EA scope); no definition given.
- **rule Employment links to one employer and one person**: Also implies DA relationships Employment-Employer and Employment-Person.
- **rule Late employer returns flagged for penalty review**: 'Filing deadline' and 'penalty review' are not defined anywhere in this batch - gap for SME.
- **taxonomy EmploymentStatus**: CONTRADICTS taxcore-data-dictionary.csv line 20, which also lists Suspended. Proposed as written.
- **concept National Insurance Number**: States issuer (NumberHub) and timing (age 16); no definition.
- **rule National Insurance Number issued at age 16**: CONTRADICTS taxcore-system-overview.md line 14 (issued by TAXCORE at first registration). This source is newer (2023) and operational, so preferred, but the contradiction is left for SME resolution.
- **rule Qualifying year threshold**: The lower earnings limit value is not given in this batch.
- **concept Qualifying Year**: Defined only through the rule sentence. Data dictionary holds a Y/N qualifying flag per tax year on TC_NI_RECORD (DA attribute).
- **concept Lower Earnings Limit**: Used but not defined; no value given. Gap for SME.
- **concept Class 1 Contribution**: Calculated from the earnings in each employer return; no definition of Class 1 or of other classes.
- **taxonomy NiCategory**: CONTRADICTS taxcore-data-dictionary.csv line 33, which also lists V. Proposed as written.
- **rule Childcare eligibility based on expected income**: How expected income is derived is not stated here; taxcore_procedures.sql line 25 derives it as SUM(GROSS_PAY) * 4 (calculation, Engineering scope). A separate income-verify-svc appears in the ChildcarePortal config.
- **concept Expected Income**: Used but not defined (period, gross/net). Data dictionary calls it 'Expected annual income'.
- **concept Parent**: Not defined in the glossary. childcare-scheme-guide.md line 15 uses 'account holder'; whether Parent and Account Holder are the same role is an SME question.
- **rule Quarterly eligibility reconfirmation**: Batch catalogue runs the eligibility check job daily (J310); frequency of the job vs. the reconfirmation period may differ - not a contradiction as written.
- **rule Top-up paid within one working day**: Batch catalogue shows the top-up calculation (J320) running in real time.
- **taxonomy CorrespondencePreference**: Codes PST/DIG on TC_PERSON.CORR_PREF.
- **taxonomy AddressType**: Codes RES/COR on TC_ADDRESS.ADDR_TYPE.
- **taxonomy EmploymentStatus**: Codes LIV/CEA/SUS. CONTRADICTS paye-operations-manual.md line 18 (Live, Ceased only). Proposed as written.
- **taxonomy NiCategory**: CONTRADICTS national-insurance-procedures.md line 22, which omits V. Proposed as written.
- **taxonomy ChildcareAccountStatus**: Codes OPN/SUS/CLO.
- **taxonomy EligibilityOutcome**: Codes ELG/NEL on TC_ELIGIBILITY_CHECK.OUTCOME.
- **concept Eligibility Check**: Only a table/column name (TC_ELIGIBILITY_CHECK.CHECK_ID); no definition. Entity itself is DA scope.
- **rule Close accounts of deceased persons**: Job J330 writes TC_CHILDCARE_ACCOUNT and TC_NI_RECORD, so it may affect NI records as well as childcare accounts - the effect on NI records is not stated anywhere. Owned by Customer Services.
- **concept Employer Return**: Payload of interface PAY-01 (interface is DA/Engineering scope).
- **concept Parent Payment**: Payload of interface CC-01. Not defined in the glossary; Top-up Payment definition refers to 'a parent's payment into a childcare account'.
- **concept Parent Payment**: Edge label on CC-01 from ChildcarePortal to TAXCORE.
- **rule No contributions after death (code)**: Implemented in PRC_CALC_NIC. Corroborates national-insurance-procedures.md line 18. Stale example code (2020).
- **rule Childcare income limit (code)**: PRC_CHECK_ELIGIBILITY. Expected income is derived as SUM(GROSS_PAY) * 4 (calculation, Engineering scope). Stale example code (2020).
- **rule Top-up is 25% of parent payment**: PRC_CALC_TOPUP; the calculation itself is Engineering scope. No document states the 25% rate. Stale example code (2020).
- **rule Close childcare account on death (code)**: PRC_CLOSE_DECEASED sets STATUS = 'CLO' (line 42). Corroborates childcare-scheme-guide.md line 15.
- **rule Quarterly eligibility reconfirmation (config)**: Feature flag corroborates childcare-scheme-guide.md line 12. The config also references an income-verify-svc (system, EA scope) not shown in the context diagram or interface catalogue.

## Data Architect agent (22)

- **identifier National Insurance Number**: Nullable in TC_PERSON (CHAR(9), Y), so a person can exist before a number is allocated. No issuer stated in this source.
- **entity Address**: No primary key is declared for this table in the data dictionary; the natural key is unconfirmed.
- **taxonomy EmploymentStatus**: Dictionary lists SUS=Suspended; the PAYE Operations Manual lists only Live and Ceased.
- **attribute PayPeriod.niCategory**: No code list on this column; assumed to share the NiCategory code list from TC_NI_CONTRIBUTION.NI_CATEGORY.
- **taxonomy NiCategory**: Dictionary includes V; the National Insurance Procedures list only A, B, C, H, J, M, Z.
- **taxonomy QualifyingYear**: Yes/No flag; may be better modelled as a boolean.
- **attribute Child.personId**: Nullable reference to TC_PERSON with no foreign key declared.
- **attribute ChildcarePayment.childcareProviderReference**: References a childcare provider; no provider table exists in this dictionary and no foreign key is declared.
- **identifier Childcare Provider Reference**: Identifies a childcare provider held outside TAXCORE (no provider table in the dictionary). Issuer unknown.
- **entity NiContribution**: Example code (2020, simplified); corroborates the table, not its full structure.
- **identifier National Insurance Number**: 2020 example code generates the number inside TAXCORE from sequence SEQ_NINO. Pre-dates the 2022 NumberHub carve-out described in the National Insurance Procedures; may be obsolete.
- **taxonomy EligibilityOutcome**: Code uses NEL/ELG; labels taken from the data dictionary code list.
- **entity Person**: Table named in the batch-job catalogue reads/writes; the manifest gives no table_prefix for this file, TC_ stripped for consistency with the data dictionary.
- **identifier National Insurance Number**: Job J020 (PRC_ALLOCATE_NINO, daily) still writes TC_PERSON in a 2024 catalogue, after the 2022 NumberHub carve-out. Unclear whether TAXCORE still generates the number or only stores the number received from NumberHub (NIN-02). No issuer asserted here.
- **identifier National Insurance Number**: Interface NIN-02 'NI number allocated' sends the National Insurance Number from NumberHub to TAXCORE in real time.
- **identifier National Insurance Number**: Source is stale (2016) and pre-dates the 2022 NumberHub carve-out. Contradicts docs/national-insurance-procedures.md (issued by NumberHub, at age 16 rather than first registration).
- **identifier Person Id**: 'Internal' Person Id; issued_by TAXCORE inferred from 'internal'. Source is stale (2016).
- **identifier National Insurance Number**: Contradicts docs/taxcore-system-overview.md (issued by TAXCORE at first registration). This source is newer (2023) and states NumberHub replaced the TAXCORE allocation module in 2022.
- **taxonomy NiCategory**: Data dictionary code list for TC_NI_CONTRIBUTION.NI_CATEGORY also includes V.
- **taxonomy EmploymentStatus**: Data dictionary code list for TC_EMPLOYMENT.STATUS also includes SUS=Suspended.
- **relationship ChildcareAccount → Person**: The Person referenced by the account is the account holder (parent).
- **relationship PayPeriod → Employment**: Glossary says a pay period is reported in an employer return; the dictionary links it to an employment.

## Engineering agent (27)

- **calculation PRC_REGISTER_PERSON**: From the batch-job catalogue (TAXCORE). Column-level writes not stated in the catalogue.
- **calculation PRC_ALLOCATE_NINO**: From the batch-job catalogue (TAXCORE). Column-level writes not stated in the catalogue. TC_PERSON listed as both read and written; counted as written only. Still scheduled Daily in TAXCORE although the NI procedures say NumberHub replaced the TAXCORE allocation module in 2022.
- **calculation PRC_CALC_PAYE**: From the batch-job catalogue (TAXCORE). Column-level writes not stated in the catalogue. TC_PAY_PERIOD listed as both read and written; counted as written only.
- **calculation PRC_CALC_TOPUP**: From the batch-job catalogue (TAXCORE). Column-level writes not stated in the catalogue. TC_CHILDCARE_PAYMENT listed as both read and written; counted as written only.
- **calculation PRC_CLOSE_DECEASED**: From the batch-job catalogue (TAXCORE). Column-level writes not stated in the catalogue. Catalogue says it writes TC_NI_RECORD too; the 2020 procedure extract only updates TC_CHILDCARE_ACCOUNT. Contradiction for review.
- **calculation PRC_CALC_NIC**: Stored procedure from the 2020 example extract (simplified, stale). INSERT INTO TC_NI_CONTRIBUTION from TC_PAY_PERIOD joined to TC_EMPLOYMENT and TC_PERSON, excluding persons with DATE_OF_DEATH set. Hard-coded thresholds 1048/758 and rates 0.08/0.138.
- **calculation PRC_ALLOCATE_NINO**: Stored procedure from the 2020 example extract (simplified, stale). UPDATE TC_PERSON SET NI_NUMBER from sequence SEQ_NINO. Writes an NI-domain column in the person table. Extract dates from 2020, before the 2022 NumberHub carve-out.
- **calculation PRC_CHECK_ELIGIBILITY**: Stored procedure from the 2020 example extract (simplified, stale). INSERT INTO TC_ELIGIBILITY_CHECK; expected income = SUM(GROSS_PAY) * 4, outcome NEL when > 100000 else ELG. Childcare domain reads PAYE tables directly.
- **calculation PRC_CALC_TOPUP**: Stored procedure from the 2020 example extract (simplified, stale). UPDATE TC_CHILDCARE_PAYMENT SET TOPUP_AMOUNT = PARENT_AMOUNT * 0.25 (table both read and written; counted as written).
- **calculation PRC_CLOSE_DECEASED**: Stored procedure from the 2020 example extract (simplified, stale). UPDATE TC_CHILDCARE_ACCOUNT SET STATUS = 'CLO' for persons with DATE_OF_DEATH set. Does not touch TC_NI_RECORD, unlike the batch-job catalogue entry.
- **interface CUS-01**: Catalogue row. Target 'TC' is an alias of TAXCORE.
- **interface PAY-01**: Catalogue row.
- **interface CUS-01**: Edge in current-state context diagram (transcribed from a slide).
- **interface MI-01**: Prose mention matching catalogue MI-01 (stale 2016 doc); ID not stated in the text.
- **interface PAY-01**: Prose mention matching catalogue PAY-01; ID not stated in the text.
- **interface ChildcarePortal-TAXCORE-JDBC**: Not in the interface catalogue. ChildcarePortal backend connects directly to the TAXCORE DB2 database (port 50000), bypassing CC-01.
- **interface ChildcarePortal-NumberHub-API**: Not in the interface catalogue or diagram.
- **interface ChildcarePortal-IncomeVerify-API**: Not in the interface catalogue or diagram; income-verify-svc appears in no other source. Childcare guide says expected income comes from PAYE employment records, and PRC_CHECK_ELIGIBILITY reads TC_PAY_PERIOD; possible contradiction.
- **event NationalInsuranceNumberAllocated**: Catalogue interface 'NI number allocated' is an MQ message, real time.
- **taxonomy Correspondence Preference Code**: Code list from the TAXCORE data dictionary.
- **taxonomy Employment Status Code**: Code list includes SUS=Suspended; PAYE Operations Manual lists only Live, Ceased. Contradiction for Business Domain Owner.
- **taxonomy NI Category Code**: Code list includes V; NI procedures list A, B, C, H, J, M, Z only. Contradiction for Business Domain Owner.
- **taxonomy Eligibility Outcome Code**: Codes NEL/ELG used as literals in PRC_CHECK_ELIGIBILITY; labels from the data dictionary.
- **rule NI contributions excluded for deceased persons**: Matches the NI procedures rule on date of death.
- **rule Childcare income limit**: Sum of all pay periods x 4 as annual income looks questionable; flag for review.
- **rule NI contribution thresholds and rates**: No floor at zero in the extract; hard-coded values in a simplified 2020 extract.
- **rule Quarterly eligibility reconfirmation**: Feature flag; matches the guide's three-monthly reconfirmation rule.


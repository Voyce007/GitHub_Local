# Diagrams — loop-01

Generated from the graded model by `ontokit`, one set per agent. Node colours show evidence grade: A confirmed · B corroborated · C single source (dashed) · D assumed · X contradicted.

## Business Analyst · Concept map

Business terms by domain. Rounded boxes are concepts; dotted links are synonyms; arrows point to the entity that holds each concept. "(undefined)" marks a term used without a definition.

```mermaid
flowchart LR
    CON_01(["Customer"])
    CON_15(["Lower Earnings Limit (undefined)"])
    CON_17(["Expected Income (undefined)"])
    CON_18(["Parent (undefined)"])
    CON_20(["Parent Payment (undefined)"])
  subgraph dom_childcare["childcare"]
    CON_09(["Childcare Account"])
    CON_10(["Childcare Provider"])
    CON_11(["Child"])
    CON_12(["Top-up Payment"])
    CON_19(["Eligibility Check (undefined)"])
  end
  subgraph dom_ni["ni"]
    CON_02(["National Insurance Number"])
    CON_07(["NI Contribution"])
    CON_08(["NI Record"])
    CON_14(["Qualifying Year"])
    CON_16(["Class 1 Contribution (undefined)"])
  end
  subgraph dom_paye["paye"]
    CON_03(["Employer"])
    CON_04(["Employment"])
    CON_05(["Pay Period"])
    CON_06(["Tax Code"])
    CON_13(["Employer Return (undefined)"])
  end
  syn_CON_01_Taxpayer["Taxpayer"] -. synonym .- CON_01
  syn_CON_01_Citizen["Citizen"] -. synonym .- CON_01
  syn_CON_01_Person["Person"] -. synonym .- CON_01
  syn_CON_02_NINO["NINO"] -. synonym .- CON_02
  CON_03 --> ENT_03[("Employer")]
  CON_04 --> ENT_04[("Employment")]
  CON_05 --> ENT_06[("Pay Period")]
  CON_06 --> ENT_05[("Tax Code")]
  CON_07 --> ENT_07[("Ni Contribution")]
  CON_08 --> ENT_08[("Ni Record")]
  CON_09 --> ENT_09[("Childcare Account")]
  CON_11 --> ENT_10[("Child")]
  CON_19 --> ENT_12[("Eligibility Check")]

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class ENT_03,ENT_04,ENT_06,ENT_05,ENT_07,ENT_08,ENT_09,ENT_10,ENT_12 gB
  class CON_01,CON_09,CON_10,CON_11,CON_12,CON_02,CON_07,CON_08,CON_14,CON_03,CON_04,CON_05,CON_06 gC
  class CON_15,CON_17,CON_18,CON_20,CON_19,CON_16,CON_13 gD
```

## Enterprise Architect · System context

Each system with its candidate role and known aliases, and the data flows between them, labelled with interface ids.

```mermaid
flowchart LR
  SYS_01["<b>TAXCORE</b><br/>system of record (candidate): Customer<br/><i>aka the Core, TC, TC_</i>"]
  SYS_02["<b>CitizenPortal</b><br/>channel<br/><i>aka the online account, online account, CP</i>"]
  SYS_03["<b>RevenueWarehouse</b><br/>reporting / analytics (candidate)<br/><i>aka the MI warehouse, MI warehouse, RW</i>"]
  SYS_04["<b>EmployerGateway</b><br/>channel<br/><i>aka employer filing, EG, EmployerGateway (employer filing)</i>"]
  SYS_05["<b>NumberHub</b><br/>identifier issuer (candidate): National Insurance Number<br/><i>aka NI allocation, NH, NumberHub (NI allocation)</i>"]
  SYS_06["<b>ChildcarePortal</b><br/>channel<br/><i>aka the parent account, parent account, CC</i>"]
  SYS_07["<b>income-verify-svc</b><br/>role unknown<br/><i>aka income-verify</i>"]
  SYS_02 -->|"Customer details; addresses"| SYS_01
  SYS_04 -->|"Employer return"| SYS_01
  SYS_05 -->|"National Insurance Number"| SYS_01
  SYS_06 -->|"Parent payment"| SYS_01
  SYS_01 -->|"All modules"| SYS_03
  SYS_06 -->|"NumberHub API call"| SYS_05
  SYS_06 -->|"income-verify API call"| SYS_07

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class SYS_01,SYS_02,SYS_03,SYS_04,SYS_05,SYS_06 gB
  class SYS_07 gC
```

## Enterprise Architect · Capability map

Business capabilities grouped by their one accountable team. In a decomposition, these teams decide domain ownership.

```mermaid
flowchart TB
  subgraph team_0["Customer Services"]
    direction TB
    CAP_01["Register Customer"]
    CAP_02["Record Life Events"]
  end
  subgraph team_1["Family Support"]
    direction TB
    CAP_09["Open Childcare Account"]
    CAP_10["Check Childcare Eligibility"]
    CAP_11["Calculate Childcare Top-up"]
  end
  subgraph team_2["NI Operations"]
    direction TB
    CAP_06["Allocate NI Number"]
    CAP_07["Calculate NI Contributions"]
    CAP_08["Maintain NI Record"]
  end
  subgraph team_3["PAYE Operations"]
    direction TB
    CAP_03["Process Employer Returns"]
    CAP_04["Issue Tax Code"]
    CAP_05["Calculate PAYE"]
  end

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class CAP_01,CAP_02,CAP_03,CAP_04,CAP_05,CAP_06,CAP_07,CAP_08,CAP_09,CAP_10,CAP_11 gB
```

## Data Architect · Entity-relationship diagram

Entities with up to 8 attributes each (PK marks a key), and relationships with cardinality. Labels show how each link is made and its grade.

```mermaid
erDiagram
  Person {
    integer personId PK "grade C"
    char nationalInsuranceNumber PK "grade C"
    varchar forename "grade C"
    varchar surname "grade C"
    date dateOfBirth "grade C"
    date dateOfDeath "grade C"
    char correspondencePreference "grade C"
  }
  Address {
    integer personId "grade C"
    char addressType "grade C"
    varchar addressLine1 "grade C"
    varchar postcode "grade C"
  }
  Employer {
    varchar employerReference PK "grade C"
    varchar employerName "grade C"
  }
  Employment {
    integer employmentId PK "grade C"
    integer personId "grade C"
    varchar employerReference "grade C"
    date startDate "grade C"
    date endDate "grade C"
    char status "grade C"
  }
  TaxCode {
    integer employmentId "grade C"
    varchar taxCode "grade C"
    date effectiveFrom "grade C"
  }
  PayPeriod {
    integer employmentId "grade C"
    char taxYear "grade C"
    smallint periodNumber "grade C"
    decimal grossPay "grade C"
    decimal taxDeducted "grade C"
    char niCategory "grade C"
  }
  NiContribution {
    integer employmentId "grade C"
    char taxYear "grade C"
    smallint periodNumber "grade C"
    char niCategory "grade C"
    decimal employeeNiContribution "grade C"
    decimal employerNiContribution "grade C"
  }
  NiRecord {
    integer personId "grade C"
    char taxYear "grade C"
    char qualifyingYear "grade C"
    decimal class1Total "grade C"
  }
  ChildcareAccount {
    integer childcareAccountId PK "grade C"
    integer personId "grade C"
    char status "grade C"
    date openedDate "grade C"
  }
  Child {
    integer childId PK "grade C"
    integer childcareAccountId "grade C"
    integer personId "grade C"
    varchar forename "grade C"
    date dateOfBirth "grade C"
  }
  ChildcarePayment {
    integer paymentId PK "grade C"
    integer childcareAccountId "grade C"
    varchar childcareProviderReference "grade C"
    decimal parentAmount "grade C"
    decimal topUpAmount "grade C"
    date paidDate "grade C"
  }
  EligibilityCheck {
    integer checkId PK "grade C"
    integer childcareAccountId "grade C"
    date checkDate "grade C"
    decimal expectedIncome "grade C"
    char outcome "grade C"
  }
  Address }o--|| Person : "TC_ADDRESS.PERSON_ID (C)"
  Employment }o--|| Person : "TC_EMPLOYMENT.PERSON_ID (B)"
  Employment }o--|| Employer : "TC_EMPLOYMENT.EMPLOYER_REF (B)"
  TaxCode }o--|| Employment : "TC_TAX_CODE.EMPLOYMENT_ID (C)"
  PayPeriod }o--|| Employment : "TC_PAY_PERIOD.EMPLOYMENT_ID (B)"
  NiContribution }o--|| Employment : "TC_NI_CONTRIBUTION.EMPLOYMENT_ID (C)"
  NiRecord }o--|| Person : "TC_NI_RECORD.PERSON_ID (C)"
  ChildcareAccount }o--|| Person : "TC_CHILDCARE_ACCOUNT.PERSON_ID (B)"
  Child }o--|| ChildcareAccount : "TC_CHILD.CC_ACCOUNT_ID (B)"
  ChildcarePayment }o--|| ChildcareAccount : "TC_CHILDCARE_PAYMENT.CC_ACCOUNT_ID (C)"
  EligibilityCheck }o--|| ChildcareAccount : "TC_ELIGIBILITY_CHECK.CC_ACCOUNT_ID (C)"
  Child }o--|| Person : "TC_CHILD.PERSON_ID (C)"
  NiContribution ||--|| PayPeriod : "TC_NI_CONTRIBUTION (EMPLOYMENT_ID, TAX_YEAR, PERIOD_NO) (C)"
  NiRecord ||--o{ NiContribution : "TC_NI_RECORD (PERSON_ID, TAX_YEAR) to TC_NI_CONTRIBUTION (EMPLOYMENT_ID -> PERSON_ID, TAX_YEAR) (C)"
```

## Engineer · Calculation data flow

Each batch job or stored procedure, grouped by domain. Thick arrows show the tables it changes (with columns, where known); dotted arrows show tables it only reads. Arrows that cross a domain boundary are what the decomposition must turn into services or events.

```mermaid
flowchart LR
  subgraph cd_childcare["childcare calculations"]
    CAL_08[["Open childcare account<br/><small>PRC_OPEN_CC_ACCOUNT</small>"]]
    CAL_09[["Check childcare eligibility<br/><small>PRC_CHECK_ELIGIBILITY</small>"]]
    CAL_10[["Calculate childcare top-up<br/><small>PRC_CALC_TOPUP</small>"]]
  end
  subgraph cd_customer["customer calculations"]
    CAL_01[["Register person<br/><small>PRC_REGISTER_PERSON</small>"]]
    CAL_11[["Close accounts of deceased<br/><small>PRC_CLOSE_DECEASED</small>"]]
  end
  subgraph cd_ni["ni calculations"]
    CAL_02[["Allocate NI number<br/><small>PRC_ALLOCATE_NINO</small>"]]
    CAL_06[["Calculate NI contributions<br/><small>PRC_CALC_NIC</small>"]]
    CAL_07[["Update NI record<br/><small>PRC_UPDATE_NI_RECORD</small>"]]
  end
  subgraph cd_paye["paye calculations"]
    CAL_03[["Load employer returns<br/><small>PRC_LOAD_RETURNS</small>"]]
    CAL_04[["Calculate PAYE<br/><small>PRC_CALC_PAYE</small>"]]
    CAL_05[["Issue tax codes<br/><small>PRC_ISSUE_TAX_CODE</small>"]]
  end
  CAL_01 ==> tbl_TC_PERSON
  CAL_01 ==> tbl_TC_ADDRESS
  CAL_02 ==>|"NI_NUMBER"| tbl_TC_PERSON
  CAL_03 ==> tbl_TC_EMPLOYMENT
  CAL_03 ==> tbl_TC_PAY_PERIOD
  tbl_TC_EMPLOYER -.-> CAL_03
  CAL_04 ==> tbl_TC_PAY_PERIOD
  tbl_TC_TAX_CODE -.-> CAL_04
  CAL_05 ==> tbl_TC_TAX_CODE
  tbl_TC_EMPLOYMENT -.-> CAL_05
  CAL_06 ==> tbl_TC_NI_CONTRIBUTION
  tbl_TC_PAY_PERIOD -.-> CAL_06
  tbl_TC_EMPLOYMENT -.-> CAL_06
  tbl_TC_PERSON -.-> CAL_06
  CAL_07 ==> tbl_TC_NI_RECORD
  tbl_TC_NI_CONTRIBUTION -.-> CAL_07
  CAL_08 ==> tbl_TC_CHILDCARE_ACCOUNT
  CAL_08 ==> tbl_TC_CHILD
  tbl_TC_PERSON -.-> CAL_08
  CAL_09 ==> tbl_TC_ELIGIBILITY_CHECK
  tbl_TC_CHILDCARE_ACCOUNT -.-> CAL_09
  tbl_TC_EMPLOYMENT -.-> CAL_09
  tbl_TC_PAY_PERIOD -.-> CAL_09
  CAL_10 ==>|"TOPUP_AMOUNT"| tbl_TC_CHILDCARE_PAYMENT
  CAL_11 ==>|"STATUS"| tbl_TC_CHILDCARE_ACCOUNT
  CAL_11 ==> tbl_TC_NI_RECORD
  tbl_TC_PERSON -.-> CAL_11
  subgraph td_childcare["childcare data"]
    tbl_TC_CHILD[("TC_CHILD")]
    tbl_TC_CHILDCARE_ACCOUNT[("TC_CHILDCARE_ACCOUNT")]
    tbl_TC_CHILDCARE_PAYMENT[("TC_CHILDCARE_PAYMENT")]
    tbl_TC_ELIGIBILITY_CHECK[("TC_ELIGIBILITY_CHECK")]
  end
  subgraph td_customer["customer data"]
    tbl_TC_ADDRESS[("TC_ADDRESS")]
    tbl_TC_PERSON[("TC_PERSON")]
  end
  subgraph td_ni["ni data"]
    tbl_TC_NI_CONTRIBUTION[("TC_NI_CONTRIBUTION")]
    tbl_TC_NI_RECORD[("TC_NI_RECORD")]
  end
  subgraph td_paye["paye data"]
    tbl_TC_EMPLOYER[("TC_EMPLOYER")]
    tbl_TC_EMPLOYMENT[("TC_EMPLOYMENT")]
    tbl_TC_PAY_PERIOD[("TC_PAY_PERIOD")]
    tbl_TC_TAX_CODE[("TC_TAX_CODE")]
  end

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class CAL_01,CAL_02,CAL_03,CAL_04,CAL_05,CAL_06,CAL_07,CAL_08,CAL_09,CAL_10,CAL_11 gC
```

## Ontology Steward · Alias merges

System names merged only where a source states they are the same. A diamond marks a system nobody explains.

```mermaid
flowchart LR
  SYS_01(["<b>TAXCORE</b>"])
  SYS_01_a0["the Core"] -- same system --> SYS_01
  SYS_01_a1["TC"] -- same system --> SYS_01
  SYS_01_a2["TC_"] -- same system --> SYS_01
  SYS_01_a3["TAXCORE (the Core)"] -- same system --> SYS_01
  SYS_01_a4["taxcore-db"] -- same system --> SYS_01
  SYS_02(["<b>CitizenPortal</b>"])
  SYS_02_a0["the online account"] -- same system --> SYS_02
  SYS_02_a1["online account"] -- same system --> SYS_02
  SYS_02_a2["CP"] -- same system --> SYS_02
  SYS_02_a3["CitizenPortal (online account)"] -- same system --> SYS_02
  SYS_03(["<b>RevenueWarehouse</b>"])
  SYS_03_a0["the MI warehouse"] -- same system --> SYS_03
  SYS_03_a1["MI warehouse"] -- same system --> SYS_03
  SYS_03_a2["RW"] -- same system --> SYS_03
  SYS_03_a3["RevenueWarehouse (MI warehouse)"] -- same system --> SYS_03
  SYS_04(["<b>EmployerGateway</b>"])
  SYS_04_a0["employer filing"] -- same system --> SYS_04
  SYS_04_a1["EG"] -- same system --> SYS_04
  SYS_04_a2["EmployerGateway (employer filing)"] -- same system --> SYS_04
  SYS_05(["<b>NumberHub</b>"])
  SYS_05_a0["NI allocation"] -- same system --> SYS_05
  SYS_05_a1["NH"] -- same system --> SYS_05
  SYS_05_a2["NumberHub (NI allocation)"] -- same system --> SYS_05
  SYS_05_a3["numberhub"] -- same system --> SYS_05
  SYS_06(["<b>ChildcarePortal</b>"])
  SYS_06_a0["the parent account"] -- same system --> SYS_06
  SYS_06_a1["parent account"] -- same system --> SYS_06
  SYS_06_a2["CC"] -- same system --> SYS_06
  SYS_06_a3["ChildcarePortal (parent account)"] -- same system --> SYS_06
  SYS_07(["<b>income-verify-svc</b>"])
  SYS_07_a0["income-verify"] -- same system --> SYS_07
  q_SYS_07{"What is it? Who owns it?"} -.- SYS_07

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class SYS_01,SYS_02,SYS_03,SYS_04,SYS_05,SYS_06 gB
  class SYS_07 gC
```

## Ontology Steward · Target decomposition

Each domain with the data it owns and its business services: rectangles are commands, rounded boxes are queries, double boxes are events. Arrows show which domain uses which service; dotted arrows show columns that move.

```mermaid
flowchart LR
  subgraph customer["Customer<br/><small>Director of Customer Services</small>"]
    direction TB
    customer_data[("Address, Person")]
    customer_s0["Register Customer"]
    customer_s1["Record Life Events"]
    customer_s2(["Get Person"])
    customer_s3[["LifeEventRecorded"]]
  end
  subgraph paye["PAYE<br/><small>Director of Employer Taxes</small>"]
    direction TB
    paye_data[("Employer, Employment, Pay Period, Tax Code")]
    paye_s0["Process Employer Returns"]
    paye_s1["Issue Tax Code"]
    paye_s2["Calculate PAYE"]
    paye_s3(["Get Employment"])
    paye_s4(["Get Pay Period"])
  end
  subgraph ni["National Insurance<br/><small>Director of National Insurance</small>"]
    direction TB
    ni_data[("Ni Contribution, Ni Record")]
    ni_s0["Allocate NI Number"]
    ni_s1["Calculate NI Contributions"]
    ni_s2["Maintain NI Record"]
    ni_s3(["Get National Insurance Number"])
  end
  subgraph childcare["Childcare<br/><small>Director of Family Support</small>"]
    direction TB
    childcare_data[("Child, Childcare Account, Childcare Payment, Eligibility Check")]
    childcare_s0["Open Childcare Account"]
    childcare_s1["Check Childcare Eligibility"]
    childcare_s2["Calculate Childcare Top-up"]
  end
  childcare -- uses --> customer_s2
  ni -- uses --> customer_s2
  paye -- uses --> customer_s2
  ni -. reacts to .-> customer_s3
  childcare -. reacts to .-> customer_s3
  childcare -- uses --> paye_s3
  ni -- uses --> paye_s3
  childcare -- uses --> paye_s4
  ni -- uses --> paye_s4
  customer -- uses --> ni_s3
  customer_data -. "NI_NUMBER moves" .-> ni
```

## Conformance · Evidence grades

How the evidence for every element is graded.

```mermaid
pie showData title Evidence grades
  "B corroborated" : 47
  "C single source" : 141
  "D assumed" : 8
  "X contradicted" : 3
```

## Conformance · Phase gates

Automated exit-gate result per phase, with how much in-scope evidence is still below grade B.

```mermaid
flowchart LR
  P1["Phase 1<br/>Enterprise scope and architecture discovery<br/><b>PROVISIONAL</b><br/><small>3 of 14 below B</small>"]
  P2["Phase 2<br/>Business concepts and domain modelling<br/><b>PROVISIONAL</b><br/><small>52 of 54 below B</small>"]
  P1 --> P2
  P3["Phase 3<br/>Entity and relationship modelling<br/><b>PROVISIONAL</b><br/><small>77 of 95 below B</small>"]
  P2 --> P3

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class P1 gC
  class P2 gC
  class P3 gC
```

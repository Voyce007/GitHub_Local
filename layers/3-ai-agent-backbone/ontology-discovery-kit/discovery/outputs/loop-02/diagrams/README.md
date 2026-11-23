# Diagrams — loop-02

Generated from the graded model by `ontokit`, one set per agent. Node colours show evidence grade: A confirmed · B corroborated · C single source (dashed) · D assumed · X contradicted.

## Business Analyst · Concept map

Business terms by domain. Rounded boxes are concepts; dotted links are synonyms; arrows point to the entity that holds each concept. "(undefined)" marks a term used without a definition.

```mermaid
flowchart LR
    CON_01(["Customer"])
    CON_02(["Party"])
    CON_03(["Customer Number"])
    CON_04(["Product"])
    CON_05(["Order"])
    CON_06(["Invoice"])
    CON_07(["Legal Entity"])
    CON_08(["Cost Centre"])
    CON_09(["Risk"])
    CON_10(["Control"])
    CON_11(["Tax Code"])
  syn_CON_01_Client["Client"] -. synonym .- CON_01
  syn_CON_01_Account["Account"] -. synonym .- CON_01
  CON_01 --> ENT_01[("Customer")]
  syn_CON_03_Customer_ID["Customer ID"] -. synonym .- CON_03
  syn_CON_03_Debtor_Number["Debtor Number"] -. synonym .- CON_03
  CON_06 --> ENT_08[("Invoice")]
  CON_07 --> ENT_05[("Legal Entity")]
  CON_08 --> ENT_06[("Cost Centre")]
  CON_09 --> ENT_03[("Risk")]
  CON_10 --> ENT_04[("Control")]

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class ENT_01 gA
  class CON_01,CON_02,CON_03,CON_04,CON_05,CON_06,CON_07,CON_08,CON_09,CON_10,CON_11,ENT_08,ENT_05,ENT_06,ENT_03,ENT_04 gC
```

## Enterprise Architect · System context

Each system with its candidate role and known aliases, and the data flows between them, labelled with interface ids.

```mermaid
flowchart LR
  SYS_01["<b>CustHub</b><br/>system of record (candidate): Customer<br/><i>aka Customer Hub, CRM, CH</i>"]
  SYS_02["<b>LedgerOne</b><br/>system of record (candidate): Invoice<br/><i>aka ERP, GL, LO</i>"]
  SYS_03["<b>OrderFlow</b><br/>processing: customer orders<br/><i>aka OMS, Order Management System, OF</i>"]
  SYS_04["<b>Web Shop</b><br/>channel<br/><i>aka WS</i>"]
  SYS_05["<b>Partner Portal</b><br/>channel<br/><i>aka PP</i>"]
  SYS_06["<b>RiskReg</b><br/>system of record (candidate): Risk<br/><i>aka GRC platform, RR</i>"]
  SYS_08["<b>TaxEngine</b><br/>calculation: sales tax for every invoice line<br/><i>aka tax-engine</i>"]
  SYS_07["<b>DataMart</b><br/>reporting / analytics (candidate)<br/><i>aka MI warehouse, DM</i>"]
  SYS_04 -->|"ORD-01 order request"| SYS_03
  SYS_05 -->|"registration"| SYS_01
  SYS_01 -->|"CUST-FIN-01"| SYS_02
  SYS_03 -->|"OrderFulfilled"| SYS_02
  SYS_02 -->|"MI-01 nightly"| SYS_07
  SYS_01 -->|"MI-02 nightly"| SYS_07
  SYS_06 -->|"RISK-01 weekly"| SYS_07
  SYS_04 -->|"runtime dependency (config)"| SYS_01
  SYS_04 -->|"runtime dependency (config)"| SYS_02
  SYS_04 -->|"runtime dependency (config)"| SYS_08

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class SYS_01 gA
  class SYS_02,SYS_03,SYS_04,SYS_05,SYS_06,SYS_08,SYS_07 gB
```

## Data Architect · Entity-relationship diagram

Entities with up to 8 attributes each (PK marks a key), and relationships with cardinality. Labels show how each link is made and its grade.

```mermaid
erDiagram
  Customer {
    char customerNumber PK "grade A"
    char customerType "grade A"
    varchar fullName "grade A"
    date dateOfBirth "grade A"
    varchar emailAddress "grade A"
    char creditStatus "grade A"
    timestamp createdTimestamp "grade A"
    timestamp updatedTimestamp "grade A"
  }
  CustomerAddress {
    char customerNumber "grade A"
    char addressType "grade A"
    varchar line1 "grade A"
    varchar postcode "grade A"
    varchar line2 "grade A"
    char countryCode "grade A"
  }
  Risk {
    varchar riskId PK "grade C"
    varchar title "grade C"
    char rating "grade C"
    varchar costCentreCode "grade C"
    char legalEntityCode "grade C"
    date reviewDate "grade C"
  }
  Control {
    varchar controlId PK "grade C"
    varchar riskId "grade C"
    char controlType "grade C"
    date lastTested "grade C"
  }
  LegalEntity {
    char legalEntityCode PK "grade C"
    varchar registeredName "grade C"
    char countryCode "grade C"
    char functionalCurrency "grade C"
  }
  CostCentre {
    varchar costCentreCode PK "grade C"
    varchar name "grade C"
    char legalEntityCode "grade C"
  }
  Account {
    varchar accountCode PK "grade C"
    varchar accountName "grade C"
    varchar accountType "grade C"
  }
  Invoice {
    varchar invoiceNumber PK "grade C"
    char customerNumber "grade C"
    char legalEntityCode "grade C"
    date invoiceDate "grade C"
    numeric totalAmount "grade C"
    char currency "grade C"
  }
  CustomerEntity {
    char customerNumber "grade C"
    char legalEntityCode "grade C"
  }
  Address {
  }
  OrderRequest {
    string orderId PK "grade C"
    string customerNumber "grade C"
    string currency "grade C"
    bigdecimal totalAmount "grade C"
    orderstatus status "grade C"
  }
  OrderLine {
  }
  CustomerAddress }o--|| Customer : "customerNumber (A)"
  Control }o--|| Risk : "riskId (C)"
  CostCentre }o--|| LegalEntity : "legalEntityCode (C)"
  Invoice }o--|| LegalEntity : "legalEntityCode (C)"
  CustomerEntity }o--|| LegalEntity : "legalEntityCode (C)"
  Customer ||--o{ Address : "addresses (C)"
  OrderRequest ||--o{ OrderLine : "lines (C)"
  Risk }o--|| CostCentre : "costCentreCode (C)"
  Risk }o--|| LegalEntity : "legalEntityCode (C)"
  Invoice }o--|| Customer : "customerNumber (C)"
  CustomerEntity }o--|| Customer : "customerNumber (C)"
  OrderRequest }o--|| Customer : "customerNumber (C)"
  Customer }o--o{ LegalEntity : "CustomerEntity (C)"
```

## Ontology Steward · Alias merges

System names merged only where a source states they are the same. A diamond marks a system nobody explains.

```mermaid
flowchart LR
  SYS_01(["<b>CustHub</b>"])
  SYS_01_a0["Customer Hub"] -- same system --> SYS_01
  SYS_01_a1["CRM"] -- same system --> SYS_01
  SYS_01_a2["CH"] -- same system --> SYS_01
  SYS_02(["<b>LedgerOne</b>"])
  SYS_02_a0["ERP"] -- same system --> SYS_02
  SYS_02_a1["GL"] -- same system --> SYS_02
  SYS_02_a2["LO"] -- same system --> SYS_02
  SYS_03(["<b>OrderFlow</b>"])
  SYS_03_a0["OMS"] -- same system --> SYS_03
  SYS_03_a1["Order Management System"] -- same system --> SYS_03
  SYS_03_a2["OF"] -- same system --> SYS_03
  SYS_04(["<b>Web Shop</b>"])
  SYS_04_a0["WS"] -- same system --> SYS_04
  SYS_05(["<b>Partner Portal</b>"])
  SYS_05_a0["PP"] -- same system --> SYS_05
  SYS_06(["<b>RiskReg</b>"])
  SYS_06_a0["GRC platform"] -- same system --> SYS_06
  SYS_06_a1["RR"] -- same system --> SYS_06
  SYS_08(["<b>TaxEngine</b>"])
  SYS_08_a0["tax-engine"] -- same system --> SYS_08
  SYS_07(["<b>DataMart</b>"])
  SYS_07_a0["MI warehouse"] -- same system --> SYS_07
  SYS_07_a1["DM"] -- same system --> SYS_07

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class SYS_01 gA
  class SYS_02,SYS_03,SYS_04,SYS_05,SYS_06,SYS_08,SYS_07 gB
```

## Conformance · Evidence grades

How the evidence for every element is graded.

```mermaid
pie showData title Evidence grades
  "A confirmed" : 19
  "B corroborated" : 26
  "C single source" : 88
  "D assumed" : 5
```

## Conformance · Phase gates

Automated exit-gate result per phase, with how much in-scope evidence is still below grade B.

```mermaid
flowchart LR
  P1["Phase 1<br/>Enterprise scope and architecture discovery<br/><b>PROVISIONAL</b><br/><small>4 of 18 below B</small>"]
  P2["Phase 2<br/>Business concepts and domain modelling<br/><b>PROVISIONAL</b><br/><small>23 of 28 below B</small>"]
  P1 --> P2
  P3["Phase 3<br/>Entity and relationship modelling<br/><b>PROVISIONAL</b><br/><small>65 of 85 below B</small>"]
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

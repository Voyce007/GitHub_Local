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
    CON_06(["Service Contract"])
    CON_07(["Invoice"])
    CON_08(["Credit Limit"])
    CON_09(["Exposure"])
    CON_10(["Legal Entity"])
    CON_11(["Cost Centre"])
    CON_12(["Risk"])
    CON_13(["Control"])
  syn_CON_01_Client["Client"] -. synonym .- CON_01
  syn_CON_01_Debtor["Debtor"] -. synonym .- CON_01
  CON_01 --> ENT_01[("Customer")]
  CON_01 -- same concept --> ENT_03[("Client")]
  syn_CON_03_Customer_ID["Customer ID"] -. synonym .- CON_03
  syn_CON_03_Debtor_Number["Debtor Number"] -. synonym .- CON_03
  syn_CON_05_OrderRequest["OrderRequest"] -. synonym .- CON_05
  CON_05 -- same concept --> ENT_13[("Order Request")]
  CON_06 --> ENT_04[("Service Contract")]
  CON_07 --> ENT_10[("Invoice")]
  CON_10 --> ENT_07[("Legal Entity")]
  CON_11 --> ENT_08[("Cost Centre")]
  CON_12 --> ENT_05[("Risk")]
  CON_13 --> ENT_06[("Control")]

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class ENT_01 gA
  class CON_01,CON_05 gB
  class CON_02,CON_03,CON_04,CON_06,CON_07,CON_08,CON_09,CON_10,CON_11,CON_12,CON_13,ENT_03,ENT_13,ENT_04,ENT_10,ENT_07,ENT_08,ENT_05,ENT_06 gC
```

## Enterprise Architect · System context

Each system with its candidate role and known aliases, and the data flows between them, labelled with interface ids.

```mermaid
flowchart LR
  SYS_01["<b>TradeDesk</b><br/>system of record (candidate): Customer<br/><i>aka Industrial CRM, TD</i>"]
  SYS_02["<b>ServiceLink</b><br/>system of record (candidate): Client<br/><i>aka contracts system, SL</i>"]
  SYS_03["<b>ShopFront</b><br/>processing: online orders for Meridale Direct<br/><i>aka web store, online order platform, SF</i>"]
  SYS_04["<b>FinCore</b><br/>system of record (candidate): Invoice<br/><i>aka ERP, GL, FC</i>"]
  SYS_05["<b>Sales Desk</b><br/>channel"]
  SYS_06["<b>RiskVault</b><br/>system of record (candidate): Risk<br/><i>aka GRC platform, RV</i>"]
  SYS_08["<b>CreditScore</b><br/>calculation: an external credit score for every new customer<br/><i>aka credit-score-svc</i>"]
  SYS_07["<b>InsightHub</b><br/>reporting / analytics (candidate)<br/><i>aka MI warehouse, IH</i>"]
  SYS_03 -->|"ORD-FIN-02 web orders"| SYS_04
  SYS_01 -->|"CUST-FIN-01"| SYS_04
  SYS_02 -->|"CLI-FIN-03 daily file"| SYS_04
  SYS_04 -->|"MI-01 nightly"| SYS_07
  SYS_01 -->|"MI-02 nightly"| SYS_07
  SYS_06 -->|"RISK-01 weekly"| SYS_07
  SYS_03 -->|"runtime dependency (config)"| SYS_01
  SYS_03 -->|"runtime dependency (config)"| SYS_08

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class SYS_01 gA
  class SYS_02,SYS_03,SYS_04,SYS_06,SYS_08,SYS_07 gB
  class SYS_05 gC
```

## Data Architect · Entity-relationship diagram

Entities with up to 8 attributes each (PK marks a key), and relationships with cardinality. Labels show how each link is made and its grade.

```mermaid
erDiagram
  Customer {
    char customerNumber PK "grade A"
    char customerType "grade A"
    varchar fullName "grade A"
    varchar regNumber "grade A"
    char creditStatus "grade A"
    numeric creditLimit "grade A"
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
  Client {
    varchar clientRef PK "grade C"
    char customerNumber "grade C"
    varchar clientName "grade C"
    numeric creditLimit "grade C"
  }
  ServiceContract {
    varchar contractId PK "grade C"
    varchar clientRef "grade C"
    date startDate "grade C"
    date endDate "grade C"
    numeric annualValue "grade C"
  }
  Risk {
    varchar riskId PK "grade C"
    varchar title "grade C"
    char rating "grade C"
    varchar costCentreCode "grade C"
    char customerNumber "grade C"
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
    date dueDate "grade C"
    numeric totalAmount "grade C"
    numeric amountOutstanding "grade C"
    char currency "grade C"
  }
  CustomerEntity {
    char customerNumber "grade C"
    char legalEntityCode "grade C"
    numeric creditLimit "grade C"
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
  ServiceContract }o--|| Client : "clientRef (C)"
  Control }o--|| Risk : "riskId (C)"
  CostCentre }o--|| LegalEntity : "legalEntityCode (C)"
  Invoice }o--|| LegalEntity : "legalEntityCode (C)"
  CustomerEntity }o--|| LegalEntity : "legalEntityCode (C)"
  Customer ||--o{ Address : "addresses (C)"
  OrderRequest ||--o{ OrderLine : "lines (C)"
  Client }o--|| Customer : "customerNumber (C)"
  Risk }o--|| CostCentre : "costCentreCode (C)"
  Risk }o--|| Customer : "customerNumber (C)"
  Invoice }o--|| Customer : "customerNumber (C)"
  CustomerEntity }o--|| Customer : "customerNumber (C)"
  OrderRequest }o--|| Customer : "customerNumber (C)"
  Customer }o--o{ LegalEntity : "CustomerEntity (C)"
```

## Ontology Steward · Alias merges

System names merged only where a source states they are the same. A diamond marks a system nobody explains.

```mermaid
flowchart LR
  SYS_01(["<b>TradeDesk</b>"])
  SYS_01_a0["Industrial CRM"] -- same system --> SYS_01
  SYS_01_a1["TD"] -- same system --> SYS_01
  SYS_02(["<b>ServiceLink</b>"])
  SYS_02_a0["contracts system"] -- same system --> SYS_02
  SYS_02_a1["SL"] -- same system --> SYS_02
  SYS_03(["<b>ShopFront</b>"])
  SYS_03_a0["web store"] -- same system --> SYS_03
  SYS_03_a1["online order platform"] -- same system --> SYS_03
  SYS_03_a2["SF"] -- same system --> SYS_03
  SYS_04(["<b>FinCore</b>"])
  SYS_04_a0["ERP"] -- same system --> SYS_04
  SYS_04_a1["GL"] -- same system --> SYS_04
  SYS_04_a2["FC"] -- same system --> SYS_04
  SYS_05(["<b>Sales Desk</b>"])
  SYS_06(["<b>RiskVault</b>"])
  SYS_06_a0["GRC platform"] -- same system --> SYS_06
  SYS_06_a1["RV"] -- same system --> SYS_06
  SYS_08(["<b>CreditScore</b>"])
  SYS_08_a0["credit-score-svc"] -- same system --> SYS_08
  SYS_07(["<b>InsightHub</b>"])
  SYS_07_a0["MI warehouse"] -- same system --> SYS_07
  SYS_07_a1["IH"] -- same system --> SYS_07

  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px
  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px
  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3
  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3
  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px
  class SYS_01 gA
  class SYS_02,SYS_03,SYS_04,SYS_06,SYS_08,SYS_07 gB
  class SYS_05 gC
```

## Conformance · Evidence grades

How the evidence for every element is graded.

```mermaid
pie showData title Evidence grades
  "A confirmed" : 19
  "B corroborated" : 26
  "C single source" : 110
  "D assumed" : 5
```

## Conformance · Phase gates

Automated exit-gate result per phase, with how much in-scope evidence is still below grade B.

```mermaid
flowchart LR
  P1["Phase 1<br/>Enterprise scope and architecture discovery<br/><b>PROVISIONAL</b><br/><small>3 of 16 below B</small>"]
  P2["Phase 2<br/>Business concepts and domain modelling<br/><b>PROVISIONAL</b><br/><small>26 of 33 below B</small>"]
  P1 --> P2
  P3["Phase 3<br/>Entity and relationship modelling<br/><b>PROVISIONAL</b><br/><small>84 of 103 below B</small>"]
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

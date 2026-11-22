# Unknowns register — loop-02

Questions for subject-matter experts and requests for evidence. Answering these is what moves grades up.

| ID | Priority | Type | Question | Why | Owner | Affects |
|---|---|---|---|---|---|---|
| U-01 | high | sme question | Is 'Account' a synonym of Customer, or a different concept (a role) that shares the name? | Glossary lists 'Account' as a synonym of Customer, but LedgerOne has an entity 'Account' with its own structure. | Business Domain Owner | CON-01 Customer, ENT-07 Account |
| U-02 | high | evidence request | Request a schema export and a masked data sample from LedgerOne. | Would let 27 entity/attribute/identifier elements move to grade A. | Engineering Lead (with the system owner) | SYS-02 LedgerOne |
| U-03 | high | evidence request | Request a schema export and a masked data sample from OrderFlow. | Would let 8 entity/attribute/identifier elements move to grade A. | Engineering Lead (with the system owner) | SYS-03 OrderFlow |
| U-04 | high | evidence request | Request a schema export and a masked data sample from RiskReg. | Would let 14 entity/attribute/identifier elements move to grade A. | Engineering Lead (with the system owner) | SYS-06 RiskReg |
| U-05 | medium | sme question | Are these the same thing? 'Address' may be the unqualified form of 'CustomerAddress'. | Merging them changes the entity catalogue and the stand-in schema. | Domain Owner and Data Architecture Authority | ENT-02 CustomerAddress, ENT-10 Address |
| U-06 | medium | sme question | Are these the same thing? 'OrderRequest' looks like 'Order' with a role suffix. | Merging them changes the entity catalogue and the stand-in schema. | Domain Owner and Data Architecture Authority | ENT-11 OrderRequest, CON-05 Order |
| U-07 | medium | evidence request | Request a schema export and a masked data sample from CustHub. | Would let 1 entity/attribute/identifier elements move to grade A. | Engineering Lead (with the system owner) | SYS-01 CustHub |
| U-08 | medium | evidence request | What does 'OrderLine' contain, and which system holds it? | 'OrderLine' is referenced by OrderRequest.lines, but its structure is not in the evidence. | Data Architecture Authority | ENT-12 OrderLine |
| U-09 | medium | sme question | Where is 'Party' held, and which system is the source of truth? | No entity found for 'Party'. | Data Architecture Authority | CON-02 Party |
| U-10 | medium | sme question | Where is 'Product' held, and which system is the source of truth? | No entity found for 'Product'. | Data Architecture Authority | CON-04 Product |
| U-11 | medium | sme question | Where is 'Tax Code' held, and which system is the source of truth? | No entity found for 'Tax Code'. Possible home: TaxEngine. | Data Architecture Authority | CON-11 Tax Code |
| U-12 | low | sme question | The reference model expects 'Channel'. Does the organisation have it, and where is it recorded? | Added at grade D from the playbook's reference ontology; no evidence yet. | Domain Owner and Data Architecture Authority | ENT-15 Channel |
| U-13 | low | sme question | The reference model expects 'Customer places Order'. Is this relationship real here, and which system records it? | Added at grade D from the playbook's reference ontology; no evidence yet. | Domain Owner and Data Architecture Authority | REL-14 Customer places Order |
| U-14 | low | sme question | The reference model expects 'Order contains Product'. Is this relationship real here, and which system records it? | Added at grade D from the playbook's reference ontology; no evidence yet. | Domain Owner and Data Architecture Authority | REL-15 Order contains Product |
| U-15 | low | sme question | The reference model expects 'Organisation'. Does the organisation have it, and where is it recorded? | Added at grade D from the playbook's reference ontology; no evidence yet. | Domain Owner and Data Architecture Authority | ENT-14 Organisation |
| U-16 | low | sme question | The reference model expects 'Person'. Does the organisation have it, and where is it recorded? | Added at grade D from the playbook's reference ontology; no evidence yet. | Domain Owner and Data Architecture Authority | ENT-13 Person |

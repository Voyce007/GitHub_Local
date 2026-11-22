# Unknowns register — loop-02

Questions for subject-matter experts and requests for evidence. Answering these is what moves grades up.

| ID | Priority | Type | Question | Why | Owner | Affects |
|---|---|---|---|---|---|---|
| U-01 | high | evidence request | Request a schema export and a masked data sample from FinCore. | Would let 30 entity/attribute/identifier elements move to grade A. | Engineering Lead (with the system owner) | SYS-04 FinCore |
| U-02 | high | evidence request | Request a schema export and a masked data sample from RiskVault. | Would let 14 entity/attribute/identifier elements move to grade A. | Engineering Lead (with the system owner) | SYS-06 RiskVault |
| U-03 | high | evidence request | Request a schema export and a masked data sample from ServiceLink. | Would let 13 entity/attribute/identifier elements move to grade A. | Engineering Lead (with the system owner) | SYS-02 ServiceLink |
| U-04 | high | evidence request | Request a schema export and a masked data sample from ShopFront. | Would let 8 entity/attribute/identifier elements move to grade A. | Engineering Lead (with the system owner) | SYS-03 ShopFront |
| U-05 | medium | sme question | Are these the same thing? 'Address' may be the unqualified form of 'CustomerAddress'. | Merging them changes the entity catalogue and the stand-in schema. | Domain Owner and Data Architecture Authority | ENT-02 CustomerAddress, ENT-12 Address |
| U-06 | medium | evidence request | Request a schema export and a masked data sample from TradeDesk. | Would let 1 entity/attribute/identifier elements move to grade A. | Engineering Lead (with the system owner) | SYS-01 TradeDesk |
| U-07 | medium | evidence request | What does 'OrderLine' contain, and which system holds it? | 'OrderLine' is referenced by OrderRequest.lines, but its structure is not in the evidence. | Data Architecture Authority | ENT-14 OrderLine |
| U-08 | medium | sme question | Where is 'Credit Limit' held, and which system is the source of truth? | No entity found for 'Credit Limit'. Possible home: CreditScore. | Data Architecture Authority | CON-08 Credit Limit |
| U-09 | medium | sme question | Where is 'Exposure' held, and which system is the source of truth? | No entity found for 'Exposure'. | Data Architecture Authority | CON-09 Exposure |
| U-10 | medium | sme question | Where is 'Party' held, and which system is the source of truth? | No entity found for 'Party'. | Data Architecture Authority | CON-02 Party |
| U-11 | medium | sme question | Where is 'Product' held, and which system is the source of truth? | No entity found for 'Product'. | Data Architecture Authority | CON-04 Product |
| U-12 | low | sme question | The reference model expects 'Channel'. Does the organisation have it, and where is it recorded? | Added at grade D from the playbook's reference ontology; no evidence yet. | Domain Owner and Data Architecture Authority | ENT-17 Channel |
| U-13 | low | sme question | The reference model expects 'Customer places Order'. Is this relationship real here, and which system records it? | Added at grade D from the playbook's reference ontology; no evidence yet. | Domain Owner and Data Architecture Authority | REL-16 Customer places Order |
| U-14 | low | sme question | The reference model expects 'Order contains Product'. Is this relationship real here, and which system records it? | Added at grade D from the playbook's reference ontology; no evidence yet. | Domain Owner and Data Architecture Authority | REL-17 Order contains Product |
| U-15 | low | sme question | The reference model expects 'Organisation'. Does the organisation have it, and where is it recorded? | Added at grade D from the playbook's reference ontology; no evidence yet. | Domain Owner and Data Architecture Authority | ENT-16 Organisation |
| U-16 | low | sme question | The reference model expects 'Person'. Does the organisation have it, and where is it recorded? | Added at grade D from the playbook's reference ontology; no evidence yet. | Domain Owner and Data Architecture Authority | ENT-15 Person |

# Ontology Discovery Kit

A set of collaborating agents that reverse-engineer an **as-is enterprise
ontology** from documentation extracts and example code, and keep improving
it loop by loop as answers and real system artefacts arrive. It follows the
*Enterprise Ontology Design & Delivery Playbook* (four personas, ten gated
phases, decision rights, definition of done) in brownfield mode, for when the
source systems are not yet known or accessible.

It is **industry-agnostic**. The reference core is what almost every company
has: Party, Customer, Product, Order and Invoice, plus the group functions
Finance (Legal Entity, Cost Centre, General Ledger) and Risk (Risk, Control).
To extend it, add other functions such as HR, Procurement or Treasury in
`config/reference_ontology.yaml`.

- **Storyboard, explainer, flow diagram and simulation:** open `docs/storyboard.html` in a browser.
- **Instructions for Claude Code:** `CLAUDE.md`
- **The loop procedure:** `.claude/skills/ontology-discovery-loop/SKILL.md`

## Quick start

```bash
pip install -r requirements.txt
python -m unittest discover -s tests            # loop-1 findings, loop-2 iteration, guardrails
python -m ontokit simulate --loop loop-01        # first pass: documents + example code
python -m ontokit simulate --loop loop-02        # second pass: SME answers + a schema export
python tools/build_storyboard.py                 # rebuild docs/storyboard.html from both runs
```

## The loop

```
Evidence batch ─► A Intake ─► B Agents propose ─► C Validate ─► D Steward ─► E Grade
     ▲                              ▲ ① rejected ──┘                            │
     │                                                                          ▼
 ③ loop n+1                                                            F Reference check
     │                                                                          │
SMEs & owners ◄── questions + evidence requests ── G Unknowns ◄─────────────────┘
     ▲                                                 ▲  │
     │                                    ② deferred ──┘  ▼
  K Publish ◄── J Human gate ◄── I Change register ◄── H Gate checks
```

There are three loops:
- **① Inner loop:** the validator sends proposals it can't verify back to the agent that wrote them, for at most two retries.
- **② Inner loop:** decisions the approvers defer stay open as unknowns.
- **③ Outer loop:** answers and new code context become the next evidence batch, and the whole graph runs again.

| Stage | Actor | What happens |
|---|---|---|
| A. Intake | `ontokit ingest` | Builds a citable source index (including carried-forward files) and flags stale files |
| B. Propose | BA, EA, DA, Engineering agents | One proposal per source, with verbatim quotes |
| C. Validate | `ontokit validate` | Rejects invented quotes, out-of-scope kinds (RACI), self-confirmation and missing evidence |
| D. Reconcile | Steward | Resolves aliases, merges proposals, keeps contradictions or resolves them by authority, links concepts to entities, flags homonyms and synonyms |
| E. Grade | Conformance | A/B/C/D/X by rule |
| F. Reference | Steward | Gaps against the reference core become grade-D assumptions |
| G. Unknowns | Steward | Questions and evidence requests, each with a named owner |
| H. Gates | Conformance | Phase 1–3 exit criteria: pass, provisional or fail |
| I. Change register | Steward | From loop 2: what moved since the previous loop (phase 10) |
| J. Human gate | Named approvers | Decisions in `approvals.yaml`. Agents never fill these in. Unchanged decisions carry forward. |
| K. Publish | `ontokit publish` | Ontology, inventory, glossary, unknowns, gate report, stand-in SQL |

## The sample loops (fictional "Example Group")

**Loop 1** (`discovery/inputs/loop-01/`) has 12 files from Sales, Finance, Risk and IT. The loop should find:
- **System aliases:** CustHub = Customer Hub = CH = "the CRM", and LedgerOne = ERP = GL
- **Contradiction 1:** customer types differ between documents and code
- **Contradiction 2:** order statuses in a stale 2019 document differ from 2024 code
- **Contradiction 3:** Sales and Finance documents name different issuers for the Customer Number
- **An undocumented system:** `tax-engine`, which appears only in config
- **A homonym:** the glossary says "Account" means Customer, but Finance's Account table is the general ledger
- **A link table:** Customer ↔ Legal Entity
- **Reference gaps:** Person, Organisation and Channel

**Loop 2** (`discovery/inputs/loop-02/`) carries loop 1 forward and adds two files:
- SME answers from a working session
- a structure-only CustHub schema export.

**Result:** all three contradictions are resolved, with the superseded versions kept for audit. 19 elements are graded up, CustHub's data reaches grade A, 4 unknowns close, and `change-register.md` lists every change.

## Outputs per loop (`discovery/outputs/<loop>/`)

| File | What it is |
|---|---|
| `summary.md` | One-page result |
| `as-is-ontology.yaml` | LinkML-flavoured model, annotated with grade, status, evidence ids and open unknowns |
| `system-inventory.md` | Candidate systems, aliases, roles, flows and interfaces |
| `glossary.md` | Concepts, synonyms, classifications and rules |
| `unknowns-register.md` | SME questions and evidence requests |
| `jira-issues.json` | The unknowns, ready for the MCP `create_jira_issue` tool |
| `unknowns.json` | The unknowns as data |
| `gate-report.md` | Phase gates and human-gate decisions |
| `change-register.md` | From loop 2: what changed since the previous loop |
| `changes.json` | The change register as data |
| `standins/*.sql` | Stand-in schemas for the proof of concept, with a grade in each column comment |
| `evidence-register.json` | Every cited line, and what it supports |
| `elements.json` | Every element, with its evidence |
| `trace.json` | The run's event log |

## Requirements and licence notes
- Python 3.10+ and PyYAML, both open source.
- Optional: `linkml` to validate the ontology, and `sqlglot` for parsing large SQL extracts in live runs.
- No hosted services. Live agent runs use Claude Code itself. If inputs must stay local, run first-pass extraction on local models such as Ollama.

## Executive scenario: Meridale Group (fictional)

`scenarios/meridale/` is a worked use case for a COO or CIO audience. A
fictional industrial group asks: "What is our total exposure to each customer
across the group, today?" The folder holds the scenario framing
(`scenario.yaml`), two loops of inputs, and the outputs of a full simulated
play-through. `docs/meridale-storyboard.html` is the animated 17-scene
storyboard built from those outputs. Rebuild it with:

```bash
python -m ontokit simulate --root scenarios/meridale --loop loop-01
python -m ontokit simulate --root scenarios/meridale --loop loop-02
python tools/build_exec_storyboard.py
```

## Monolith decomposition scenario: Northmere Revenue Service (fictional)

`scenarios/northmere/` splits a legacy monolith, TAXCORE, into four
business-owned domain ontologies: Customer, PAYE, National Insurance and
Childcare. Each domain is exposed through business services on the access
layer. The split is driven by a `target_domains.yaml` file next to the
scenario's inputs, and the decomposition stage (`ontokit/decompose.py`) runs
whenever that file is present.

**The rule:** the domain whose business capability creates or changes data
owns it. Other domains use the owner's services or react to its events.

**The evidence:** the business capability map, the batch-job catalogue and
example stored procedures, which show who really writes each table and column.

**The outputs** go to `outputs/<loop>/decomposition/`:
- a LinkML ontology per domain
- an OpenAPI service contract per domain
- a monolith-to-domain source-to-target mapping
- split candidates and cross-domain events
- a report with a target-state diagram.

```bash
python -m ontokit simulate --root scenarios/northmere --loop loop-01
```

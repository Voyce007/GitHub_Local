# Ontology Discovery Kit

A set of collaborating agents that reverse-engineer an **as-is enterprise
ontology** from documentation extracts and example code. It follows the
*Enterprise Ontology Design & Delivery Playbook* (four personas, ten gated
phases, decision rights, definition of done) in brownfield mode, for when
the source systems are not yet known or accessible.

- **Storyboard, explainer and simulation:** open `docs/storyboard.html` in a browser.
- **Instructions for Claude Code:** `CLAUDE.md`
- **The loop procedure:** `.claude/skills/ontology-discovery-loop/SKILL.md`

## Quick start

```bash
pip install -r requirements.txt
python -m unittest discover -s tests       # 3 tests: planted findings + guardrails
python -m ontokit simulate                 # full loop on the fictional sample batch
python tools/build_storyboard.py           # rebuild docs/storyboard.html from that run
```

The outputs go to `discovery/outputs/loop-01/`:

| File | What it is |
|---|---|
| `summary.md` | One-page result of the loop |
| `as-is-ontology.yaml` | LinkML-flavoured model. Every class, attribute and enum is annotated with grade, status, evidence ids and open unknowns. |
| `system-inventory.md` | Candidate systems, aliases, roles, flows and interfaces |
| `glossary.md` | Concepts, synonyms, classifications and rules |
| `unknowns-register.md` | SME questions and evidence requests |
| `jira-issues.json` | The unknowns, ready for the MCP `create_jira_issue` tool |
| `gate-report.md` | Automated phase gates plus human decisions |
| `standins/*.sql` | Stand-in schemas for the proof of concept, with a grade in each column comment |
| `evidence-register.json` | Every cited source line, with the elements it supports |
| `elements.json` | Every element, with its evidence |
| `trace.json` | The ordered event log of the run |

## How a loop works

| Stage | Actor | What happens |
|---|---|---|
| A. Intake | `ontokit ingest` | Loads the manifest's files into a citable source index and flags stale files |
| B. Propose | BA, EA, DA, Engineering agents | Each writes `proposals/<agent>.json`: one proposal per source, verbatim quotes |
| C. Validate | `ontokit validate` | Rejects invented quotes, out-of-scope kinds (RACI), self-confirmation and missing evidence |
| D. Reconcile | Steward (`ontokit reconcile`) | Resolves aliases, merges duplicates, keeps contradictions, links concepts to entities, flags synonyms and homonyms |
| E. Grade | Conformance | Grades each element A, B, C, D or X by rule (`config/evidence_grades.yaml`) |
| F. Reference | Steward | Compares against the playbook §6 reference model. Gaps are added as grade-D assumptions. |
| G. Unknowns | Steward | Writes questions and evidence requests, each with an owner from decision rights |
| H. Gates | Conformance | Automated exit criteria for phases 1–3: pass, provisional or fail |
| I. Human gate | Named approvers | Decisions per element in `approvals.yaml`. Agents never fill these in. |
| J. Publish | `ontokit publish` | Writes the deliverables and stand-ins |

In **simulation** mode, rule-based stand-ins replace the four persona agents
and the approvals are marked "simulated". In **live** mode the Claude Code
subagents in `.claude/agents/` write the proposal files. Every later stage is
the same code in both modes.

## The sample batch

`discovery/inputs/loop-01/` is a fictional bank ("Northbridge Bank"). It
contains ten files with planted, realistic problems that the loop should find:
- **System aliases:** CustHub = Customer Hub = CH = "the CRM"
- **Contradiction 1:** a customer-type list that differs between documents and code
- **Contradiction 2:** payment statuses from a stale 2019 document against 2024 code
- **Contradiction 3:** two different issuers for the Customer Number
- **An undocumented system** that appears only in config (`mandate-svc`)
- **A homonym:** the glossary says "Account Holder" means Customer, but the ledger has an AccountHolder link table
- **Reference-model gaps:** Person, Organisation, Product and others

Replace the folder with your own extracts to run it for real.

## Requirements and licence notes
- Python 3.10+ and PyYAML, both open source.
- Optional: `linkml` to validate the ontology output, and `sqlglot` for parsing large SQL extracts in live runs.
- No hosted services. Live agent runs use Claude Code itself. If your inputs must stay local, run first-pass extraction on local models such as Ollama (see the repo's layer 2).

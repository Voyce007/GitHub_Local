# Ontology Discovery Kit — instructions for Claude Code

This folder is a self-contained kit. Copy it to the root of any repository
(or open it as its own project) and Claude Code will load the subagents in
`.claude/agents/` and the `ontology-discovery-loop` skill.

It implements **document-led reverse engineering** for the *Enterprise
Ontology Design & Delivery Playbook*. It is industry-agnostic: the reference
core is Party, Customer, Product, Order and Invoice, plus the group functions
Finance (Legal Entity, Cost Centre) and Risk (Risk, Control). The source systems are not known
up front; the evidence is documentation extracts and example code. Each loop
turns one evidence batch into:
- an evidence-graded as-is ontology
- a candidate system inventory
- an unknowns register
- stand-in schemas for a proof of concept.

Loops iterate. Loop n+1 carries loop n's evidence forward, adds the answers and
new code context, resolves contradictions by authority, and publishes a change
register against loop n.

## Discovery roots and scenarios
Every `ontokit` command takes `--root`. The default root is `discovery/`. The folders under `scenarios/` are self-contained roots:
- `meridale`: customer exposure, run over two loops
- `northmere`: monolith decomposition.

A root with a `target_domains.yaml` also gets the decomposition stage, which splits a monolith into business-owned domains with a business-service catalogue.

## Start here
- To run a loop, follow `.claude/skills/ontology-discovery-loop/SKILL.md`.
- For a demo with no LLM, run `python -m ontokit simulate --loop loop-01`, then `--loop loop-02`.
- Tests: `python -m unittest discover -s tests`. Requires Python 3.10+ and PyYAML (`pip install -r requirements.txt`).

## Non-negotiable rules
1. **Agents recommend; humans approve.** Never write a decision into `approvals.yaml` that the user did not give.
2. **Every claim cites a verbatim quote** from a file listed in the loop's `manifest.yaml`. The validator enforces this. Do not work around it.
3. **Grades are computed, not chosen.** See `config/evidence_grades.yaml`. Documents and example code top out at B, and contradictions are X.
4. **Assumptions stay visible.** Anything taken from the reference ontology is origin `assumed`, grade D.
5. **Write scopes follow the RACI** in `config/decision_rights.yaml`. An agent proposes only its own kinds.

## Layout
| Path | Purpose |
|---|---|
| `config/` | The playbook as data: phases and gates, decision rights, evidence grades, reference ontology |
| `schemas/proposal.schema.json` | The contract every persona agent writes |
| `.claude/agents/` | BA, EA, DA, Engineering, Ontology Steward and Conformance subagents |
| `.claude/skills/ontology-discovery-loop/` | The orchestration procedure |
| `ontokit/` | Deterministic pipeline: ingest, validate, reconcile, grade, reference check, unknowns, gates, approvals, publish (plus rule-based stand-in agents for simulation) |
| `discovery/inputs/<loop>/` | Evidence batches. The fictional samples are `loop-01` (documents and example code) and `loop-02` (SME answers and a schema export, carrying loop-01 forward). |
| `discovery/work/<loop>/` | Intermediate state (proposals, model, approvals) |
| `discovery/outputs/<loop>/` | Deliverables, plus `change-register.md` from loop 2 onwards |

## Changing the playbook
Edit `config/*.yaml`, not the code. New gate criteria need a check function
in `ontokit/gates.py` (`_checks`) with the same `check:` key.

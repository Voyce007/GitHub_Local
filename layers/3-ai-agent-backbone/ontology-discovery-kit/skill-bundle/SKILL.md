---
name: ontology-discovery
description: Build an evidence-graded enterprise ontology from documents and code extracts, and optionally split a legacy monolith into business-owned domains with business services, following the Enterprise Ontology Design and Delivery Playbook. Use when the user uploads documentation, data dictionaries, batch-job lists or code extracts and asks to discover an ontology, map systems, find contradictions, or decompose a monolith into domains. Also use to demo the method on a bundled sample.
---

# Ontology discovery (Claude apps edition)

This skill runs the same method as the Claude Code kit, inside a Claude app with code execution:
- six roles from the playbook: Business Analyst, Enterprise Architect, Data Architect, Engineer, Ontology Steward and Conformance
- a fixed Python pipeline (`kit/ontokit`) that validates, merges, grades, decomposes and publishes.

These apps have no subagents, so **you play each role in turn**, reading its brief in `kit/roles/`. The pipeline checks your work exactly as it checks the Claude Code agents. **Agents recommend; only named people approve.** Never record an approval the user did not give.

## 0. Set up (every conversation)
```bash
cp -r <this skill folder>/kit /tmp/ontokit && cd /tmp/ontokit
python -c "import yaml" 2>/dev/null || pip install --quiet "PyYAML>=6.0"
```
Run every command below from `/tmp/ontokit`.

## 1. Demo first, if the user just wants to see it
```bash
python -m ontokit simulate --root scenarios/northmere --loop loop-01
```
This uses rule-based stand-in agents, and needs no reading by you. Then show these files:
- `scenarios/northmere/outputs/loop-01/summary.md`
- `scenarios/northmere/outputs/loop-01/decomposition/decomposition-report.md`
- the agent diagrams in `scenarios/northmere/outputs/loop-01/diagrams/README.md`. Render the Mermaid blocks inline.

`scenarios/meridale` (customer exposure, loops 1 and 2) is a second sample.

## 2. A real run on the user's files
1. **Make a root:** `mkdir -p work-root/inputs/loop-01` and put the uploaded files under it, in sub-folders such as `docs/`, `spreadsheets/` and `code/`.
2. **Write `work-root/inputs/loop-01/manifest.yaml`.** Use `scenarios/northmere/inputs/loop-01/manifest.yaml` as the pattern. For each file record `path`, `provenance` and `date`, plus `author`, `system_hint` and `table_prefix` where you know them. Provenance is one of: document, wiki, spreadsheet, diagram, example-code, real-code, schema, data-sample, sme-answer.
   - **Ask the user for anything you cannot tell from the file**, especially dates and whether code is real source or an extract.
   - **If personal data is present, stop** and ask whether it may be processed.
3. **Splitting a monolith?** Also write `work-root/target_domains.yaml`, using `scenarios/northmere/target_domains.yaml` as the pattern: the domains, owners, owning teams (as named in the capability map) and keywords. Agree it with the user first.
4. **Ingest:** `python -m ontokit ingest --root work-root --loop loop-01`
5. **Play the four specialist roles one at a time.** For each of `ba`, `ea`, `da` and `eng`:
   - Read `roles/<role>-agent.md` and follow it.
   - Read every file listed in `work-root/work/loop-01/sources.json`. Open each at `work-root/inputs/<location>` and cite it by its key.
   - Write `work-root/work/loop-01/proposals/<role>.json`.
   - **Copy quotes programmatically**: write a small Python script that takes each quote as a whole line from the file. Never type quotes from memory.
6. **Validate:** `python -m ontokit validate --root work-root --loop loop-01`. Fix every rejection in `work-root/work/loop-01/validated.json`, re-running at most twice.
7. **Run the pipeline:** `python -m ontokit run --root work-root --loop loop-01`.
8. **Review as the Steward, then as Conformance.**
   - Read `roles/ontology-steward.md` and `roles/conformance-agent.md`.
   - Write `work-root/work/loop-01/steward-notes.md` and `conformance-briefing.md`.
   - Recommend only; change no element, grade or approval.
9. **Report back to the user:**
   - `outputs/loop-01/summary.md`
   - the high-priority rows of `unknowns-register.md`
   - with a decomposition, `decomposition/decomposition-report.md`
   - the steward's key findings.

   - the **agent diagrams** in `work-root/outputs/loop-01/diagrams/`. Show them inline by rendering the Mermaid blocks from the `README.md` there (one or two per role: concept map, system context, capability map, entity-relationship, calculation flow, aliases, decomposition, grades and gates). Nodes are coloured by evidence grade.

   Offer the outputs as files to download, such as the domain ontologies, service contracts, `source-to-target.csv` and the diagram files.
10. **Human gate.** Decisions live in `work-root/work/loop-01/approvals.yaml`, all `pending`. Ask the user for decisions one approver role at a time, record exactly what they say, then run `python -m ontokit publish --root work-root --loop loop-01`.

## 3. The next loop
Make `inputs/loop-02/manifest.yaml` with `carry_forward: [loop-01]`. Add the owners' answers (provenance `sme-answer`) and any real schemas, code or samples. Then repeat from step 4 with `--loop loop-02`. You get stable ids, contradictions settled by authority, and a `change-register.md`.

Files in this app's sandbox do not persist between conversations, so offer the user a zip of `work-root/` at the end of each session.

## Rules
- Every claim quotes a source line word for word. The validator rejects anything else.
- Grades are computed, never chosen. Only real system artefacts (schema, real-code, data-sample) reach grade A.
- Assumptions from the reference model stay at grade D.
- Never resolve a contradiction yourself. It becomes a question for the named owner.

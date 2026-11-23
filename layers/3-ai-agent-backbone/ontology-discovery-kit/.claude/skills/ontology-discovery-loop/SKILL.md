---
name: ontology-discovery-loop
description: Run one evidence loop of document-led ontology discovery (Enterprise Ontology Playbook, brownfield mode). Use when asked to "run the discovery loop", "process loop-02", "build the as-is ontology from these documents", or to simulate the workflow. Orchestrates the BA, EA, DA and Engineering subagents, the deterministic ontokit pipeline, the Steward and Conformance reviews, and the human approval gate.
---

# Ontology discovery loop

One loop = one evidence batch in `<root>/inputs/<loop>/` with a `manifest.yaml`.

**`<root>` is the discovery root.** It is `discovery/` by default, or a scenario folder such as `scenarios/northmere/`. Pass `--root <root>` to every `python -m ontokit` command, and tell every subagent which root and loop to use.

A root can also hold:
- `target_domains.yaml`: turns on the **decomposition** stage, which splits a monolith into business-owned domains
- `reference_ontology.yaml`: overrides the reference prior
- `scenario.yaml`: key concepts for the gates, and storyboard framing.
Agents **recommend**; named humans **approve**. Nothing in a documents-only loop
reaches grade A.

## 0. Pick the mode
- **Simulation**: `python -m ontokit simulate --loop <loop>`. Uses rule-based stand-in agents and simulated approvals. Use it for demos and to check the pipeline. Stop after this step.
- **Live** (real material): continue with steps 1–8 below.

## 1. Check the batch
- Confirm `<root>/inputs/<loop>/manifest.yaml` lists every file, with `provenance`, `date` and, where known, a `system_hint`.
- Allowed provenance values: document, wiki, spreadsheet, diagram, example-code, real-code, schema, data-sample.
- Diagrams that only exist as images: read them with your own vision and transcribe them to Mermaid (`.mmd`) next to the image. Add both to the manifest, and put `notes: transcribed from <image>` on the `.mmd` entry.
- If files contain personal data, stop and ask the user whether they may be processed here.

Then run `python -m ontokit ingest --loop <loop>`.

## 2. Agents propose (in parallel)
Launch the four persona subagents **in one message** with the Agent tool:
`ea-agent`, `ba-agent`, `da-agent`, `eng-agent`. Give each:
> Root `<root>`, loop `<loop>`. Read `<root>/work/<loop>/sources.json` for the citable files and open each one at `<root>/inputs/<location>`.
> Write `<root>/work/<loop>/proposals/<your key>.json`, following your instructions and `schemas/proposal.schema.json`.

When decomposing a monolith, remind the EA agent to propose every capability with its `owner_team`, and the Engineering agent to propose every batch job and stored procedure as a `calculation` with its `reads`, `writes` and `writes_columns`.

## 3. Validate (the guardrail)
Run `python -m ontokit validate --loop <loop>`.
- Read the `rejected` list in `<root>/work/<loop>/validated.json`.
- Send each agent its own rejections (wrong quote, out-of-scope kind, missing evidence) and ask it to fix its file. Allow at most 2 retries per agent, then carry on.
- Never edit an agent's quotes yourself to make them pass.

## 4. Reconcile, grade, check gates
Run `python -m ontokit run --loop <loop>`. From loop-02 on it also compares against the previous loop. It runs:
- ingest
- validate
- Steward merge
- grading
- reference check
- decomposition (only when `target_domains.yaml` exists)
- unknowns
- gates
- change register (loop 2 onwards)
- a pending approvals file
- publish.

It does not invent human decisions. Decisions already recorded in `approvals.yaml` are kept.

## 5. Steward and Conformance review (in parallel)
Launch `ontology-steward` and `conformance-agent` in one message. They write:
- `<root>/work/<loop>/steward-notes.md`
- `<root>/work/<loop>/conformance-briefing.md`

## 6. Human gate
`<root>/work/<loop>/approvals.yaml` lists every element under its approver role, with decision `pending`.
- Show the user the conformance briefing for one approver role at a time.
- Ask for decisions with AskUserQuestion (approve-provisional / defer / reject / note-assumption), batching by grade. The user may instead edit the YAML directly.
- Record each answer in `approvals.yaml`, with `by:` set to the person's role or name as the user gives it, and a `reason:` for rejections.
- **Never fill in decisions the user did not give.** If they want to skip, leave items `pending`.

## 7. Publish
Run `python -m ontokit publish --root <root> --loop <loop>`. It also draws **diagrams for each agent** in `<root>/outputs/<loop>/diagrams/`, as Mermaid files plus a `README.md` that embeds them all:

| Agent | Diagrams |
|---|---|
| Business Analyst | `ba-concept-map` |
| Enterprise Architect | `ea-system-context`, `ea-capability-map` |
| Data Architect | `da-entity-relationship` |
| Engineer | `eng-calculation-flow` |
| Ontology Steward | `steward-aliases`, `steward-decomposition` (when decomposing) |
| Conformance | `conformance-grades`, `conformance-gates` |

Nodes are coloured by evidence grade. To regenerate the diagrams alone, run `python -m ontokit diagrams --root <root> --loop <loop>`. Show the user the diagrams `README.md` along with the summary. In a Claude app that can publish pages, embed the Mermaid blocks in an artifact. With a decomposition, it also writes `<root>/outputs/<loop>/decomposition/`:
- one LinkML ontology per domain
- one OpenAPI service contract per domain
- `source-to-target.csv`
- `decomposition-report.md`. Show the user `<root>/outputs/<loop>/summary.md` and the high-priority rows of `unknowns-register.md`.

Optional, and only with the user's explicit go-ahead: create Jira issues from `<root>/outputs/<loop>/jira-issues.json` using the `create_jira_issue` MCP tool.

## 8. Next loop (the graph iterates)
The loop repeats until each domain meets the exit checklist below. Every run has the same steps 1–7. To start loop n+1:
1. Create `<root>/inputs/loop-<n+1>/manifest.yaml` with `carry_forward: [loop-<n>]`. Earlier files stay citable as `loop-<n>/<path>`; don't copy them.
2. Record answers as files with `provenance: sme-answer`, one per working session or reply. Write each answer in plain sentences, saying who answered. Example: "Customer type values: Individual, Sole Trader, Company."
3. Add new code context with its real provenance: `schema`, `real-code` or `data-sample`. These are the only sources that can reach grade A.
4. Run steps 1–7 with `--loop loop-<n+1>`. The previous loop's published outputs are picked up automatically, which gives you:
   - **stable element ids**
   - **contradictions resolved by authority**: an SME answer beats a real artefact, which beats a document
   - **human decisions carried forward** for elements whose grade has not changed
   - **a change register** (`change-register.md`) for the approvers to review before the new baseline is accepted.

### Exit checklist for a domain baseline
- Every in-scope element is grade A or B, and no X is left.
- High-priority unknowns are closed, or accepted as known gaps by their owner.
- The phase 1–3 gates pass rather than being provisional.
- Each production mapping (phase 9) traces to grade A or B evidence.
- Approvers sign the change register for the baseline version.

After the baseline, keep running the same loop under phase 10 change control. It is then triggered by change requests and new systems instead of discovery batches.

## Rules
- Production mappings (phase 9) need every mapped attribute at grade A or B (`config/evidence_grades.yaml`).
- Assumptions taken from the reference ontology stay at grade D until evidence supports them.
- Keep sensitive inputs local. Prefer local models via Ollama for first-pass extraction when the user's policy requires it.

---
name: ontology-discovery-loop
description: Run one evidence loop of document-led ontology discovery (Enterprise Ontology Playbook, brownfield mode). Use when asked to "run the discovery loop", "process loop-02", "build the as-is ontology from these documents", or to simulate the workflow. Orchestrates the BA, EA, DA and Engineering subagents, the deterministic ontokit pipeline, the Steward and Conformance reviews, and the human approval gate.
---

# Ontology discovery loop

One loop = one evidence batch in `discovery/inputs/<loop>/` with a `manifest.yaml`.
Agents **recommend**; named humans **approve**. Nothing in a documents-only loop
reaches grade A.

## 0. Pick the mode
- **Simulation**: `python -m ontokit simulate --loop <loop>`. Uses rule-based stand-in agents and simulated approvals. Use it for demos and to check the pipeline. Stop after this step.
- **Live** (real material): continue with steps 1–8 below.

## 1. Check the batch
- Confirm `discovery/inputs/<loop>/manifest.yaml` lists every file, with `provenance`, `date` and, where known, a `system_hint`.
- Allowed provenance values: document, wiki, spreadsheet, diagram, example-code, real-code, schema, data-sample.
- Diagrams that only exist as images: read them with your own vision and transcribe them to Mermaid (`.mmd`) next to the image. Add both to the manifest, and put `notes: transcribed from <image>` on the `.mmd` entry.
- If files contain personal data, stop and ask the user whether they may be processed here.

Then run `python -m ontokit ingest --loop <loop>`.

## 2. Agents propose (in parallel)
Launch the four persona subagents **in one message** with the Agent tool:
`ea-agent`, `ba-agent`, `da-agent`, `eng-agent`. Give each:
> Loop `<loop>`. Read `discovery/inputs/<loop>/manifest.yaml` and the files it lists.
> Write `discovery/work/<loop>/proposals/<your key>.json` following your instructions and `schemas/proposal.schema.json`.

## 3. Validate (the guardrail)
Run `python -m ontokit validate --loop <loop>`.
- Read the `rejected` list in `discovery/work/<loop>/validated.json`.
- Send each agent its own rejections (wrong quote, out-of-scope kind, missing evidence) and ask it to fix its file. Allow at most 2 retries per agent, then carry on.
- Never edit an agent's quotes yourself to make them pass.

## 4. Reconcile, grade, check gates
Run `python -m ontokit run --loop <loop>`. It runs:
- ingest
- validate
- Steward merge
- grading
- reference check
- unknowns
- gates
- a pending approvals file
- publish.

It does not invent human decisions. Decisions already recorded in `approvals.yaml` are kept.

## 5. Steward and Conformance review (in parallel)
Launch `ontology-steward` and `conformance-agent` in one message. They write:
- `discovery/work/<loop>/steward-notes.md`
- `discovery/work/<loop>/conformance-briefing.md`

## 6. Human gate
`discovery/work/<loop>/approvals.yaml` lists every element under its approver role, with decision `pending`.
- Show the user the conformance briefing for one approver role at a time.
- Ask for decisions with AskUserQuestion (approve-provisional / defer / reject / note-assumption), batching by grade. The user may instead edit the YAML directly.
- Record each answer in `approvals.yaml`, with `by:` set to the person's role or name as the user gives it, and a `reason:` for rejections.
- **Never fill in decisions the user did not give.** If they want to skip, leave items `pending`.

## 7. Publish
Run `python -m ontokit publish --loop <loop>`. Show the user `discovery/outputs/<loop>/summary.md` and the high-priority rows of `unknowns-register.md`.

Optional, and only with the user's explicit go-ahead: create Jira issues from `discovery/outputs/<loop>/jira-issues.json` using the `create_jira_issue` MCP tool.

## 8. Next loop
When answers or new evidence arrive, create `discovery/inputs/loop-<n+1>/`:
- Copy forward every file from earlier loops (keep their manifest entries).
- Add the new files.
- Record SME answers as a `document` file (e.g. `docs/sme-answers-<date>.md`) quoting who said what.

Run the loop again, then compare `elements.json` between loops. Grade changes and new or removed elements go through the playbook's change process (phase 10) before the new baseline is approved.

## Rules
- Production mappings (phase 9) need every mapped attribute at grade A or B (`config/evidence_grades.yaml`).
- Assumptions taken from the reference ontology stay at grade D until evidence supports them.
- Keep sensitive inputs local. Prefer local models via Ollama for first-pass extraction when the user's policy requires it.

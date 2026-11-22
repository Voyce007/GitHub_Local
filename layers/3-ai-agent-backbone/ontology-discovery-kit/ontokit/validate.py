"""Guardrail for agent output (simulated or live LLM agents).

Checks each proposals/<agent>.json for:
  * shape (mirrors schemas/proposal.schema.json),
  * write scope (an agent may only propose the kinds its RACI row allows),
  * citations (every quote must exist verbatim in a manifest-listed file),
  * origin rules (only "assumed" proposals may come without evidence).
Rejected proposals are dropped and reported; they never reach the Steward.
"""
from __future__ import annotations

from .common import LoopPaths, Trace, load_config, read_json, write_json
from .ingest import quote_found

KINDS = {"concept", "rule", "taxonomy", "system", "flow", "domain", "entity", "attribute",
         "relationship", "identifier", "interface", "event"}
ORIGINS = {"inferred", "assumed", "confirmed"}


def validate_file(agent: str, data: dict, index: dict, scopes: dict) -> tuple[list[dict], list[dict]]:
    accepted, rejected = [], []
    allowed = set(scopes.get(agent, {}).get("may_propose", []))
    for i, p in enumerate(data.get("proposals", [])):
        problems = []
        if p.get("kind") not in KINDS:
            problems.append(f"unknown kind {p.get('kind')!r}")
        elif p["kind"] not in allowed:
            problems.append(f"agent '{agent}' may not propose '{p['kind']}' (RACI write scope)")
        if not str(p.get("name", "")).strip():
            problems.append("missing name")
        if p.get("origin") not in ORIGINS:
            problems.append(f"origin must be one of {sorted(ORIGINS)}")
        if p.get("origin") == "confirmed":
            problems.append("agents cannot mark elements 'confirmed'; only grade-A evidence or a human can")
        ev = p.get("evidence") or []
        if not ev and p.get("origin") != "assumed":
            problems.append("no evidence; inferred proposals must cite a source")
        for e in ev:
            if e.get("file") not in index["sources"]:
                problems.append(f"cites a file not in the manifest: {e.get('file')!r}")
            elif not quote_found(index, e["file"], e.get("quote", "")):
                problems.append(f"quote not found in {e['file']}: {e.get('quote', '')[:60]!r}")
        if problems:
            rejected.append({"agent": agent, "index": i, "name": p.get("name"), "kind": p.get("kind"),
                             "problems": problems})
        else:
            accepted.append({**p, "proposed_by": agent})
    return accepted, rejected


def validate(paths: LoopPaths, trace: Trace) -> list[dict]:
    index = read_json(paths.work / "sources.json")
    scopes = load_config("decision_rights.yaml")["agents"]
    all_ok, all_bad = [], []
    for agent in ("ea", "ba", "da", "eng"):
        fp = paths.proposals / f"{agent}.json"
        if not fp.exists():
            trace.emit("C. Validate", "Validator", "missing proposals", f"{fp.name} not found")
            continue
        ok, bad = validate_file(agent, read_json(fp), index, scopes)
        all_ok += ok
        all_bad += bad
        trace.emit("C. Validate", "Validator", "checked", f"{agent.upper()}: {len(ok)} accepted, {len(bad)} rejected",
                   agent=agent, accepted=len(ok), rejected=len(bad))
        for b in bad:
            trace.emit("C. Validate", "Validator", "rejected", f"{agent.upper()} · {b['kind']} '{b['name']}': {b['problems'][0]}")
    write_json(paths.work / "validated.json", {"accepted": all_ok, "rejected": all_bad})
    return all_ok

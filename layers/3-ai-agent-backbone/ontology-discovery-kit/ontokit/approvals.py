"""Stage I — Human gate: route every element to its approver (decision rights).

`prepare` writes work/<loop>/approvals.yaml with one pending decision per
element, grouped by approver role. A human edits it (or the live Claude Code
orchestrator collects answers with AskUserQuestion and writes them).

Allowed decisions:
  approve-provisional   accept for now; revisit when better evidence arrives
  approve               accept (only sensible for grade A/B)
  reject                remove from the model; give a reason
  defer                 leave open; the linked unknown must be answered first
  note-assumption       keep a grade-D assumption visible, not as as-is fact
  pending               not yet decided (default)

`simulate` fills in the decisions a sensible reviewer would make, and labels
them "simulated" so they can never be mistaken for real sign-off.
"""
from __future__ import annotations

from collections import Counter, defaultdict

import yaml

from .common import LoopPaths, Trace, load_config, read_json

DECISIONS = {"approve", "approve-provisional", "reject", "defer", "note-assumption", "pending"}


def prepare(paths: LoopPaths, trace: Trace, simulate: bool) -> dict:
    model = read_json(paths.work / "model.json")
    rights = load_config("decision_rights.yaml")["approvals"]
    # Keep decisions a human already recorded (matched on id + name), unless simulating.
    previous = {} if simulate else {k: v for k, v in load(paths).items() if v.get("mode") != "simulated"}
    groups: dict[str, list] = defaultdict(list)
    kept = 0
    for e in model["elements"]:
        approver = rights[e["kind"]]["approves"]
        decision, by, reason = "pending", "", ""
        if simulate:
            decision = {"X": "defer", "D": "note-assumption"}.get(e["grade"], "approve-provisional")
            by = "simulated reviewer"
        elif (old := previous.get(e["id"])) and old.get("name") == e["name"]:
            decision, by, reason = old.get("decision", "pending"), old.get("by", ""), old.get("reason", "")
            kept += decision != "pending"
        groups[approver].append({"id": e["id"], "kind": e["kind"], "name": e["name"], "grade": e["grade"],
                                 "recommended_by": rights[e["kind"]]["recommends"], "decision": decision,
                                 "by": by, "reason": reason})
    doc = {"loop": paths.loop, "mode": "simulated" if simulate else "manual",
           "instructions": "Set each decision. Agents recommend; only the named role may approve.",
           "approvers": dict(groups)}
    out = paths.work / "approvals.yaml"
    out.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    if kept:
        trace.emit("I. Human gate", "Human gate", "kept earlier decisions", f"{kept} human decisions carried over")
    for approver, items in groups.items():
        c = Counter(i["decision"] for i in items)
        trace.emit("I. Human gate", "Human gate", f"routed to {approver}",
                   f"{len(items)} items — " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())),
                   approver=approver, decisions=dict(c), simulated=simulate)
    return doc


def load(paths: LoopPaths) -> dict[str, dict]:
    fp = paths.work / "approvals.yaml"
    if not fp.exists():
        return {}
    doc = yaml.safe_load(fp.read_text(encoding="utf-8"))
    out = {}
    for approver, items in (doc.get("approvers") or {}).items():
        for it in items:
            d = it.get("decision", "pending")
            if d not in DECISIONS:
                raise ValueError(f"{it['id']}: unknown decision {d!r}")
            out[it["id"]] = {**it, "approver": approver, "mode": doc.get("mode")}
    return out

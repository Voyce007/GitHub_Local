"""Stage I — Change register (playbook phase 10): what moved since the previous loop.

Runs from loop 2 onwards. Element ids are stable across loops (see
steward.IdAllocator), so a change is matched by id. Unknowns are matched by
question text. The register goes to the human gate with the rest, so
approvers see what moved before they approve the new baseline.
"""
from __future__ import annotations

from .common import LoopPaths, Trace, read_json, write_json

RANK = {"A": 4, "B": 3, "C": 2, "D": 1, "X": 0}


def _brief(e: dict) -> dict:
    return {"id": e["id"], "kind": e["kind"], "name": e["name"], "grade": e["grade"]}


def diff(paths: LoopPaths, prev: LoopPaths, trace: Trace) -> dict:
    before = {e["id"]: e for e in read_json(prev.outputs / "elements.json")}
    after = {e["id"]: e for e in read_json(paths.work / "model.json")["elements"]}
    u_before = {u["question"]: u for u in read_json(prev.outputs / "unknowns.json")}
    u_after = {u["question"]: u for u in read_json(paths.work / "unknowns.json")}

    regraded = []
    for i, e in after.items():
        if i in before and before[i]["grade"] != e["grade"]:
            b = before[i]["grade"]
            regraded.append({**_brief(e), "from": b, "to": e["grade"],
                             "direction": "up" if RANK[e["grade"]] > RANK[b] else "down",
                             "reason": e.get("grade_reason", "")})
    resolved = [{**_brief(e), "resolutions": [{"property": r["property"], "value": r["value"],
                                               "resolved_by": r["resolved_by"],
                                               "superseded": [v["value"] for v in r["superseded"]]}
                                              for r in e["resolutions"]]}
                for i, e in after.items() if e.get("resolutions") and before.get(i, {}).get("grade") == "X"]
    changes = {
        "from_loop": prev.loop, "to_loop": paths.loop,
        "added": [_brief(e) for i, e in after.items() if i not in before],
        "removed": [_brief(e) for i, e in before.items() if i not in after],
        "regraded": sorted(regraded, key=lambda r: (r["direction"] != "up", r["kind"], r["name"])),
        "resolved": resolved,
        "unknowns_closed": [{"id": u["id"], "question": u["question"]} for q, u in u_before.items() if q not in u_after],
        "unknowns_opened": [{"id": u["id"], "question": u["question"]} for q, u in u_after.items() if q not in u_before],
        "unknowns_still_open": sum(1 for q in u_after if q in u_before),
    }
    up = sum(1 for r in regraded if r["direction"] == "up")
    changes["summary"] = {
        "added": len(changes["added"]), "removed": len(changes["removed"]), "graded_up": up,
        "graded_down": len(regraded) - up, "contradictions_resolved": len(resolved),
        "unknowns_closed": len(changes["unknowns_closed"]), "unknowns_opened": len(changes["unknowns_opened"]),
        "unknowns_still_open": changes["unknowns_still_open"],
    }
    write_json(paths.work / "changes.json", changes)

    st = "I. Change register"
    s = changes["summary"]
    trace.emit(st, "Ontology Steward", f"compared with {prev.loop}",
               f"{s['graded_up']} graded up, {s['graded_down']} down, {s['added']} added, {s['removed']} removed; "
               f"{s['contradictions_resolved']} contradictions resolved; unknowns {s['unknowns_closed']} closed, "
               f"{s['unknowns_opened']} new, {s['unknowns_still_open']} still open", summary=s)
    for r in resolved:
        for x in r["resolutions"]:
            val = ", ".join(x["value"]) if isinstance(x["value"], list) else x["value"]
            trace.emit(st, "Ontology Steward", "resolved", f"{r['kind']} '{r['name']}' X → {r['grade']}: {x['property']} = {val}",
                       element=r["id"])
    for r in regraded:
        if r["direction"] == "up" and r["to"] == "A" and r["kind"] in ("entity", "identifier", "system"):
            trace.emit(st, "Ontology Steward", "graded up", f"{r['kind']} '{r['name']}' {r['from']} → {r['to']}: {r['reason']}",
                       element=r["id"])
    for r in regraded:
        if r["direction"] == "down":
            trace.emit(st, "Ontology Steward", "graded down", f"{r['kind']} '{r['name']}' {r['from']} → {r['to']}: {r['reason']}",
                       element=r["id"])
    for u in changes["unknowns_closed"]:
        trace.emit(st, "Ontology Steward", "unknown closed", f"{u['id']} ({prev.loop}): {u['question']}")
    return changes

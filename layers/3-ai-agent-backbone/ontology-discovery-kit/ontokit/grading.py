"""Stage E — Conformance agent: grade every element (A/B/C/D/X).

Rules (config/evidence_grades.yaml):
  X  any contradiction
  A  any evidence from real-code / schema / data-sample
  B  two or more distinct, current (non-stale) files
  C  one file, or only stale files
  D  assumed (reference ontology) or no usable evidence
For concepts, a bare mention does not support the definition: only
`definition`, `structure` or `value-list` evidence counts.
"""
from __future__ import annotations

from collections import Counter

from .common import LoopPaths, Trace, load_config, read_json, write_json


def grade_element(el: dict, index: dict, ceiling: dict) -> tuple[str, str]:
    if el["conflicts"]:
        return "X", "sources contradict on " + ", ".join(c["property"] for c in el["conflicts"])
    ev = el["evidence"]
    if el["kind"] == "concept":
        ev = [e for e in ev if e.get("support") != "mention"]
    if el["origin"] == "assumed" or not ev:
        return "D", "assumed from reference ontology" if el["origin"] == "assumed" else "no definitional evidence"
    files = {e["file"] for e in ev}
    provs = {index["sources"][f]["provenance"] for f in files}
    if any(ceiling.get(p) == "A" for p in provs):
        return "A", "confirmed by a real system artefact"
    current = sorted(f for f in files if not index["sources"][f]["stale"])
    if len(current) >= 2:
        return "B", f"{len(current)} independent current sources"
    if len(files) == 1:
        return "C", "single source"
    return "C", "only one current source (others stale)"


def grade(paths: LoopPaths, trace: Trace) -> dict:
    model = read_json(paths.work / "model.json")
    index = read_json(paths.work / "sources.json")
    ceiling = load_config("evidence_grades.yaml")["provenance_ceiling"]
    for el in model["elements"]:
        el["grade"], el["grade_reason"] = grade_element(el, index, ceiling)
    dist = Counter(e["grade"] for e in model["elements"])
    write_json(paths.work / "model.json", model)
    trace.emit("E. Grade evidence", "Conformance agent", "graded",
               " · ".join(f"{g}: {dist.get(g, 0)}" for g in "ABCDX"), distribution={g: dist.get(g, 0) for g in "ABCDX"})
    for el in model["elements"]:
        if el["grade"] == "X" or (el["kind"] in ("system", "concept", "identifier") and el["grade"] in "BC"):
            trace.emit("E. Grade evidence", "Conformance agent", f"grade {el['grade']}",
                       f"{el['kind']} '{el['name']}': {el['grade_reason']}", element=el["id"], grade=el["grade"])
    return model

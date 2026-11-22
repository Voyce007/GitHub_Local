"""Stage F — Compare the as-is model with the reference ontology (playbook section 6).

Matches are recorded on the as-is element. Anything the reference expects but
the evidence does not show is added as an element with origin "assumed",
grade D, so the gap is visible and turns into an unknown. It is never
presented as as-is fact.
"""
from __future__ import annotations

from collections import Counter

from .common import LoopPaths, Trace, load_config, norm, read_json, write_json


def apply_prior(paths: LoopPaths, trace: Trace) -> dict:
    model = read_json(paths.work / "model.json")
    ref = load_config("reference_ontology.yaml")
    els = model["elements"]
    counters = Counter(e["id"].split("-")[0] for e in els)

    def new_id(prefix):
        counters[prefix] += 1
        return f"{prefix}-{counters[prefix]:02d}"

    names = {}
    for e in els:
        if e["kind"] in ("concept", "entity"):
            for n in [e["name"], *e.get("aliases", [])]:
                names.setdefault(norm(n), e)

    matched, assumed = [], []
    for r in ref["entities"]:
        hit = names.get(norm(r["name"]))
        if hit:
            hit["properties"]["reference_match"] = r["name"]
            hit["properties"]["domain"] = r["domain"]
            matched.append(r["name"])
        else:
            el = {"id": new_id("ENT"), "kind": "entity", "name": r["name"], "aliases": [], "definition": "",
                  "properties": {"domain": r["domain"], "reference": True}, "evidence": [], "proposed_by": ["reference"],
                  "conflicts": [], "origin": "assumed", "grade": "D", "grade_reason": "assumed from reference ontology",
                  "status": "proposed"}
            els.append(el)
            assumed.append(el)

    rels = [e for e in els if e["kind"] == "relationship"]
    for r in ref["relationships"]:
        a, b = norm(r["from"]), norm(r["to"])
        hit = next((x for x in rels if {norm(x["properties"]["from"]), norm(x["properties"]["to"])} == {a, b}), None)
        label = f"{r['from']} {r['verb']} {r['to']}"
        if hit:
            hit["properties"]["reference_match"] = label
            matched.append(label)
        else:
            el = {"id": new_id("REL"), "kind": "relationship", "name": label, "aliases": [], "definition": "",
                  "properties": {"from": r["from"], "to": r["to"], "verb": r["verb"], "reference": True},
                  "evidence": [], "proposed_by": ["reference"], "conflicts": [], "origin": "assumed",
                  "grade": "D", "grade_reason": "assumed from reference ontology", "status": "proposed"}
            els.append(el)
            assumed.append(el)

    write_json(paths.work / "model.json", model)
    trace.emit("F. Reference check", "Ontology Steward", "compared with reference ontology",
               f"{len(matched)} reference items found in evidence; {len(assumed)} added as assumptions (grade D)",
               matched=matched, assumed=[a["name"] for a in assumed])
    for a in assumed:
        trace.emit("F. Reference check", "Ontology Steward", "assumed (D)", f"{a['kind']} '{a['name']}' — expected by reference, not seen in evidence",
                   element=a["id"])
    return model

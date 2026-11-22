"""Stage F — Compare the as-is model with the reference ontology (playbook section 6).

Matches are recorded on the as-is element. Anything the reference expects but
the evidence does not show is added as an element with origin "assumed",
grade D, so the gap is visible and turns into an unknown. It is never
presented as as-is fact.
"""
from __future__ import annotations

import yaml

from .common import LoopPaths, Trace, load_config, norm, read_json, write_json
from .steward import IdAllocator, _key


def apply_prior(paths: LoopPaths, trace: Trace) -> dict:
    model = read_json(paths.work / "model.json")
    # a scenario may bring its own reference prior next to its inputs/
    override = paths.root / "reference_ontology.yaml"
    ref = yaml.safe_load(override.read_text(encoding="utf-8")) if override.exists() else load_config("reference_ontology.yaml")
    els = model["elements"]
    ids = IdAllocator(state=model["id_state"])

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
            hit["properties"]["reference_domain"] = r["domain"]
            matched.append(r["name"])
        else:
            el = {"id": ids.get(_key({"kind": "entity", "name": r["name"]}), "entity"), "kind": "entity",
                  "name": r["name"], "aliases": [], "definition": "", "resolutions": [],
                  "properties": {"reference_domain": r["domain"], "reference": True}, "evidence": [], "proposed_by": ["reference"],
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
            el = {"id": ids.get(_key({"kind": "relationship", "name": label, "properties": {"from": r["from"], "to": r["to"]}}),
                                "relationship"),
                  "kind": "relationship", "name": label, "aliases": [], "definition": "", "resolutions": [],
                  "properties": {"from": r["from"], "to": r["to"], "verb": r["verb"], "reference": True},
                  "evidence": [], "proposed_by": ["reference"], "conflicts": [], "origin": "assumed",
                  "grade": "D", "grade_reason": "assumed from reference ontology", "status": "proposed"}
            els.append(el)
            assumed.append(el)

    model["id_state"] = ids.state()
    write_json(paths.work / "model.json", model)
    trace.emit("F. Reference check", "Ontology Steward", "compared with reference ontology",
               f"{len(matched)} reference items found in evidence; {len(assumed)} added as assumptions (grade D)",
               matched=matched, assumed=[a["name"] for a in assumed])
    for a in assumed:
        trace.emit("F. Reference check", "Ontology Steward", "assumed (D)", f"{a['kind']} '{a['name']}' — expected by reference, not seen in evidence",
                   element=a["id"])
    return model

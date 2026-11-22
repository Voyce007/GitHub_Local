"""Stage H — Conformance agent: automated exit-gate checks for the loop's phases.

Each criterion returns the elements that fail it. Result per criterion:
  pass         nothing fails
  provisional  failures exist but every one is covered by an open unknown,
               or the phase is "provisional" in discovery mode
  fail         an uncovered failure
A phase result is its worst criterion; a phase whose in-scope elements are
not all grade A/B can at best be provisional.
"""
from __future__ import annotations

from .common import LoopPaths, Trace, load_config, norm, read_json, write_json

SCOPE = {1: {"system", "flow"}, 2: {"concept", "taxonomy", "rule"},
         3: {"entity", "attribute", "relationship", "identifier"}}
RANK = {"pass": 0, "provisional": 1, "fail": 2}


def _checks(model, unknowns, index, cfg):
    E = [e for e in model["elements"]]
    by = lambda k: [e for e in E if e["kind"] == k]
    real = lambda k: [e for e in by(k) if e["origin"] != "assumed"]
    covered = {a for u in unknowns for a in u["affects"]}
    return covered, {
        "all_inputs_ingested": lambda: index["missing"],
        "systems_have_role_or_unknown": lambda: [s["id"] for s in by("system") if not s["properties"].get("roles")],
        "systems_have_evidence": lambda: [s["id"] for s in by("system") if not s["evidence"]],
        "unknowns_published": lambda: [] if unknowns else ["(no unknowns register)"],
        "concepts_defined": lambda: [c["id"] for c in by("concept") if not c["definition"]],
        "synonyms_registered": lambda: [] if any(c["aliases"] for c in by("concept")) else ["(no synonyms)"],
        "conflicts_have_unknowns": lambda: [e["id"] for e in E if e["conflicts"]],
        "key_concepts_present": lambda: [k for k in cfg["key_concepts"]
                                         if norm(k) not in {norm(c["name"]) for c in by("concept")}],
        "entities_have_attributes": lambda: [e["id"] for e in real("entity") if not e["properties"].get("attribute_ids")],
        "entities_traced_to_concepts": lambda: [e["id"] for e in real("entity") if "realises" not in e["properties"]
                                                and not e["properties"].get("link_entity")],
    }


def run_gates(paths: LoopPaths, trace: Trace) -> list[dict]:
    model = read_json(paths.work / "model.json")
    unknowns = read_json(paths.work / "unknowns.json")
    index = read_json(paths.work / "sources.json")
    cfg = load_config("playbook.yaml")
    covered, checks = _checks(model, unknowns, index, cfg)
    results = []
    for ph in cfg["phases"]:
        if ph["id"] not in cfg["loop1_gated_phases"]:
            continue
        crit_results = []
        for c in ph.get("loop1_criteria", []):
            failing = checks[c["check"]]()
            if c["check"] == "conflicts_have_unknowns":
                failing = [f for f in failing if f not in covered]
                status = "pass" if not failing else "fail"
            elif not failing:
                status = "pass"
            elif all(f in covered for f in failing):
                status = "provisional"
            else:
                status = "fail"
            crit_results.append({**c, "status": status, "failing": failing,
                                 "covered_by_unknowns": [f for f in failing if f in covered]})
        in_scope = [e for e in model["elements"] if e["kind"] in SCOPE.get(ph["id"], set())]
        weak = [e["id"] for e in in_scope if e["grade"] not in ("A", "B")]
        status = max((c["status"] for c in crit_results), key=RANK.get, default="pass")
        if status == "pass" and (weak or ph["discovery_mode"] == "provisional"):
            status = "provisional"
        res = {"phase": ph["id"], "name": ph["name"], "exit_gate": ph["exit_gate"], "status": status,
               "discovery_mode": ph["discovery_mode"], "criteria": crit_results,
               "in_scope": len(in_scope), "below_B": len(weak)}
        results.append(res)
        trace.emit("H. Gate checks", "Conformance agent", f"phase {ph['id']} gate: {status}",
                   f"{ph['name']} — " + "; ".join(f"{c['id']} {c['status']}" for c in crit_results)
                   + f"; {len(weak)}/{len(in_scope)} in-scope elements below grade B",
                   phase=ph["id"], status=status)
    write_json(paths.work / "gates.json", results)
    return results

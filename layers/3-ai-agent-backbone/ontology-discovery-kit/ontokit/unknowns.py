"""Stage G — Unknowns register: turn gaps into precise questions and evidence requests.

The register is the main working output of a document-led loop. Each item
names who should answer it (from decision rights) and what it would affect.
"""
from __future__ import annotations

from collections import Counter

from .common import LoopPaths, Trace, load_config, read_json, write_json

WEIGHT = {"high": 3, "medium": 2, "low": 1}


def _fmt(v):
    return ", ".join(v) if isinstance(v, list) else str(v)


def build_unknowns(paths: LoopPaths, trace: Trace) -> list[dict]:
    model = read_json(paths.work / "model.json")
    index = read_json(paths.work / "sources.json")
    approvals = load_config("decision_rights.yaml")["approvals"]
    els = {e["id"]: e for e in model["elements"]}
    items: list[dict] = []

    def add(kind, priority, question, why, affects, owner):
        items.append({"type": kind, "priority": priority, "question": question, "why": why,
                      "affects": affects, "owner": owner, "status": "open"})

    # 1. Contradictions
    for e in model["elements"]:
        for c in e["conflicts"]:
            parts = []
            for v in c["variants"]:
                src = "; ".join(f"{f}" + (f" (stale, {index['sources'][f]['age_years']} yrs)" if f in v["stale"] else "")
                                for f in v["files"])
                parts.append(f"{_fmt(v['value'])} ← {src}")
            add("sme_question", "high",
                f"Sources disagree on the {c['property'].replace('_', ' ')} of {e['kind']} '{e['name']}'. Which is correct today?",
                " | ".join(parts), [e["id"]], approvals[e["kind"]]["approves"])

    # 2. Steward review flags
    for f in model["flags"]:
        first = els[f["affects"][0]]
        if f["type"] == "homonym_risk":
            add("sme_question", "high",
                f"Is '{f['term']}' a synonym of {f['concept']}, or a different concept (a role) that shares the name?", f["detail"],
                f["affects"], "Business Domain Owner")
        elif f["type"] == "candidate_synonym":
            add("sme_question", "medium", f"Are these the same thing? {f['detail']}.",
                "Merging them changes the entity catalogue and the stand-in schema.", f["affects"],
                "Domain Owner and Data Architecture Authority")
        elif f["type"] == "unrealised_concept":
            add("sme_question", "medium", f"Where is '{first['name']}' held, and which system is the source of truth?",
                f["detail"], f["affects"], "Data Architecture Authority")
        elif f["type"] == "implied_entity":
            add("evidence_request", "medium", f"What does '{first['name']}' contain, and which system holds it?",
                f["detail"], f["affects"], "Data Architecture Authority")
        elif f["type"] == "system_without_role":
            add("sme_question", "medium", f"What is '{first['name']}', who owns it, and does it master any data?",
                f["detail"], f["affects"], "Enterprise Architecture Authority")

    # 3. Reference assumptions
    for e in model["elements"]:
        if e["origin"] == "assumed":
            q = (f"The reference model expects '{e['name']}'. Does the organisation have it, and where is it recorded?"
                 if e["kind"] == "entity" else
                 f"The reference model expects '{e['name']}'. Is this relationship real here, and which system records it?")
            add("sme_question", "low", q, "Added at grade D from the playbook's reference ontology; no evidence yet.",
                [e["id"]], approvals[e["kind"]]["approves"])

    # 4. Evidence requests: the path to grade A
    by_system = Counter()
    for e in model["elements"]:
        if e["kind"] in ("entity", "attribute", "identifier") and e["origin"] != "assumed" and e["grade"] != "A":
            sysname = e["properties"].get("system") or els.get(e["properties"].get("entity_id", ""), {}).get("properties", {}).get("system")
            if sysname:
                by_system[sysname] += 1
    for sysname, n in by_system.most_common():
        affects = [e["id"] for e in model["elements"] if e["kind"] == "system" and e["name"] == sysname]
        add("evidence_request", "high" if n >= 5 else "medium",
            f"Request a schema export and a masked data sample from {sysname}.",
            f"Would let {n} entity/attribute/identifier elements move to grade A.", affects,
            "Engineering Lead (with the system owner)")

    for i, it in enumerate(sorted(items, key=lambda x: (-WEIGHT[x["priority"]], -len(x["affects"]), x["question"])), 1):
        it["id"] = f"U-{i:02d}"
    items.sort(key=lambda x: x["id"])
    write_json(paths.work / "unknowns.json", items)
    pc = Counter(i["priority"] for i in items)
    trace.emit("G. Unknowns", "Ontology Steward", "unknowns register built",
               f"{len(items)} items — high {pc.get('high', 0)}, medium {pc.get('medium', 0)}, low {pc.get('low', 0)}",
               priorities=dict(pc))
    for it in items:
        if it["priority"] == "high":
            trace.emit("G. Unknowns", "Ontology Steward", it["id"], it["question"], owner=it["owner"])
    return items

"""Stage D — Ontology Steward: reconcile the four agents' proposals into one model.

1. Resolve system aliases (CustHub = Customer Hub = CH = "the CRM" ...).
2. Canonicalise every system reference inside other elements.
3. Merge duplicate proposals into elements; collect evidence; detect contradictions
   on comparable properties (taxonomy values, identifier issuer).
4. Link concepts <-> entities <-> identifiers for traceability.
5. Raise review flags: candidate synonyms, homonym risks, unrealised concepts,
   systems with no role. These become unknowns; the Steward never decides them.
The Steward merges and links only. It never invents an element.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from .common import LoopPaths, Trace, norm, read_json, write_json

COMPARABLE = {"values", "issued_by"}            # disagreement here = contradiction
LIST_PROPS = {"roles"}                           # unioned
SYSTEM_REFS = ("source", "target", "producer", "consumer", "issued_by", "system")
PREFIX = {"system": "SYS", "flow": "FLW", "concept": "CON", "rule": "RUL", "taxonomy": "TAX",
          "entity": "ENT", "attribute": "ATT", "relationship": "REL", "identifier": "IDN",
          "interface": "INT", "event": "EVT", "domain": "DOM"}
ROLE_SUFFIXES = {"instruction", "record", "detail", "details", "info", "master", "data"}


def sysnorm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", re.sub(r"^the\s+", "", name.strip(), flags=re.I).lower())


class _UF:
    def __init__(self):
        self.p: dict[str, str] = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


def _resolve_systems(proposals: list[dict], trace: Trace) -> dict[str, str]:
    uf = _UF()
    names: dict[str, Counter] = defaultdict(Counter)
    display: dict[str, str] = {}
    for p in proposals:
        if p["kind"] != "system":
            continue
        k = sysnorm(p["name"])
        uf.find(k)
        names[k][p["name"]] += 1
        display.setdefault(k, p["name"])
        for a in p.get("aliases", []):
            uf.union(sysnorm(a), k)
            display.setdefault(sysnorm(a), a)
    groups: dict[str, set] = defaultdict(set)
    for k in list(uf.p):
        groups[uf.find(k)].add(k)

    def score(n: str, c: int):
        camel = bool(re.fullmatch(r"[A-Z][a-z]+(?:[A-Z][a-z]+)+", n))
        return (camel, c, n[:1].isupper(), len(n))

    lookup: dict[str, str] = {}
    for root, keys in groups.items():
        cands = Counter()
        for k in keys:
            cands.update(names.get(k, {}))
        if not cands:
            continue
        canon = max(cands.items(), key=lambda kv: score(*kv))[0]
        for k in keys:
            lookup[k] = canon
        forms = sorted({display[k] for k in keys if k != sysnorm(canon)}, key=str.lower)
        if forms:
            trace.emit("D. Steward reconciles", "Ontology Steward", "resolved aliases",
                       f"{canon} = " + ", ".join(forms), system=canon, aliases=forms)
    return lookup


def _key(p: dict) -> str:
    pr = p.get("properties", {})
    k = p["kind"]
    if k == "system":
        return f"system:{sysnorm(p['name'])}"
    if k == "flow":
        return f"flow:{sysnorm(pr['source'])}>{sysnorm(pr['target'])}"
    if k == "attribute":
        return f"attribute:{norm(pr['entity'])}.{norm(pr['attribute'])}"
    if k == "relationship":
        return f"relationship:{norm(pr['from'])}>{norm(pr['to'])}"
    if k == "interface":
        return f"interface:{p['name'].upper()}"
    return f"{k}:{norm(p['name'])}"


def reconcile(paths: LoopPaths, trace: Trace) -> dict:
    accepted = read_json(paths.work / "validated.json")["accepted"]
    index = read_json(paths.work / "sources.json")
    lookup = _resolve_systems(accepted, trace)
    canon = lambda v: lookup.get(sysnorm(v), v) if isinstance(v, str) else v

    # Canonicalise names and references
    for p in accepted:
        if p["kind"] == "system":
            p["name"] = canon(p["name"])
            p["aliases"] = [a for a in p.get("aliases", []) if canon(a) != a or sysnorm(a) != sysnorm(p["name"])]
        pr = p.setdefault("properties", {})
        for f in SYSTEM_REFS:
            if f in pr:
                pr[f] = canon(pr[f])
        if p["kind"] == "flow":
            p["name"] = f"{pr['source']} → {pr['target']}"

    # Merge
    buckets: dict[str, list[dict]] = defaultdict(list)
    for p in accepted:
        buckets[_key(p)].append(p)

    elements: list[dict] = []
    counters: Counter = Counter()
    for key, group in buckets.items():
        kind = group[0]["kind"]
        counters[kind] += 1
        names = Counter(p["name"] for p in group)
        if kind == "concept":
            name = next((p["name"] for p in group if p.get("definition")), names.most_common(1)[0][0])
        else:
            name = names.most_common(1)[0][0]
        el = {"id": f"{PREFIX[kind]}-{counters[kind]:02d}", "kind": kind, "name": name, "aliases": [],
              "definition": "", "properties": {}, "evidence": [], "proposed_by": [], "conflicts": [],
              "origin": "inferred", "grade": None, "status": "proposed"}
        variants: dict[str, dict] = defaultdict(dict)
        for p in group:
            for a in p.get("aliases", []):
                if a not in el["aliases"] and a != name:
                    el["aliases"].append(a)
            if p.get("definition") and not el["definition"]:
                el["definition"] = p["definition"]
            for k, v in p.get("properties", {}).items():
                if k in COMPARABLE:
                    vkey = repr(sorted(v)) if isinstance(v, list) else repr(v)
                    slot = variants[k].setdefault(vkey, {"value": v, "files": []})
                    for e in p["evidence"]:
                        if e["file"] not in slot["files"]:
                            slot["files"].append(e["file"])
                elif k in LIST_PROPS:
                    el["properties"].setdefault(k, [])
                    el["properties"][k] += [x for x in v if x not in el["properties"][k]]
                elif k == "codes":
                    el["properties"].setdefault("codes", {}).update(v)
                else:
                    el["properties"].setdefault(k, v)
            for e in p["evidence"]:
                if not any(x["file"] == e["file"] and x["locator"] == e.get("locator") for x in el["evidence"]):
                    el["evidence"].append(dict(e))
            if p["proposed_by"] not in el["proposed_by"]:
                el["proposed_by"].append(p["proposed_by"])
            if p.get("origin") == "assumed" and len(group) == 1:
                el["origin"] = "assumed"
        for prop, vs in variants.items():
            if len(vs) == 1:
                el["properties"][prop] = next(iter(vs.values()))["value"]
            else:
                el["conflicts"].append({
                    "property": prop,
                    "variants": [{"value": v["value"], "files": v["files"],
                                  "stale": [f for f in v["files"] if index["sources"][f]["stale"]]}
                                 for v in vs.values()],
                })
        elements.append(el)
        if len(group) > 1:
            trace.emit("D. Steward reconciles", "Ontology Steward", "merged",
                       f"{kind} '{name}': {len(group)} proposals from {', '.join(sorted(set(el['proposed_by'])))} "
                       f"across {len({e['file'] for e in el['evidence']})} files", element=el["id"])
        for c in el["conflicts"]:
            desc = " vs ".join(f"{v['value']} ({', '.join(v['files'])})" for v in c["variants"])
            trace.emit("D. Steward reconciles", "Ontology Steward", "contradiction",
                       f"{kind} '{name}' · {c['property']}: {desc}", element=el["id"])

    flags = _link_and_flag(elements, trace)

    # Evidence register ids
    reg: dict[tuple, str] = {}
    for el in elements:
        for e in el["evidence"]:
            k = (e["file"], e.get("locator"))
            if k not in reg:
                reg[k] = f"E-{len(reg) + 1:03d}"
            e["id"] = reg[k]

    model = {"loop": paths.loop, "system_lookup": lookup, "elements": elements, "flags": flags}
    write_json(paths.work / "model.json", model)
    counts = Counter(e["kind"] for e in elements)
    trace.emit("D. Steward reconciles", "Ontology Steward", "model assembled",
               f"{len(accepted)} proposals → {len(elements)} elements; "
               f"{sum(1 for e in elements if e['conflicts'])} contradictions; {len(flags)} review flags",
               counts=dict(counts))
    return model


def _link_and_flag(elements: list[dict], trace: Trace) -> list[dict]:
    by_kind = defaultdict(list)
    for e in elements:
        by_kind[e["kind"]].append(e)
    ents = {norm(e["name"]): e for e in by_kind["entity"]}
    concepts = {norm(c["name"]): c for c in by_kind["concept"]}
    flags: list[dict] = []

    # attributes -> entities
    for a in by_kind["attribute"]:
        ent = ents.get(norm(a["properties"]["entity"]))
        if ent:
            a["properties"]["entity_id"] = ent["id"]
            ent["properties"].setdefault("attribute_ids", []).append(a["id"])
    # identifiers -> entities, concepts
    for i in by_kind["identifier"]:
        if ent := ents.get(norm(i["properties"].get("entity", ""))):
            i["properties"]["entity_id"] = ent["id"]
        if con := concepts.get(norm(i["name"])):
            i["properties"]["defined_by"] = con["id"]
            con["properties"]["defines_identifier"] = i["id"]
    # concepts <-> entities
    for n, c in concepts.items():
        if ent := ents.get(n):
            ent["properties"]["realises"] = c["id"]
            c["properties"]["realised_by"] = ent["id"]
            trace.emit("D. Steward reconciles", "Ontology Steward", "linked",
                       f"concept '{c['name']}' is realised by entity '{ent['name']}' ({ent['properties'].get('system')})")

    # homonym risk: a concept synonym that names a different entity
    for c in by_kind["concept"]:
        for alias in c["aliases"]:
            ent = ents.get(norm(alias))
            if ent and norm(ent["name"]) != norm(c["name"]):
                flags.append({"type": "homonym_risk", "affects": [c["id"], ent["id"]], "term": alias, "concept": c["name"],
                              "detail": f"Glossary lists '{alias}' as a synonym of {c['name']}, but "
                                        f"{ent['properties'].get('system', 'a system')} has an entity "
                                        f"'{ent['name']}' with its own structure."})
    # candidate synonyms by name containment
    named = {**{norm(e["name"]): e for e in by_kind["entity"]}}
    pool = {**concepts, **named}
    for n1, e1 in named.items():
        for n2, e2 in pool.items():
            if n1 == n2 or n2 not in n1 or len(n2) < 5:
                continue
            if n1.startswith(n2) and n1[len(n2):] in ROLE_SUFFIXES:
                why = f"'{e1['name']}' looks like '{e2['name']}' with a role suffix"
            elif n1.endswith(n2) and n1[: -len(n2)] in pool and e2["kind"] == "entity":
                why = f"'{e2['name']}' may be the unqualified form of '{e1['name']}'"
            else:
                continue
            flags.append({"type": "candidate_synonym", "affects": [e1["id"], e2["id"]], "detail": why})
    # concepts with no structural realisation
    for c in by_kind["concept"]:
        if "realised_by" in c["properties"] or "defines_identifier" in c["properties"]:
            continue
        if any(c["id"] in f["affects"] for f in flags):
            continue
        hint = next((s["name"] for s in by_kind["system"] if norm(c["name"])[:6] in norm(s["name"])), None)
        flags.append({"type": "unrealised_concept", "affects": [c["id"]],
                      "detail": f"No entity found for '{c['name']}'." + (f" Possible home: {hint}." if hint else ""),
                      **({"hint_system": hint} if hint else {})})
    # systems with no role
    for s in by_kind["system"]:
        if not s["properties"].get("roles"):
            flags.append({"type": "system_without_role", "affects": [s["id"]],
                          "detail": f"'{s['name']}' appears in {len({e['file'] for e in s['evidence']})} source(s) "
                                    f"but nothing says what it does."})
    for f in flags:
        trace.emit("D. Steward reconciles", "Ontology Steward", "flagged", f"{f['type']}: {f['detail']}")
    return flags

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

from .common import LoopPaths, Trace, load_config, norm, read_json, tokens, write_json

COMPARABLE = {"values", "issued_by"}            # disagreement here = contradiction
LIST_PROPS = {"roles", "confirmed_synonyms", "not_synonyms", "reads", "writes", "writes_columns"}   # unioned
SYSTEM_REFS = ("source", "target", "producer", "consumer", "issued_by", "system")
PREFIX = {"system": "SYS", "flow": "FLW", "concept": "CON", "rule": "RUL", "taxonomy": "TAX",
          "entity": "ENT", "attribute": "ATT", "relationship": "REL", "identifier": "IDN",
          "interface": "INT", "event": "EVT", "domain": "DOM", "capability": "CAP", "calculation": "CAL"}
ROLE_SUFFIXES = {"instruction", "request", "record", "detail", "details", "info", "master", "data"}


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


class IdAllocator:
    """Keeps element ids stable across loops: same key in a later loop -> same id."""

    def __init__(self, prev_elements=None, state=None):
        if state:
            self.prev, self.counters, self.used = state["prev"], Counter(state["counters"]), set(state["used"])
            return
        self.prev, self.counters, self.used = {}, Counter(), set()
        for e in prev_elements or []:
            self.prev[_key(e)] = e["id"]
            pre, num = e["id"].rsplit("-", 1)
            self.counters[pre] = max(self.counters[pre], int(num))

    def get(self, key: str, kind: str, alt=()) -> str:
        for k in (key, *alt):
            pid = self.prev.get(k)
            if pid and pid not in self.used:
                self.used.add(pid)
                return pid
        pre = PREFIX[kind]
        self.counters[pre] += 1
        nid = f"{pre}-{self.counters[pre]:02d}"
        self.used.add(nid)
        return nid

    def state(self) -> dict:
        return {"prev": self.prev, "counters": dict(self.counters), "used": sorted(self.used)}


def reconcile(paths: LoopPaths, trace: Trace, prev_elements: list | None = None) -> dict:
    accepted = read_json(paths.work / "validated.json")["accepted"]
    index = read_json(paths.work / "sources.json")
    authority = load_config("evidence_grades.yaml").get("authority", {})
    auth = lambda f: authority.get(index["sources"][f]["provenance"], 1)
    ids = IdAllocator(prev_elements)
    if prev_elements:
        trace.emit("D. Steward reconciles", "Ontology Steward", "loaded previous baseline",
                   f"{len(prev_elements)} elements from the previous loop; matching elements keep their ids")
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

    rev: dict[str, set] = defaultdict(set)
    for k, v in lookup.items():
        rev[v].add(k)
    names_of = lambda n: rev.get(n, set()) | {sysnorm(n)}

    # Merge
    buckets: dict[str, list[dict]] = defaultdict(list)
    for p in accepted:
        buckets[_key(p)].append(p)

    elements: list[dict] = []
    for key, group in buckets.items():
        kind = group[0]["kind"]
        names = Counter(p["name"] for p in group)
        if kind == "concept":
            name = next((p["name"] for p in group if p.get("definition")), names.most_common(1)[0][0])
        else:
            name = names.most_common(1)[0][0]
        alt = []
        if kind == "system":
            alt = [f"system:{sysnorm(a)}" for p in group for a in p.get("aliases", [])]
        elif kind == "flow":
            pr0 = group[0]["properties"]
            alt = [f"flow:{a}>{b}" for a in names_of(pr0["source"]) for b in names_of(pr0["target"])]
        el = {"id": ids.get(key, kind, alt), "kind": kind, "name": name, "aliases": [],
              "definition": "", "properties": {}, "evidence": [], "proposed_by": [], "conflicts": [],
              "resolutions": [], "origin": "inferred", "grade": None, "status": "proposed"}
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
                continue
            vlist = [{"value": v["value"], "files": v["files"],
                      "stale": [f for f in v["files"] if index["sources"][f]["stale"]],
                      "authority": max(auth(f) for f in v["files"])} for v in vs.values()]
            top = max(v["authority"] for v in vlist)
            winners = [v for v in vlist if v["authority"] == top]
            if top >= 2 and len(winners) == 1:
                w = winners[0]
                el["properties"][prop] = w["value"]
                el["resolutions"].append({"property": prop, "value": w["value"], "supported_by": w["files"],
                                          "resolved_by": [f for f in w["files"] if auth(f) == top],
                                          "superseded": [v for v in vlist if v is not w]})
            else:
                el["conflicts"].append({"property": prop, "variants": vlist})
        elements.append(el)
        if len(group) > 1:
            trace.emit("D. Steward reconciles", "Ontology Steward", "merged",
                       f"{kind} '{name}': {len(group)} proposals from {', '.join(sorted(set(el['proposed_by'])))} "
                       f"across {len({e['file'] for e in el['evidence']})} files", element=el["id"])
        for c in el["conflicts"]:
            desc = " vs ".join(f"{v['value']} ({', '.join(v['files'])})" for v in c["variants"])
            trace.emit("D. Steward reconciles", "Ontology Steward", "contradiction",
                       f"{kind} '{name}' · {c['property']}: {desc}", element=el["id"])
        for r in el["resolutions"]:
            val = ", ".join(r["value"]) if isinstance(r["value"], list) else r["value"]
            trace.emit("D. Steward reconciles", "Ontology Steward", "contradiction resolved",
                       f"{kind} '{name}' · {r['property']} = {val} (decided by {', '.join(r['resolved_by'])}; "
                       f"{len(r['superseded'])} superseded variant(s) kept for audit)", element=el["id"])

    flags = _link_and_flag(elements, trace)

    # Evidence register ids
    reg: dict[tuple, str] = {}
    for el in elements:
        for e in el["evidence"]:
            k = (e["file"], e.get("locator"))
            if k not in reg:
                reg[k] = f"E-{len(reg) + 1:03d}"
            e["id"] = reg[k]

    model = {"loop": paths.loop, "system_lookup": lookup, "elements": elements, "flags": flags,
             "id_state": ids.state()}
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

    # link tables: an entity that only joins two others (many-to-many)
    for r in by_kind["relationship"]:
        if r["properties"].get("cardinality") == "many-to-many" and (ent := ents.get(norm(r["properties"].get("via", "")))):
            ent["properties"]["link_entity"] = True
            ent["properties"]["links"] = [r["properties"]["from"], r["properties"]["to"]]

    # recorded synonym decisions (from sme-answer sources)
    confirmed_by_concept = {}
    for c in by_kind["concept"]:
        no = {norm(x) for x in c["properties"].get("not_synonyms", [])}
        if no:
            dropped = [a for a in c["aliases"] if norm(a) in no]
            c["aliases"] = [a for a in c["aliases"] if norm(a) not in no]
            for a in dropped:
                if ent := ents.get(norm(a)):
                    ent["properties"]["separate_from"] = c["id"]
                    ent["properties"]["decision"] = f"not the same as {c['name']} (recorded SME answer)"
                trace.emit("D. Steward reconciles", "Ontology Steward", "synonym decision applied",
                           f"'{a}' is not a synonym of {c['name']}: removed from its synonyms, separate concept kept")
        confirmed_by_concept[c["id"]] = {norm(x) for x in c["properties"].get("confirmed_synonyms", [])}

    def confirm_link(ent, c):
        if "realises" not in ent["properties"]:
            ent["properties"]["realises"] = c["id"]
        c["properties"].setdefault("also_realised_by", [])
        if ent["id"] not in c["properties"]["also_realised_by"]:
            c["properties"]["also_realised_by"].append(ent["id"])
        trace.emit("D. Steward reconciles", "Ontology Steward", "synonym decision applied",
                   f"'{ent['name']}' ({ent['properties'].get('system', '?')}) confirmed as the same concept as {c['name']}")

    # homonym risk: a concept synonym that names a different entity
    for c in by_kind["concept"]:
        for alias in c["aliases"]:
            ent = ents.get(norm(alias))
            if ent and norm(alias) in confirmed_by_concept.get(c["id"], set()):
                confirm_link(ent, c)
                continue
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
            if e2["kind"] == "concept" and n1 in confirmed_by_concept.get(e2["id"], set()):
                if e1["properties"].get("realises") != e2["id"]:
                    confirm_link(e1, e2)
                continue
            if e1["properties"].get("realises"):
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
        if any(k in c["properties"] for k in ("realised_by", "also_realised_by", "defines_identifier")):
            continue
        if any(c["id"] in f["affects"] for f in flags):
            continue
        hint = next((s["name"] for s in by_kind["system"]
                     if any(len(t) >= 3 and t in sysnorm(s["name"]) for t in tokens(c["name"]))), None)
        flags.append({"type": "unrealised_concept", "affects": [c["id"]],
                      "detail": f"No entity found for '{c['name']}'." + (f" Possible home: {hint}." if hint else ""),
                      **({"hint_system": hint} if hint else {})})
    # entities referenced in code but with no structure in the evidence
    for e in by_kind["entity"]:
        if e["properties"].get("implied_by") and not e["properties"].get("attribute_ids") \
                and not any(e["id"] in f["affects"] for f in flags):
            flags.append({"type": "implied_entity", "affects": [e["id"]],
                          "detail": f"'{e['name']}' is referenced by {e['properties']['implied_by']}, "
                                    f"but its structure is not in the evidence."})
    # systems with no role
    for s in by_kind["system"]:
        if not s["properties"].get("roles"):
            flags.append({"type": "system_without_role", "affects": [s["id"]],
                          "detail": f"'{s['name']}' appears in {len({e['file'] for e in s['evidence']})} source(s) "
                                    f"but nothing says what it does."})
    for f in flags:
        trace.emit("D. Steward reconciles", "Ontology Steward", "flagged", f"{f['type']}: {f['detail']}")
    return flags

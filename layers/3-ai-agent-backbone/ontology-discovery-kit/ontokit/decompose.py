"""Stage F2 — Domain decomposition: split a monolith's ontology into business-owned domains.

Runs only when the discovery root has a target_domains.yaml. The rule, from the
business perspective:

    The domain whose business capability creates or changes data owns it.
    Other domains read it through the owner's business services, or react to
    the owner's events. They never join the owner's tables.

Evidence, strongest first:
  1. who WRITES each table or column (calculations from batch jobs and stored procedures)
  2. which capability a calculation implements, and which team owns that capability
  3. business vocabulary (each domain's keywords), only where nothing writes the data

What it produces (stored in model.json under "decomposition", and as files on publish):
  * a domain for every element, with the basis for the decision
  * split candidates: a column written by another domain's capability that creates it
    (e.g. the NI Number written into the person table by NI allocation)
  * cross-domain writes: another domain changing data it does not own. The
    recommendation is an event from the writer that the owner reacts to
  * cross-domain reads: dependencies that become query services on the access layer
  * a business-service catalogue per domain (commands, queries, events)
Disputed or unassignable items become flags, and so unknowns for the named owners.
The stage recommends. Domain owners and the Enterprise Architecture Authority decide.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from .common import LoopPaths, Trace, camel, human, norm, pascal, read_json, tokens, write_json

ST = "F2. Decompose"


def load_targets(root: Path) -> dict | None:
    fp = root / "target_domains.yaml"
    return yaml.safe_load(fp.read_text(encoding="utf-8")) if fp.exists() else None


def _kw_score(text: str, keywords: list[str]) -> int:
    toks = set(tokens(text))
    score = 0
    for kw in keywords:
        kt = tokens(kw)
        if kt and all(t in toks for t in kt):
            score += len(kt)
    return score


def _group(xwrites: list[dict]) -> dict:
    out = defaultdict(list)
    for x in xwrites:
        out[(x["writer"], x["event"])].append(x)
    return out


def decompose(paths: LoopPaths, trace: Trace) -> dict | None:
    cfg = load_targets(paths.root)
    if not cfg:
        return None
    model = read_json(paths.work / "model.json")
    els = model["elements"]
    by_id = {e["id"]: e for e in els}
    by_kind = defaultdict(list)
    for e in els:
        by_kind[e["kind"]].append(e)
    domains = {d["key"]: d for d in cfg["domains"]}
    team2dom = {norm(t): d["key"] for d in cfg["domains"] for t in d.get("owning_teams", [])}
    dname = lambda k: domains[k]["name"] if k in domains else "Unassigned"

    def by_keywords(text: str) -> tuple[str | None, dict]:
        scores = {k: _kw_score(text, d.get("keywords", [])) for k, d in domains.items()}
        best = max(scores.values()) if scores else 0
        tops = [k for k, v in scores.items() if v == best and v > 0]
        return (tops[0] if len(tops) == 1 else None), scores

    def assign(e: dict, dom: str | None, basis: str) -> None:
        e["properties"]["domain"] = dom
        e["properties"]["domain_basis"] = basis

    # 1. Capabilities: the capability map names the owning team
    caps = {norm(c["name"]): c for c in by_kind["capability"]}
    for c in by_kind["capability"]:
        dom = team2dom.get(norm(c["properties"].get("owner_team", "")))
        assign(c, dom, f"capability map: owned by {c['properties'].get('owner_team', '?')}")

    # 2. Calculations: owned by the team that runs them, or by the capability they implement
    for calc in by_kind["calculation"]:
        p = calc["properties"]
        cap = caps.get(norm(p.get("capability", "")))
        dom = team2dom.get(norm(p.get("owner_team", ""))) or (cap and cap["properties"].get("domain"))
        assign(calc, dom, f"run by {p.get('owner_team') or '?'}" + (f"; implements {cap['name']}" if cap else ""))
        if cap:
            p["capability_id"] = cap["id"]

    # 3. Entities: who writes them
    ents = [e for e in by_kind["entity"]]
    by_table = {e["properties"]["physical"].upper(): e for e in ents if e["properties"].get("physical")}
    writes = defaultdict(lambda: defaultdict(list))      # entity id -> domain -> [calc ids]
    reads = defaultdict(lambda: defaultdict(list))
    col_writes = defaultdict(lambda: defaultdict(list))  # (entity id, COLUMN) -> domain -> [calc ids]
    for calc in by_kind["calculation"]:
        dom, p = calc["properties"].get("domain"), calc["properties"]
        if not dom:
            continue
        for t in p.get("writes", []):
            if e := by_table.get(t.upper()):
                writes[e["id"]][dom].append(calc["id"])
        for t in p.get("reads", []):
            if e := by_table.get(t.upper()):
                reads[e["id"]][dom].append(calc["id"])
        for tc in p.get("writes_columns", []):
            t, _, col = tc.partition(".")
            if e := by_table.get(t.upper()):
                col_writes[(e["id"], col.upper())][dom].append(calc["id"])

    flags, splits, xwrites = [], [], []
    for e in ents:
        if e["origin"] == "assumed":
            continue
        text = " ".join([human(e["name"]), e["properties"].get("physical", "")])
        ws = writes.get(e["id"], {})
        if len(ws) == 1:
            dom = next(iter(ws))
            assign(e, dom, f"only {dname(dom)} capabilities change it")
        elif len(ws) > 1:
            kw_dom, scores = by_keywords(text)
            cands = sorted(ws, key=lambda k: (-scores.get(k, 0), -len(ws[k])))
            dom = kw_dom if kw_dom in ws else (cands[0] if scores.get(cands[0], 0) > scores.get(cands[1], 0) else None)
            if dom:
                assign(e, dom, f"changed by {', '.join(dname(k) for k in ws)}; {dname(dom)} creates it")
            else:
                assign(e, None, "changed by several domains; owner unclear")
                flags.append({"type": "contested_ownership", "affects": [e["id"]], "domains": sorted(ws),
                              "detail": f"'{e['name']}' is changed by {', '.join(dname(k) for k in ws)}, and nothing shows which one creates it."})
        else:
            dom, _ = by_keywords(text)
            if dom:
                assign(e, dom, "no capability writes it; assigned by business vocabulary")
            else:
                assign(e, None, "no write evidence and no matching vocabulary")
                flags.append({"type": "unassigned_domain", "affects": [e["id"]],
                              "detail": f"Nothing shows which business capability creates '{e['name']}'."})

        # non-owner writers: a column the writer's capability creates (split) or a cross-domain write (event)
        owner = e["properties"].get("domain")
        if not owner:
            continue
        for wdom, calc_ids in ws.items():
            if wdom == owner:
                continue
            for cid in calc_ids:
                calc = by_id[cid]
                cols = [tc.partition(".")[2] for tc in calc["properties"].get("writes_columns", [])
                        if tc.partition(".")[0].upper() == e["properties"]["physical"].upper()]
                cap_name = by_id.get(calc["properties"].get("capability_id", ""), {}).get("name", calc["properties"].get("capability", ""))
                cap_toks = set(tokens(cap_name))
                created = [c for c in cols if set(tokens(c)) & cap_toks - {"customer", "record"}]
                if created:
                    for col in created:
                        attr = next((a for a in by_kind["attribute"] if a["properties"].get("entity_id") == e["id"]
                                     and a["properties"].get("physical", "").upper() == col.upper()), None)
                        splits.append({"entity": e["name"], "entity_id": e["id"], "column": col,
                                       "attribute": (attr["properties"].get("description") if attr else None) or human(col), "attribute_id": attr and attr["id"],
                                       "from": owner, "to": wdom, "calculation": calc["name"], "capability": cap_name})
                        if attr:
                            assign(attr, wdom, f"created by {cap_name} ({dname(wdom)}); stored in {e['name']} today")
                            attr["properties"]["split_from"] = owner
                        flags.append({"type": "column_split", "affects": [e["id"]] + ([attr["id"]] if attr else []),
                                      "from": owner, "to": wdom,
                                      "detail": f"{col} in {e['properties']['physical']} is created by {cap_name} ({dname(wdom)}), "
                                                f"but the table belongs to {dname(owner)}."})
                        trace.emit(ST, "Ontology Steward", "split candidate",
                                   f"{e['name']}.{col}: created by {cap_name} → move to {dname(wdom)}; {dname(owner)} keeps a reference")
                else:
                    trig = next((by_table[t.upper()] for t in calc["properties"].get("reads", []) if t.upper() in by_table), None)
                    event = (pascal(trig["name"]) if trig else pascal(cap_name)) + "Changed"
                    xwrites.append({"entity": e["name"], "entity_id": e["id"], "owner": owner, "writer": wdom,
                                    "calculation": calc["name"], "capability": cap_name, "columns": cols, "event": event,
                                    "calc_id": cid})
                    trace.emit(ST, "Ontology Steward", "cross-domain write",
                               f"{dname(wdom)} changes {e['name']} ({dname(owner)}) via {calc['name']} → event {event}")

    # one question per recommended event, covering every write it replaces
    for (wdom, event), group in sorted(_group(xwrites).items()):
        owners = sorted({x["owner"] for x in group})
        flags.append({"type": "cross_domain_write", "affects": sorted({x["entity_id"] for x in group} | {x["calc_id"] for x in group}),
                      "owner": owners, "writer": wdom, "event": event,
                      "detail": f"{group[0]['capability']} ({dname(wdom)}) changes "
                                + ", ".join(f"{x['entity']} ({dname(x['owner'])})" for x in group)
                                + f" directly. Recommendation: {dname(wdom)} publishes {event}; "
                                + ", ".join(dname(o) for o in owners) + " react with their own services."})

    # 4. Attributes, identifiers, taxonomies, concepts, rules, relationships
    ent_by_id = {e["id"]: e for e in ents}
    for a in by_kind["attribute"]:
        if a["properties"].get("split_from"):
            continue
        ent = ent_by_id.get(a["properties"].get("entity_id", ""))
        assign(a, ent and ent["properties"].get("domain"), "belongs to its entity")
    attr_by_name = defaultdict(list)
    for a in by_kind["attribute"]:
        attr_by_name[norm(a["properties"].get("description") or a["properties"].get("attribute", ""))].append(a)
    for i in by_kind["identifier"]:
        ent = ent_by_id.get(i["properties"].get("entity_id", ""))
        moved = next((a for a in attr_by_name.get(norm(i["name"]), []) if a["properties"].get("split_from")), None)
        if moved:
            assign(i, moved["properties"]["domain"], f"its attribute moves to {dname(moved['properties']['domain'])}")
        elif ent and ent["properties"].get("domain"):
            assign(i, ent["properties"]["domain"], f"identifies {ent['name']}")
        else:
            dom, _ = by_keywords(i["name"])
            assign(i, dom, "business vocabulary")
    for t in by_kind["taxonomy"]:
        a = next((a for a in by_kind["attribute"] if a["properties"].get("range") == t["name"] and a["properties"].get("domain")), None)
        if a:
            assign(t, a["properties"]["domain"], f"used by {a['name']}")
        else:
            dom, _ = by_keywords(human(t["name"]))
            assign(t, dom, "business vocabulary")
    for c in by_kind["concept"]:
        ent = by_id.get(c["properties"].get("realised_by", ""))
        if ent and ent["properties"].get("domain"):
            assign(c, ent["properties"]["domain"], f"realised by {ent['name']}")
        else:
            dom, _ = by_keywords(c["name"] + " " + c.get("definition", ""))
            assign(c, dom, "business vocabulary")
    for r in by_kind["rule"]:
        dom, _ = by_keywords(r["name"])
        assign(r, dom, "business vocabulary")

    deps = defaultdict(lambda: {"entities": set(), "via": set()})   # (consumer, provider) -> detail
    for r in by_kind["relationship"]:
        if r["origin"] == "assumed":
            continue
        fe = next((e for e in ents if e["name"] == r["properties"].get("from")), None)
        te = next((e for e in ents if e["name"] == r["properties"].get("to")), None)
        fd, td = fe and fe["properties"].get("domain"), te and te["properties"].get("domain")
        assign(r, fd, "belongs to its source entity")
        if fd and td and fd != td:
            r["properties"]["cross_domain"] = True
            deps[(fd, td)]["entities"].add(te["name"])
            deps[(fd, td)]["via"].add(f"{r['name']} (reference)")
    for eid, doms in reads.items():
        owner = ent_by_id[eid]["properties"].get("domain")
        for rdom, cids in doms.items():
            if owner and rdom != owner:
                deps[(rdom, owner)]["entities"].add(ent_by_id[eid]["name"])
                deps[(rdom, owner)]["via"].update(by_id[c]["name"] for c in cids)
    for s in splits:
        deps[(s["from"], s["to"])]["entities"].add(s["attribute"])
        deps[(s["from"], s["to"])]["via"].add(f"{s['entity']}.{s['column']} (moved)")

    # 5. Business services per domain (the access layer)
    services = defaultdict(list)
    for c in by_kind["capability"]:
        dom = c["properties"].get("domain")
        if not dom:
            continue
        impl = [k for k in by_kind["calculation"] if k["properties"].get("capability_id") == c["id"]]
        w = sorted({ent_by_id[eid]["name"] for k in impl for t in k["properties"].get("writes", [])
                    for eid in [by_table.get(t.upper(), {}).get("id")] if eid and ent_by_id[eid]["properties"].get("domain") == dom})
        services[dom].append({"name": c["name"], "type": "command", "capability": c["id"], "grade": c["grade"],
                              "calculations": [k["name"] for k in impl], "changes": w, "consumers": []})
    for (cons, prov), dd in sorted(deps.items()):
        for ent_name in sorted(dd["entities"]):
            svc_name = f"Get {human(ent_name)}"
            svc = next((s for s in services[prov] if s["name"] == svc_name), None)
            if not svc:
                svc = {"name": svc_name, "type": "query", "returns": ent_name, "grade": None, "consumers": []}
                services[prov].append(svc)
            if cons not in svc["consumers"]:
                svc["consumers"].append(cons)
    for x in xwrites:
        ev = next((s for s in services[x["writer"]] if s["name"] == x["event"]), None)
        if not ev:
            ev = {"name": x["event"], "type": "event", "replaces": [], "consumers": []}
            services[x["writer"]].append(ev)
        if x["owner"] not in ev["consumers"]:
            ev["consumers"].append(x["owner"])
        ev["replaces"].append(f"{x['calculation']} writing {x['entity']}")

    # 6. Summary and flags
    summary = {}
    for k in domains:
        mine = [e for e in els if e["properties"].get("domain") == k and e["origin"] != "assumed"]
        summary[k] = {"name": dname(k), "owner": domains[k].get("owner"),
                      "counts": dict(Counter(e["kind"] for e in mine)),
                      "grades": dict(Counter(e["grade"] for e in mine)),
                      "entities": sorted(e["name"] for e in mine if e["kind"] == "entity"),
                      "services": len(services[k])}
    unassigned = [e["id"] for e in els if e["kind"] in ("entity", "attribute", "calculation", "capability")
                  and e["origin"] != "assumed" and not e["properties"].get("domain")]
    deps_out = [{"consumer": c, "provider": p, "entities": sorted(v["entities"]), "via": sorted(v["via"])}
                for (c, p), v in sorted(deps.items())]
    model["decomposition"] = {"monolith": cfg.get("monolith"), "domains": [{"key": k, **{kk: vv for kk, vv in d.items()
                              if kk in ("name", "owner")}} for k, d in domains.items()],
                              "summary": summary, "splits": splits, "cross_domain_writes": xwrites,
                              "dependencies": deps_out, "services": {k: services[k] for k in domains},
                              "unassigned": unassigned}
    model["flags"].extend(flags)
    write_json(paths.work / "model.json", model)
    for k, s in summary.items():
        trace.emit(ST, "Ontology Steward", f"domain {s['name']}",
                   f"{s['counts'].get('entity', 0)} entities, {s['counts'].get('attribute', 0)} attributes, "
                   f"{s['counts'].get('calculation', 0)} calculations, {s['services']} services", domain=k, **s)
    trace.emit(ST, "Ontology Steward", "decomposition proposed",
               f"{len(domains)} domains; {len(deps_out)} cross-domain dependencies; {len(splits)} split candidates; "
               f"{len(xwrites)} cross-domain writes → events; {len(unassigned)} unassigned",
               dependencies=len(deps_out), splits=len(splits), events=len(xwrites), unassigned=len(unassigned))
    return model["decomposition"]


# ------------------------------------------------------------------ outputs

SQL2JSON = [(r"^(CHAR|VARCHAR)", "string"), (r"^(INTEGER|SMALLINT|BIGINT)", "integer"),
            (r"^(DECIMAL|NUMERIC)", "number"), (r"^DATE$", "string:date"), (r"^TIMESTAMP", "string:date-time")]


def _jtype(dt: str) -> dict:
    for rx, t in SQL2JSON:
        if re.match(rx, dt or "", re.I):
            typ, _, fmt = t.partition(":")
            return {"type": typ, **({"format": fmt} if fmt else {})}
    return {"type": "string"}


def _kebab(s: str) -> str:
    return "-".join(tokens(s))


def publish_outputs(paths: LoopPaths, trace: Trace) -> None:
    model = read_json(paths.work / "model.json")
    dec = model.get("decomposition")
    if not dec:
        return
    out = paths.outputs / "decomposition"
    (out / "domains").mkdir(parents=True, exist_ok=True)
    (out / "services").mkdir(parents=True, exist_ok=True)
    els = model["elements"]
    by_id = {e["id"]: e for e in els}
    names = {d["key"]: d["name"] for d in dec["domains"]}
    ann = lambda e: {"grade": e["grade"], "domain_basis": e["properties"].get("domain_basis", ""),
                     "evidence": ",".join(x["id"] for x in e["evidence"]) or "none"}

    mapping = ["monolith_table,monolith_column,target_domain,target_entity,target_attribute,grade,note"]
    for d in dec["domains"]:
        k = d["key"]
        classes, enums = {}, {}
        for e in els:
            if e["kind"] == "entity" and e["properties"].get("domain") == k and e["origin"] != "assumed":
                attrs = {}
                for aid in e["properties"].get("attribute_ids", []):
                    a = by_id[aid]
                    p = a["properties"]
                    spec = {"annotations": ann(a)}
                    if p.get("description"):
                        spec["description"] = p["description"]
                    if p.get("domain") != k:
                        spec["annotations"]["reference_to"] = f"{p.get('domain')}:{a['name']}"
                        spec["description"] = f"Reference only. Owned by {names.get(p.get('domain'), '?')}."
                    attrs[p["attribute"]] = spec
                    note = f"moves to {names.get(p.get('domain'))}" if p.get("split_from") else ""
                    mapping.append(f"{e['properties'].get('physical', '')},{p.get('physical', '')},{names.get(p.get('domain'), '')},"
                                   f"{e['name']},{p['attribute']},{a['grade']},{note}")
                for r in els:
                    if r["kind"] == "relationship" and r["properties"].get("from") == e["name"] and r["origin"] != "assumed":
                        tgt = next((x for x in els if x["kind"] == "entity" and x["name"] == r["properties"]["to"]), None)
                        if tgt:
                            slot = camel(tgt["name"]) + "Ref"
                            attrs.setdefault(slot, {"range": tgt["name"] if tgt["properties"].get("domain") == k else "string",
                                                    "annotations": {**ann(r), **({"reference_to": f"{tgt['properties'].get('domain')}:{tgt['name']}"}
                                                                                 if tgt["properties"].get("domain") != k else {})}})
                classes[e["name"]] = {"description": f"Owned by {d['name']}. {e['properties'].get('domain_basis', '')}",
                                      "annotations": ann(e), "attributes": attrs}
            if e["kind"] == "taxonomy" and e["properties"].get("domain") == k:
                vals = e["properties"].get("values") or sorted({v for c in e["conflicts"] for x in c["variants"] for v in x["value"]})
                enums[e["name"]] = {"permissible_values": {v: {} for v in vals}, "annotations": ann(e)}
        moved_in = [by_id[s["attribute_id"]] for s in dec["splits"] if s["to"] == k and s.get("attribute_id")]
        for a in moved_in:
            cls = pascal(a["properties"].get("description") or a["name"]) + "Assignment"
            classes.setdefault(cls, {"description": f"Moved from {names.get(a['properties'].get('split_from'))}'s "
                                                    f"{a['properties'].get('entity')} table. {a['properties'].get('domain_basis')}",
                                     "annotations": ann(a), "attributes": {a["properties"]["attribute"]: {"identifier": True},
                                                                            "personRef": {"annotations": {"reference_to": "customer:Person"}}}})
        linkml = {"id": f"https://example.org/{paths.loop}/{k}", "name": f"{k}_domain",
                  "description": f"{d['name']} domain ontology, carved out of {dec['monolith']}. Owner: {d.get('owner')}.",
                  "prefixes": {"linkml": "https://w3id.org/linkml/"}, "default_range": "string", "imports": ["linkml:types"],
                  "classes": classes, "enums": enums}
        (out / "domains" / f"{k}.yaml").write_text("# Generated by ontokit decompose. Recommendation for owner review.\n"
                                                   + yaml.safe_dump(linkml, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")

        # OpenAPI stub for the domain's business services
        paths_, schemas, events = {}, {}, []
        for c, spec in classes.items():
            schemas[c] = {"type": "object", "properties": {
                a: (_jtype(by_id[aid]["properties"].get("data_type", "")) if (aid := next((x for x in by_id[e2["id"]]["properties"].get("attribute_ids", [])
                                                                                          if by_id[x]["properties"]["attribute"] == a), None)) else {"type": "string"})
                for a in spec.get("attributes", {})} if (e2 := next((x for x in els if x["kind"] == "entity" and x["name"] == c), None))
                else {a: {"type": "string"} for a in spec.get("attributes", {})}}
        for s in dec["services"][k]:
            if s["type"] == "command":
                paths_[f"/{_kebab(s['name'])}"] = {"post": {"summary": s["name"], "operationId": camel(s["name"]),
                                                            "description": f"Business service. Replaces {', '.join(s.get('calculations', [])) or 'manual process'} in {dec['monolith']}.",
                                                            "responses": {"200": {"description": "Done"}}}}
            elif s["type"] == "query":
                ref = s["returns"] if s["returns"] in schemas else None
                paths_[f"/{_kebab(s['returns'])}/{{id}}"] = {"get": {
                    "summary": s["name"], "operationId": camel(s["name"]),
                    "description": "Used by: " + ", ".join(names[c] for c in s["consumers"]),
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {"200": {"description": s["returns"], **({"content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{ref}"}}}} if ref else {})}}}}
            else:
                events.append({"name": s["name"], "consumers": [names[c] for c in s["consumers"]], "replaces": s.get("replaces", [])})
        api = {"openapi": "3.0.3", "info": {"title": f"{d['name']} business services", "version": "0.1.0",
                                             "description": f"Ontology-based access layer for the {d['name']} domain. Generated stub for review."},
               "paths": paths_, "components": {"schemas": schemas}, **({"x-events": events} if events else {})}
        (out / "services" / f"{k}.openapi.yaml").write_text(yaml.safe_dump(api, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")

    (out / "source-to-target.csv").write_text("\n".join(mapping) + "\n", encoding="utf-8")
    write_json(out / "decomposition.json", dec)

    # Report
    R = [f"# Decomposition of {dec['monolith']} — {paths.loop}", "",
         "Rule: the domain whose business capability creates or changes data owns it. Other domains use the owner's services or events.", "",
         "| Domain | Owner | Entities | Attributes | Calculations | Capabilities | Services | Grades |", "|---|---|---|---|---|---|---|---|"]
    for k, s in dec["summary"].items():
        c = s["counts"]
        R.append(f"| **{s['name']}** | {s['owner']} | {c.get('entity', 0)} | {c.get('attribute', 0)} | {c.get('calculation', 0)} | "
                 f"{c.get('capability', 0)} | {s['services']} | " + " ".join(f"{g}:{s['grades'].get(g, 0)}" for g in "ABCDX") + " |")
    R += ["", "## Target picture", "", "```mermaid", "flowchart LR"]
    for d in dec["domains"]:
        R.append(f"  subgraph {d['key']}[\"{d['name']}\"]")
        for i, s in enumerate(dec["services"][d["key"]]):
            shape = ("[[\"", "\"]]") if s["type"] == "event" else ("([\"", "\"])") if s["type"] == "query" else ("[\"", "\"]")
            R.append(f"    {d['key']}_{i}{shape[0]}{s['name']}{shape[1]}")
        R.append("  end")
    for d in dec["domains"]:
        for i, s in enumerate(dec["services"][d["key"]]):
            for c in s.get("consumers", []):
                R.append(f"  {c} {'-.->' if s['type'] == 'event' else '-->'} {d['key']}_{i}")
    R += ["```", "", "## Entity ownership", "", "| Entity | Monolith table | Domain | Basis | Grade |", "|---|---|---|---|---|"]
    for e in els:
        if e["kind"] == "entity" and e["origin"] != "assumed":
            R.append(f"| {e['name']} | {e['properties'].get('physical', '')} | {names.get(e['properties'].get('domain'), '**unassigned**')} | "
                     f"{e['properties'].get('domain_basis', '')} | {e['grade']} |")
    R += ["", "## Split candidates (columns that move to another domain)", ""]
    R += [f"- **{s['entity']}.{s['column']}** → {names[s['to']]}: created by *{s['capability']}* ({s['calculation']}). "
          f"{names[s['from']]} keeps a reference." for s in dec["splits"]] or ["- none"]
    R += ["", "## Cross-domain writes → events", ""]
    R += [f"- **{x['event']}** published by {names[x['writer']]}, consumed by {names[x['owner']]}: replaces {x['calculation']} "
          f"({x['capability']}) changing {x['entity']} directly." for x in dec["cross_domain_writes"]] or ["- none"]
    R += ["", "## Cross-domain dependencies → query services", "", "| Consumer | Provider | Data | Today via |", "|---|---|---|---|"]
    for dd in dec["dependencies"]:
        R.append(f"| {names[dd['consumer']]} | {names[dd['provider']]} | {', '.join(dd['entities'])} | {', '.join(dd['via'])} |")
    R += ["", "## Business services (access layer)", ""]
    for d in dec["domains"]:
        R += [f"### {d['name']}", "", "| Service | Type | Used by | Replaces / implements |", "|---|---|---|---|"]
        for s in dec["services"][d["key"]]:
            R.append(f"| {s['name']} | {s['type']} | {', '.join(names[c] for c in s.get('consumers', [])) or '—'} | "
                     f"{', '.join(s.get('calculations', []) or s.get('replaces', [])) or '—'} |")
        R.append("")
    R += ["Files: `domains/<domain>.yaml` (LinkML), `services/<domain>.openapi.yaml`, `source-to-target.csv`, `decomposition.json`."]
    (out / "decomposition-report.md").write_text("\n".join(R) + "\n", encoding="utf-8")
    trace.emit("K. Publish", "Publisher", "decomposition written",
               f"{len(dec['domains'])} domain ontologies, {len(dec['domains'])} service contracts, source-to-target mapping")

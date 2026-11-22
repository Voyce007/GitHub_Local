"""Stage J — Publish the loop's deliverables to discovery/outputs/<loop>/.

as-is-ontology.yaml   LinkML-flavoured model (classes, attributes, enums) with grade/evidence annotations
elements.json         every element with grade, status, evidence ids
evidence-register.json every cited source line, with the elements it supports
system-inventory.md   candidate systems, aliases, roles, system-to-entity map, flows
glossary.md           concepts, definitions, synonyms, grades
unknowns-register.md  questions and evidence requests (+ jira-issues.json, ready for the MCP create_jira_issue tool)
gate-report.md        automated gate results and human-gate decisions
standins/*.sql        stand-in schemas for the PoC, one per data-holding system
summary.md            one-page run summary
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

import yaml

from . import approvals as appr
from .common import LoopPaths, Trace, read_json, write_json

STATUS = {"approve": "approved", "approve-provisional": "approved (provisional)", "reject": "rejected",
          "defer": "deferred", "note-assumption": "assumption (noted)", "pending": "proposed"}
JAVA_SQL = {"String": "VARCHAR(255)", "LocalDate": "DATE", "BigDecimal": "NUMERIC(18,2)", "int": "INTEGER",
            "Integer": "INTEGER", "long": "BIGINT", "Long": "BIGINT", "boolean": "BOOLEAN", "Instant": "TIMESTAMP"}


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def publish(paths: LoopPaths, trace: Trace) -> None:
    model = read_json(paths.work / "model.json")
    index = read_json(paths.work / "sources.json")
    unknowns = read_json(paths.work / "unknowns.json")
    gates = read_json(paths.work / "gates.json")
    decisions = appr.load(paths)
    out = paths.outputs
    out.mkdir(parents=True, exist_ok=True)
    els = model["elements"]
    by_id = {e["id"]: e for e in els}
    by_kind = defaultdict(list)
    for e in els:
        d = decisions.get(e["id"])
        e["status"] = STATUS[d["decision"]] if d else "proposed"
        if d and d.get("mode") == "simulated":
            e["status"] += " — simulated"
        e["open_unknowns"] = [u["id"] for u in unknowns if e["id"] in u["affects"]]
        by_kind[e["kind"]].append(e)

    write_json(out / "elements.json", els)

    # Evidence register
    reg = {}
    for e in els:
        for ev in e["evidence"]:
            r = reg.setdefault(ev["id"], {"id": ev["id"], "file": ev["file"], "locator": ev.get("locator"),
                                          "quote": ev["quote"], "provenance": index["sources"][ev["file"]]["provenance"],
                                          "stale": index["sources"][ev["file"]]["stale"], "supports": []})
            r["supports"].append(e["id"])
    write_json(out / "evidence-register.json", sorted(reg.values(), key=lambda r: r["id"]))

    # LinkML-flavoured model
    ann = lambda e: {"grade": e["grade"], "status": e["status"], "origin": e["origin"],
                     "evidence": ",".join(x["id"] for x in e["evidence"]) or "none",
                     **({"open_unknowns": ",".join(e["open_unknowns"])} if e["open_unknowns"] else {})}
    classes, enums = {}, {}
    for t in by_kind["taxonomy"]:
        if t["conflicts"]:
            vals = {}
            for c in t["conflicts"]:
                for v in c["variants"]:
                    for x in v["value"]:
                        vals.setdefault(x, {"annotations": {"seen_in": []}})["annotations"]["seen_in"] += v["files"]
            for v in vals.values():
                v["annotations"]["seen_in"] = ",".join(sorted(set(v["annotations"]["seen_in"])))
        else:
            vals = {x: {} for x in t["properties"].get("values", [])}
        enums[t["name"]] = {"description": f"Grade {t['grade']}: {t['grade_reason']}", "permissible_values": vals,
                            "annotations": ann(t)}
    id_attr = {(i["properties"].get("entity_id"), i["properties"].get("attribute")): i for i in by_kind["identifier"]}
    for e in by_kind["entity"]:
        concept = by_id.get(e["properties"].get("realises", ""))
        attrs = {}
        for aid in e["properties"].get("attribute_ids", []):
            a = by_id[aid]
            spec = {"annotations": ann(a)}
            if a["properties"].get("description"):
                spec["description"] = a["properties"]["description"]
            if (rng := a["properties"].get("range")) and rng in enums:
                spec["range"] = rng
            if (e["id"], a["properties"]["attribute"]) in id_attr:
                spec["identifier"] = True
            attrs[a["properties"]["attribute"]] = spec
        for r in by_kind["relationship"]:
            if r["properties"].get("from") == e["name"] and r["origin"] != "assumed":
                tgt = r["properties"]["to"]
                attrs.setdefault(re.sub(r"^.", lambda m: m.group().lower(), tgt) + ("s" if "many" in r["properties"].get("cardinality", "").split("-")[-1] else ""),
                                 {"range": tgt, "annotations": {**ann(r), "cardinality": r["properties"].get("cardinality", "")}})
        cls = {"annotations": {**ann(e), **({"system": e["properties"]["system"]} if e["properties"].get("system") else {}),
                               **({"reference_domain": e["properties"]["domain"]} if e["properties"].get("domain") else {})}}
        if concept and concept["definition"]:
            cls["description"] = concept["definition"]
        if attrs:
            cls["attributes"] = attrs
        classes[e["name"]] = cls
    linkml = {"id": f"https://example.org/ontology/{paths.loop}/as-is", "name": f"as_is_{paths.loop.replace('-', '_')}",
              "description": f"As-is ontology hypothesis from evidence batch {paths.loop}. Grades and status are annotations; "
                             f"nothing here is approved for production mapping.",
              "prefixes": {"linkml": "https://w3id.org/linkml/"}, "default_range": "string",
              "imports": ["linkml:types"], "classes": classes, "enums": enums}
    (out / "as-is-ontology.yaml").write_text(
        "# Generated by ontokit. Validate with: linkml-lint as-is-ontology.yaml (pip install linkml)\n"
        + yaml.safe_dump(linkml, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")

    # System inventory
    lines = [f"# Candidate system inventory — {paths.loop}", "",
             "Hypothesis built from documents and example code. Every row needs confirmation.", "",
             "| ID | System | Aliases | Roles | Grade | Sources | Entities | Open unknowns |", "|---|---|---|---|---|---|---|---|"]
    for s in sorted(by_kind["system"], key=lambda s: s["name"].lower()):
        ents = [e["name"] for e in by_kind["entity"] if e["properties"].get("system") == s["name"]]
        lines.append(f"| {s['id']} | **{s['name']}** | {', '.join(s['aliases']) or '—'} | "
                     f"{'; '.join(s['properties'].get('roles', [])) or '—'} | {s['grade']} | "
                     f"{len({e['file'] for e in s['evidence']})} | {', '.join(ents) or '—'} | {', '.join(s['open_unknowns']) or '—'} |")
    lines += ["", "## Data flows", "", "| From | To | Labels | Grade |", "|---|---|---|---|"]
    for f in by_kind["flow"]:
        lab = f["properties"].get("label", "")
        lines.append(f"| {f['properties']['source']} | {f['properties']['target']} | {lab} | {f['grade']} |")
    lines += ["", "## Interfaces", "", "| ID | Mechanism | Source → Target | Payload | Grade |", "|---|---|---|---|---|"]
    for i in by_kind["interface"]:
        p = i["properties"]
        lines.append(f"| {i['name']} | {p.get('mechanism', '?')} | {p.get('source', '?')} → {p.get('target', '?')} | {p.get('payload', '')} | {i['grade']} |")
    (out / "system-inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Glossary
    g = [f"# Business glossary (candidate) — {paths.loop}", "",
         "| ID | Term | Definition | Synonyms | Realised by | Grade | Status |", "|---|---|---|---|---|---|---|"]
    for c in sorted(by_kind["concept"], key=lambda c: c["name"]):
        rb = by_id.get(c["properties"].get("realised_by", "") or c["properties"].get("defines_identifier", ""), {}).get("name", "—")
        g.append(f"| {c['id']} | **{c['name']}** | {c['definition']} | {', '.join(c['aliases']) or '—'} | {rb} | {c['grade']} | {c['status']} |")
    g += ["", "## Classifications", "", "| ID | Taxonomy | Values | Grade |", "|---|---|---|---|"]
    for t in by_kind["taxonomy"]:
        vals = t["properties"].get("values") or " / ".join(f"{{{', '.join(v['value'])}}}" for c in t["conflicts"] for v in c["variants"])
        g.append(f"| {t['id']} | {t['name']} | {', '.join(vals) if isinstance(vals, list) else vals} | {t['grade']} |")
    g += ["", "## Business rules", "", "| ID | Rule | Grade | Source |", "|---|---|---|---|"]
    for r in by_kind["rule"]:
        g.append(f"| {r['id']} | {r['name']} | {r['grade']} | {', '.join(sorted({e['file'] for e in r['evidence']}))} |")
    (out / "glossary.md").write_text("\n".join(g) + "\n", encoding="utf-8")

    # Unknowns
    u = [f"# Unknowns register — {paths.loop}", "",
         "Questions for subject-matter experts and requests for evidence. Answering these is what moves grades up.", "",
         "| ID | Priority | Type | Question | Why | Owner | Affects |", "|---|---|---|---|---|---|---|"]
    for it in unknowns:
        names = ", ".join(f"{a} {by_id[a]['name']}" for a in it["affects"] if a in by_id)
        u.append(f"| {it['id']} | {it['priority']} | {it['type'].replace('_', ' ')} | {it['question']} | {it['why']} | {it['owner']} | {names} |")
    (out / "unknowns-register.md").write_text("\n".join(u) + "\n", encoding="utf-8")
    write_json(out / "jira-issues.json", [
        {"summary": f"[{it['id']}] {it['question']}"[:250],
         "description": f"{it['why']}\n\nOwner: {it['owner']}\nAffects: {', '.join(it['affects'])}\nPriority: {it['priority']}\n"
                        f"Raised by ontology discovery {paths.loop}.",
         "issue_type": "Task", "labels": ["ontology", paths.loop, it["type"]]} for it in unknowns])

    # Gate report
    gr = [f"# Gate report — {paths.loop}", ""]
    for ph in gates:
        gr += [f"## Phase {ph['phase']}: {ph['name']} — **{ph['status'].upper()}**", "",
               f"Exit gate: {ph['exit_gate']}  ", f"Discovery mode: {ph['discovery_mode']} · "
               f"{ph['below_B']} of {ph['in_scope']} in-scope elements below grade B", "",
               "| Criterion | Result | Failing | Covered by unknowns |", "|---|---|---|---|"]
        for c in ph["criteria"]:
            gr.append(f"| {c['id']} {c['text']} | {c['status']} | {', '.join(map(str, c['failing'])) or '—'} | "
                      f"{', '.join(c['covered_by_unknowns']) or '—'} |")
        gr.append("")
    gr += ["## Human gate", ""]
    if decisions:
        mode = next(iter(decisions.values())).get("mode")
        gr.append(f"Mode: **{mode}**" + (" — decisions were filled in by the simulator, not by people." if mode == "simulated" else ""))
        gr += ["", "| Approver | Decisions |", "|---|---|"]
        per = defaultdict(Counter)
        for d in decisions.values():
            per[d["approver"]][d["decision"]] += 1
        for a, c in per.items():
            gr.append(f"| {a} | {', '.join(f'{k}: {v}' for k, v in sorted(c.items()))} |")
    else:
        gr.append("No approvals file yet. Run `python -m ontokit approve`.")
    (out / "gate-report.md").write_text("\n".join(gr) + "\n", encoding="utf-8")

    # Stand-in schemas
    sdir = out / "standins"
    sdir.mkdir(exist_ok=True)
    tax = {t["name"]: t for t in by_kind["taxonomy"]}
    for sysname in sorted({e["properties"].get("system") for e in by_kind["entity"] if e["properties"].get("system")}):
        ddl = [f"-- STAND-IN schema for {sysname}, generated from evidence batch {paths.loop}.",
               "-- This is a hypothesis for the proof of concept, not a copy of the real system.",
               "-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.", ""]
        for e in [e for e in by_kind["entity"] if e["properties"].get("system") == sysname]:
            cols, pk = [], []
            for aid in e["properties"].get("attribute_ids", []):
                a = by_id[aid]
                p = a["properties"]
                dtype = p.get("data_type", "VARCHAR(255)")
                rng = p.get("range")
                if rng in tax or dtype in tax:
                    t = tax.get(rng) or tax.get(dtype)
                    dtype = "VARCHAR(20)"
                    vals = t["properties"].get("values")
                    check = f" CHECK ({_snake(p['attribute'])} IN ({', '.join(repr(v) for v in vals)}))" if vals and not t["conflicts"] else ""
                    note = f"{t['name']} grade {t['grade']}" + (" — values contested" if t["conflicts"] else "")
                else:
                    dtype = JAVA_SQL.get(dtype, dtype)
                    check, note = "", ""
                null = "" if p.get("nullable", True) else " NOT NULL"
                cols.append(f"    {_snake(p['attribute']):<22} {dtype}{null}{check},  -- grade {a['grade']}{'; ' + note if note else ''}")
                if (e["id"], p["attribute"]) in id_attr and id_attr[(e["id"], p["attribute"])]["properties"].get("key") == "primary":
                    pk.append(_snake(p["attribute"]))
            if not cols:
                ddl += [f"-- {e['name']}: no attributes in evidence yet (grade {e['grade']}); see {', '.join(e['open_unknowns']) or 'unknowns'}", ""]
                continue
            if pk:
                cols.append(f"    PRIMARY KEY ({', '.join(pk)})")
            else:
                cols[-1] = cols[-1].replace(",  --", "   --", 1)
            ddl += [f"-- {e['id']} {e['name']} · grade {e['grade']} · {e['status']}", f"CREATE TABLE {_snake(e['name'])} (", *cols, ");", ""]
        (sdir / f"{_snake(re.sub(r'[^A-Za-z0-9]', '', sysname))}.sql").write_text("\n".join(ddl), encoding="utf-8")

    # Summary
    dist = Counter(e["grade"] for e in els)
    kinds = Counter(e["kind"] for e in els)
    sm = [f"# Loop summary — {paths.loop}", "",
          f"- Sources ingested: {len(index['sources'])} ({sum(1 for s in index['sources'].values() if s['stale'])} stale)",
          f"- Elements: {len(els)} — " + ", ".join(f"{v} {k}" for k, v in sorted(kinds.items())),
          f"- Grades: " + " · ".join(f"{g} {dist.get(g, 0)}" for g in "ABCDX"),
          f"- Contradictions: {sum(1 for e in els if e['conflicts'])}",
          f"- Unknowns: {len(unknowns)} ({sum(1 for u in unknowns if u['priority'] == 'high')} high priority)",
          "- Gates: " + ", ".join(f"phase {g['phase']} {g['status']}" for g in gates), "",
          "Outputs: as-is-ontology.yaml, system-inventory.md, glossary.md, unknowns-register.md, jira-issues.json, "
          "gate-report.md, evidence-register.json, elements.json, standins/*.sql, trace.json"]
    (out / "summary.md").write_text("\n".join(sm) + "\n", encoding="utf-8")
    trace.emit("J. Publish", "Publisher", "deliverables written", f"{len(list(out.rglob('*')))} files in outputs/{paths.loop}/",
               grades={g: dist.get(g, 0) for g in "ABCDX"})

"""Build the animated executive storyboard for a scenario from its real loop outputs.

    python -m ontokit simulate --root scenarios/meridale --loop loop-01
    python -m ontokit simulate --root scenarios/meridale --loop loop-02
    python tools/build_exec_storyboard.py --scenario scenarios/meridale --out docs/meridale-storyboard.html
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT))

from ontokit.common import load_config, norm, read_json  # noqa: E402
from ontokit.validate import validate_file  # noqa: E402

KEY_QUOTES = ["also called", "issued by", "values:", "**Customer**", "**Exposure**", "CUSTOMER_NO", "enum CreditStatus",
              "CUST-FIN-01", "customer_no", "Total exposure"]


def loop_data(root: Path, loop: str) -> dict:
    out = root / "outputs" / loop
    els = read_json(out / "elements.json")
    trace = read_json(out / "trace.json")
    unknowns = read_json(out / "unknowns.json")
    ev = read_json(out / "evidence-register.json")
    sources = read_json(root / "work" / loop / "sources.json")["sources"]
    grades = {g: sum(1 for e in els if e["grade"] == g) for g in "ABCDX"}
    proposals = {e["data"]["agent"]: sum(e["data"]["counts"].values()) for e in trace if e["action"] == "proposed"}
    quotes, seen = [], set()
    for r in ev:
        if r["file"] in seen or not any(k in r["quote"] for k in KEY_QUOTES):
            continue
        seen.add(r["file"])
        quotes.append({"file": r["file"].split("/")[-1], "quote": r["quote"][:150], "provenance": r["provenance"]})
    return {
        "loop": loop,
        "files": [{"path": p, "name": p.split("/")[-1], "provenance": s["provenance"], "doc_type": s.get("doc_type"),
                   "author": s.get("author"), "date": s.get("date"), "stale": s["stale"], "carried": bool(s.get("carried_from"))}
                  for p, s in sources.items()],
        "grades": grades, "total": len(els), "kinds": dict(Counter(e["kind"] for e in els)),
        "proposals": proposals, "quotes": quotes[:9],
        "aliases": [{"system": e["data"]["system"], "aliases": e["data"]["aliases"]} for e in trace if e["action"] == "resolved aliases"],
        "contradictions": [{"id": e["id"], "kind": e["kind"], "name": e["name"],
                            "property": e["conflicts"][0]["property"].replace("_", " "),
                            "variants": [{"value": v["value"], "files": [f.split("/")[-1] for f in v["files"]],
                                          "authors": [sources[f].get("author", "") for f in v["files"]]}
                                         for v in e["conflicts"][0]["variants"]]} for e in els if e["conflicts"]],
        "resolved": [{"id": e["id"], "kind": e["kind"], "name": e["name"], "grade": e["grade"],
                      "property": r["property"].replace("_", " "), "value": r["value"],
                      "superseded": [v["value"] for v in r["superseded"]]} for e in els for r in e.get("resolutions", [])],
        "unknowns": unknowns,
        "systems": [{"id": e["id"], "name": e["name"], "aliases": e["aliases"], "roles": e["properties"].get("roles", []),
                     "grade": e["grade"]} for e in els if e["kind"] == "system"],
        "changes": read_json(out / "changes.json") if (out / "changes.json").exists() else None,
        "gates": [{"phase": g["phase"], "status": g["status"]} for g in read_json(root / "work" / loop / "gates.json")],
        "_els": els,
    }


def find(els, kind, name):
    return next((e for e in els if e["kind"] == kind and norm(e["name"]) == norm(name)), None)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=str(KIT / "scenarios" / "meridale"))
    ap.add_argument("--out", default=str(KIT / "docs" / "meridale-storyboard.html"))
    a = ap.parse_args()
    root = Path(a.scenario)
    sc = yaml.safe_load((root / "scenario.yaml").read_text(encoding="utf-8"))
    loops = sorted(p.name for p in (root / "outputs").iterdir() if (p / "elements.json").exists())
    L = [loop_data(root, l) for l in loops]
    first, last = L[0], L[-1]

    # Validator demo: three deliberately bad claims, real messages
    idx = read_json(root / "work" / first["loop"] / "sources.json")
    f0 = next(iter(idx["sources"]))
    ok = next(l for l in idx["sources"][f0]["lines"] if l.strip()).strip()
    bad = {"proposals": [
        {"kind": "concept", "name": "Customer lifetime value", "origin": "inferred", "definition": "x",
         "evidence": [{"file": f0, "quote": "Customer lifetime value is tracked in TradeDesk."}]},
        {"kind": "system", "name": "SalesCloud", "origin": "inferred", "evidence": [{"file": f0, "quote": ok}]},
        {"kind": "concept", "name": "Group Customer", "origin": "confirmed", "evidence": [{"file": f0, "quote": ok}]},
    ]}
    _, rej = validate_file("ba", bad, idx, load_config("decision_rights.yaml")["agents"])
    claims = ["“Customer lifetime value is tracked in TradeDesk.”", "“There is a system called SalesCloud.”",
              "“Group Customer is confirmed.”"]
    plain = lambda m: ("Its quote does not appear in any document" if "quote not found" in m else
                       "Outside this agent's remit (the RACI)" if "RACI" in m else
                       "Agents cannot approve their own findings" if "cannot mark" in m else m)
    rejections = [{"claim": c, "why": plain(r["problems"][0]), "raw": r["problems"][0]} for c, r in zip(claims, rej)]

    # Final customer model (last loop)
    els = last["_els"]
    layout = sc.get("model_layout", {})
    nodes = []
    for name, (x, y) in layout.items():
        e = find(els, "entity", name)
        if e:
            nodes.append({"id": e["id"], "name": name, "x": x, "y": y, "grade": e["grade"], "system": e["properties"].get("system", ""),
                          "attrs": len(e["properties"].get("attribute_ids", [])),
                          "note": "same customer, confirmed" if e["properties"].get("realises") and name != "Customer"
                          and find(els, "concept", "Customer") and e["properties"]["realises"] == find(els, "concept", "Customer")["id"] else ""})
    names = {n["name"] for n in nodes}
    edges = []
    for r in els:
        if r["kind"] != "relationship" or r["origin"] == "assumed":
            continue
        f, t = r["properties"].get("from"), r["properties"].get("to")
        if f in names and t in names and f != t:
            edges.append({"from": f, "to": t, "grade": r["grade"], "card": r["properties"].get("cardinality", ""),
                          "via": r["properties"].get("via", "") if r["properties"].get("cardinality") == "many-to-many" else ""})

    # Board-question blueprint, before vs after
    def status(e):
        if not e:
            return "missing"
        if e["kind"] == "concept" and not any(k in e["properties"] for k in ("realised_by", "also_realised_by")):
            return "build"
        return {"A": "ready", "B": "ready", "C": "confirm", "D": "blocked", "X": "blocked"}[e["grade"]]
    blueprint = []
    for b in sc["exposure_blueprint"]:
        e1, e2 = find(first["_els"], b["kind"], b["name"]), find(els, b["kind"], b["name"])
        sysname = ""
        if e2:
            p = e2["properties"]
            via = find(els, "entity", p["via"]) if p.get("cardinality") == "many-to-many" and p.get("via") else None
            sysname = (via["properties"].get("system") if via else "") or p.get("system") or next((x["properties"].get("system", "") for x in els
                                               if x["id"] == p.get("entity_id")), "") or \
                next((x["properties"].get("system", "") for x in els if x["kind"] == "entity"
                      and x["name"] == p.get("from")), "")
        if e2 and e2["kind"] == "identifier" and e2["properties"].get("issued_by"):
            sysname = f"issued by {e2['properties']['issued_by']}"
        elif e2 and e2["kind"] == "taxonomy":
            sysname = "group standard"
        blueprint.append({"need": b["need"], "element": b["name"], "kind": b["kind"],
                          "before": e1["grade"] if e1 else "—", "after": e2["grade"] if e2 else "—",
                          "status_before": status(e1), "status": status(e2), "system": sysname})
        if not e2:
            print(f"warning: blueprint element not found: {b['kind']} {b['name']}", file=sys.stderr)

    for l in L:
        l.pop("_els")
    data = {"scenario": sc, "loops": L, "rejections": rejections, "model": {"nodes": nodes, "edges": edges},
            "blueprint": blueprint}
    tpl = (KIT / "docs" / "exec-storyboard.template.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    Path(a.out).write_text(tpl.replace("__DATA__", payload), encoding="utf-8")
    print(f"wrote {a.out} ({len(payload) // 1024} KB of run data); nodes {len(nodes)}, edges {len(edges)}; "
          f"blueprint {Counter(b['status'] for b in blueprint)}")


if __name__ == "__main__":
    main()

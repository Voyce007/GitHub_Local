"""Build the animated decomposition storyboard for a monolith scenario from its real loop outputs.

    python -m ontokit simulate --root scenarios/northmere --loop loop-01
    python tools/build_decomp_storyboard.py --scenario scenarios/northmere --out docs/northmere-storyboard.html
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

from ontokit.common import read_json  # noqa: E402

# Source lines worth quoting on screen: (file suffix, text the line must contain)
QUOTES = [
    ("taxcore-system-overview.md", "TAXCORE (also called"),
    ("business-capability-map.md", "**Allocate NI Number**"),
    ("taxcore-batch-jobs.csv", "J020,"),
    ("taxcore_procedures.sql", "UPDATE TC_PERSON SET NI_NUMBER"),
    ("taxcore-batch-jobs.csv", "J330,"),
    ("childcare-scheme-guide.md", "expected income"),
    ("national-insurance-procedures.md", "issued by NumberHub"),
    ("data-glossary.md", "**Customer**"),
    ("taxcore-data-dictionary.csv", "TC_PERSON,NI_NUMBER"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=str(KIT / "scenarios" / "northmere"))
    ap.add_argument("--loop", default=None)
    ap.add_argument("--out", default=str(KIT / "docs" / "northmere-storyboard.html"))
    a = ap.parse_args()
    root = Path(a.scenario)
    loop = a.loop or sorted(p.name for p in (root / "outputs").iterdir() if (p / "decomposition").exists())[-1]
    out, work = root / "outputs" / loop, root / "work" / loop
    sc = yaml.safe_load((root / "scenario.yaml").read_text(encoding="utf-8"))
    td = yaml.safe_load((root / "target_domains.yaml").read_text(encoding="utf-8"))
    els = read_json(out / "elements.json")
    dec = read_json(out / "decomposition" / "decomposition.json")
    trace = read_json(out / "trace.json")
    unknowns = read_json(out / "unknowns.json")
    sources = read_json(work / "sources.json")["sources"]
    gates = read_json(work / "gates.json")

    ents = [e for e in els if e["kind"] == "entity" and e["origin"] != "assumed"]
    calcs = [e for e in els if e["kind"] == "calculation"]
    tables = [{"table": e["properties"].get("physical", ""), "entity": e["name"], "domain": e["properties"].get("domain"),
               "attrs": len(e["properties"].get("attribute_ids", [])), "grade": e["grade"],
               "basis": e["properties"].get("domain_basis", "")} for e in ents]
    matrix = {}
    for t in tables:
        row = {}
        for c in calcs:
            dom, p = c["properties"].get("domain"), c["properties"]
            if t["table"] in p.get("writes", []):
                row[dom] = "W"
            elif t["table"] in p.get("reads", []) and row.get(dom) != "W":
                row[dom] = "R"
        matrix[t["table"]] = row
    jobs = [{"program": c["name"], "title": c["properties"].get("title", c["name"]), "job": c["properties"].get("job_id", ""),
             "domain": c["properties"].get("domain"), "team": c["properties"].get("owner_team", ""),
             "writes": c["properties"].get("writes", []), "reads": c["properties"].get("reads", []),
             "cols": c["properties"].get("writes_columns", [])} for c in calcs]
    person = next((e for e in ents if e["name"] == "Person"), None)
    by_id = {e["id"]: e for e in els}
    person_cols = [{"col": by_id[a]["properties"].get("physical"), "domain": by_id[a]["properties"].get("domain")}
                   for a in (person["properties"].get("attribute_ids", []) if person else [])]

    quotes = []
    for suffix, needle in QUOTES:
        for path, s in sources.items():
            if path.endswith(suffix):
                line = next((l.strip() for l in s["lines"] if needle in l), None)
                if line:
                    quotes.append({"file": suffix, "quote": line[:170], "provenance": s["provenance"]})
    files = [{"name": p.split("/")[-1], "provenance": s["provenance"], "date": s.get("date"), "author": s.get("author"),
              "stale": s["stale"]} for p, s in sources.items()]
    proposals = {e["data"]["agent"]: sum(e["data"]["counts"].values()) for e in trace if e["action"] == "proposed"}
    mapping = (out / "decomposition" / "source-to-target.csv").read_text(encoding="utf-8").strip().splitlines()[1:]
    moved = [r for r in mapping if r.endswith("moves to National Insurance") or "moves to" in r]

    # carve order: domains nobody else depends on go first (leaf-first strangler)
    consumers_of = Counter()
    for d in dec["dependencies"]:
        consumers_of[d["provider"]] += 1
    carve = sorted([d["key"] for d in dec["domains"]], key=lambda k: (consumers_of[k], k != "childcare"))

    data = {
        "scenario": sc, "loop": loop, "monolith": dec["monolith"], "domains": td["domains"],
        "files": files, "proposals": proposals, "quotes": quotes,
        "tables": tables, "matrix": matrix, "jobs": jobs, "person_cols": person_cols,
        "summary": dec["summary"], "splits": dec["splits"], "xwrites": dec["cross_domain_writes"],
        "deps": dec["dependencies"], "services": dec["services"],
        "contradictions": [{"name": e["name"], "kind": e["kind"], "property": e["conflicts"][0]["property"].replace("_", " "),
                            "variants": [{"value": v["value"], "authors": [sources[f].get("author", "") for f in v["files"]],
                                          "stale": bool(v["stale"])} for v in e["conflicts"][0]["variants"]]}
                           for e in els if e["conflicts"]],
        "unknowns": unknowns,
        "grades": {g: sum(1 for e in els if e["grade"] == g) for g in "ABCDX"}, "total": len(els),
        "gates": [{"phase": g["phase"], "name": g["name"], "status": g["status"]} for g in gates],
        "mapping": {"columns": len(mapping), "moved": len(moved)},
        "carve": [{"key": k, "consumers": consumers_of[k]} for k in carve],
    }
    tpl = (KIT / "docs" / "decomp-storyboard.template.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    Path(a.out).write_text(tpl.replace("__DATA__", payload), encoding="utf-8")
    print(f"wrote {a.out} ({len(payload) // 1024} KB); {len(tables)} tables, {len(jobs)} jobs, {len(quotes)} quotes, carve order {carve}")


if __name__ == "__main__":
    main()

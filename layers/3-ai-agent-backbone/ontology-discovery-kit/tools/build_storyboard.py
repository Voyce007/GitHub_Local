"""Build docs/storyboard.html (storyboard + explainer + simulation playback) from a loop's real outputs.

    python -m ontokit simulate            # or a live run
    python tools/build_storyboard.py --loop loop-01
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT))

from ontokit.common import load_config, read_json  # noqa: E402
from ontokit.validate import validate_file  # noqa: E402


def build(loop: str, root: Path) -> dict:
    work, out = root / "work" / loop, root / "outputs" / loop
    index = read_json(work / "sources.json")
    els = read_json(out / "elements.json")
    trace = read_json(out / "trace.json")
    unknowns = read_json(work / "unknowns.json")
    gates = read_json(work / "gates.json")
    rights = load_config("decision_rights.yaml")
    grades = load_config("evidence_grades.yaml")
    playbook = load_config("playbook.yaml")

    # Real validator messages for three bad proposals (what live agents get back)
    sample_file = next(iter(index["sources"]))
    ok_quote = next(l for l in index["sources"][sample_file]["lines"] if l.strip()).strip()
    bad = {"proposals": [
        {"kind": "concept", "name": "Invented term", "origin": "inferred", "definition": "x",
         "evidence": [{"file": sample_file, "quote": "A sentence the agent made up."}]},
        {"kind": "system", "name": "Out-of-scope system", "origin": "inferred",
         "evidence": [{"file": sample_file, "quote": ok_quote}]},
        {"kind": "concept", "name": "Self-approved concept", "origin": "confirmed",
         "evidence": [{"file": sample_file, "quote": ok_quote}]},
    ]}
    _, rejected = validate_file("ba", bad, index, rights["agents"])

    first_table = ""
    sql = out / "standins" / "cust_hub.sql"
    if sql.exists():
        txt = sql.read_text().split("\n\n")
        first_table = "\n\n".join(txt[:2])

    by_kind = Counter(e["kind"] for e in els)
    return {
        "loop": loop,
        "organisation": index.get("organisation"),
        "files": [{"path": p, "provenance": s["provenance"], "doc_type": s.get("doc_type"), "date": s.get("date"),
                   "stale": s["stale"], "age": s.get("age_years"), "lines": len(s["lines"]),
                   "hint": s.get("system_hint"), "notes": s.get("notes")} for p, s in index["sources"].items()],
        "trace": trace,
        "grades": {g: sum(1 for e in els if e["grade"] == g) for g in "ABCDX"},
        "kinds": dict(by_kind),
        "elements_total": len(els),
        "systems": [{"id": e["id"], "name": e["name"], "aliases": e["aliases"], "roles": e["properties"].get("roles", []),
                     "grade": e["grade"], "sources": len({x["file"] for x in e["evidence"]})}
                    for e in els if e["kind"] == "system"],
        "contradictions": [{"id": e["id"], "kind": e["kind"], "name": e["name"],
                            "variants": [{"property": c["property"], "value": v["value"], "files": v["files"], "stale": v["stale"]}
                                         for c in e["conflicts"] for v in c["variants"]]}
                           for e in els if e["conflicts"]],
        "assumed": [{"id": e["id"], "kind": e["kind"], "name": e["name"]} for e in els if e["origin"] == "assumed"],
        "unknowns": unknowns,
        "gates": [{"phase": g["phase"], "name": g["name"], "status": g["status"], "below_B": g["below_B"],
                   "in_scope": g["in_scope"], "criteria": [{"id": c["id"], "text": c["text"], "status": c["status"]}
                                                          for c in g["criteria"]]} for g in gates],
        "rejections": [{"name": r["name"], "problem": r["problems"][0]} for r in rejected],
        "standin": first_table,
        "outputs": sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file()),
        "agents": rights["agents"],
        "approvals": rights["approvals"],
        "grade_text": grades["grades"],
        "phases": [{"id": p["id"], "name": p["name"], "mode": p["discovery_mode"], "gate": p["exit_gate"]} for p in playbook["phases"]],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", default="loop-01")
    ap.add_argument("--root", default=str(KIT / "discovery"))
    ap.add_argument("--out", default=str(KIT / "docs" / "storyboard.html"))
    a = ap.parse_args()
    data = build(a.loop, Path(a.root))
    tpl = (KIT / "docs" / "storyboard.template.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    Path(a.out).write_text(tpl.replace("__DATA__", payload), encoding="utf-8")
    print(f"wrote {a.out} ({len(payload) // 1024} KB of run data)")


if __name__ == "__main__":
    main()

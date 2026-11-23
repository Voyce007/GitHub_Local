"""Stage M — Report packs: a consumable version of every agent's results, plus one index.

For each agent (Business Analyst, Enterprise Architect, Data Architect, Engineer,
Ontology Steward, Conformance) this writes, in <root>/outputs/<loop>/reports/:

    <agent>.html   an explainer: what the agent found, its diagrams (rendered), searchable tables
    <agent>.xlsx   an Excel workbook, one sheet per table, every row with grade and evidence citations
    <agent>.docx   a Word document with the same content as prose and tables

and reports/index.html, one page that links to every agent's HTML, Excel, Word and
diagrams, and to every other loop output. <root>/outputs/index.html links all loops.

Excel and Word need openpyxl and python-docx (`pip install openpyxl python-docx`, or
the installer). Without them the HTML is still produced and the index says how to add them.
Everything is generated from the graded model: nothing here is hand-written.
"""
from __future__ import annotations

import datetime as dt
import html
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from .common import LoopPaths, Trace, human, read_json

GRADE_TEXT = {"A": "Confirmed by a real system artefact", "B": "Two or more independent sources agree",
              "C": "Single source", "D": "Assumed, not yet evidenced", "X": "Sources contradict"}
GRADE_FILL = {"A": "D7EEDF", "B": "D9E6F3", "C": "F6E7CC", "D": "E3E6EA", "X": "F5D5CF"}
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"

AGENTS = [
    ("ba", "Business Analyst", "What does the business mean?",
     "Business terms and their definitions, synonyms, business rules and classifications.", ["ba-concept-map"]),
    ("ea", "Enterprise Architect", "Which systems exist, and how do they connect?",
     "Systems and their aliases and roles, the data flows between them, and the business capabilities with their accountable teams.",
     ["ea-system-context", "ea-capability-map"]),
    ("da", "Data Architect", "How is the data structured and identified?",
     "Entities, attributes, keys and relationships, and where each monolith column ends up.", ["da-entity-relationship"]),
    ("eng", "Engineer", "How is data actually exchanged and calculated?",
     "Batch jobs and stored procedures with the tables they read and change, interfaces, events and rules enforced in code.",
     ["eng-calculation-flow"]),
    ("steward", "Ontology Steward", "Is the model coherent, and what must people decide?",
     "Open questions with owners, contradictions, review flags, the proposed decomposition and what changed since the last loop.",
     ["steward-aliases", "steward-decomposition"]),
    ("conformance", "Conformance", "Is it done, by the playbook's definition of done?",
     "Evidence grades, automated gate results, the decisions each approver is asked to make, and the evidence register.",
     ["conformance-grades", "conformance-gates"]),
]


# ------------------------------------------------------------------ data

def _ev(e, n=2):
    return "; ".join(f"{x['file']} ({x.get('locator', '')})" for x in e["evidence"][:n]) + (f" +{len(e['evidence']) - n}" if len(e["evidence"]) > n else "")


def _quote(e):
    return e["evidence"][0]["quote"][:220] if e["evidence"] else ""


def _j(v):
    return ", ".join(map(str, v)) if isinstance(v, (list, tuple)) else ("" if v is None else str(v))


def _sec(title, intro, cols, rows):
    return {"title": title, "intro": intro, "columns": cols, "rows": rows}


def _ctx(paths: LoopPaths) -> dict:
    w, o = paths.work, paths.outputs
    model = read_json(w / "model.json")
    els = model["elements"]
    by = defaultdict(list)
    for e in els:
        by[e["kind"]].append(e)
    appr = yaml.safe_load((w / "approvals.yaml").read_text(encoding="utf-8")) if (w / "approvals.yaml").exists() else {}
    return {"model": model, "els": els, "by": by, "by_id": {e["id"]: e for e in els},
            "unknowns": read_json(w / "unknowns.json") if (w / "unknowns.json").exists() else [],
            "gates": read_json(w / "gates.json") if (w / "gates.json").exists() else [],
            "changes": read_json(w / "changes.json") if (w / "changes.json").exists() else None,
            "sources": read_json(w / "sources.json")["sources"],
            "approvals": appr or {}, "dec": model.get("decomposition"),
            "notes": {k: (w / f).read_text(encoding="utf-8") for k, f in (("steward", "steward-notes.md"), ("conformance", "conformance-briefing.md"))
                      if (w / f).exists()},
            "agent_notes": (o / "agent-notes.md").read_text(encoding="utf-8") if (o / "agent-notes.md").exists() else "",
            "diagrams": {p.stem: p.read_text(encoding="utf-8") for p in (o / "diagrams").glob("*.mmd")} if (o / "diagrams").exists() else {}}


def _dom(c, e):
    d = e["properties"].get("domain")
    names = {x["key"]: x["name"] for x in (c["dec"] or {}).get("domains", [])}
    return names.get(d, d or "")


def sections(agent: str, c: dict) -> list[dict]:
    by, by_id = c["by"], c["by_id"]
    if agent == "ba":
        return [
            _sec("Business glossary", "Every business term found, with its definition and synonyms. Terms without a definition need one from the business owner.",
                 ["ID", "Term", "Definition", "Synonyms", "Domain", "Grade", "Sources", "Evidence"],
                 [[e["id"], e["name"], e["definition"] or "(not defined in any source)", _j(e["aliases"]), _dom(c, e), e["grade"],
                   len({x["file"] for x in e["evidence"]}), _ev(e)] for e in by["concept"]]),
            _sec("Business rules", "Rules stated in documents or enforced in code, as plain sentences.",
                 ["ID", "Rule", "Domain", "Grade", "Found by", "Evidence"],
                 [[e["id"], e["name"], _dom(c, e), e["grade"], _j(e["proposed_by"]), _ev(e)] for e in by["rule"]]),
            _sec("Classifications", "Code lists and lifecycles. A grade of X means sources list different values.",
                 ["ID", "Classification", "Values", "Domain", "Grade", "Conflict", "Evidence"],
                 [[e["id"], e["name"], _j(e["properties"].get("values") or ""), _dom(c, e), e["grade"],
                   " vs ".join(_j(v["value"]) for cf in e["conflicts"] for v in cf["variants"]), _ev(e)] for e in by["taxonomy"]]),
        ]
    if agent == "ea":
        return [
            _sec("Systems", "Candidate systems, every name they go by, and their candidate role. A system with no role needs an owner to explain it.",
                 ["ID", "System", "Also known as", "Roles", "Grade", "Sources", "Evidence"],
                 [[e["id"], e["name"], _j(e["aliases"]), _j(e["properties"].get("roles", [])) or "(role unknown)", e["grade"],
                   len({x["file"] for x in e["evidence"]}), _ev(e)] for e in by["system"]]),
            _sec("Data flows", "Data moving between systems, from catalogues, diagrams, prose and config.",
                 ["ID", "From", "To", "Label", "Grade", "Evidence"],
                 [[e["id"], e["properties"].get("source"), e["properties"].get("target"), e["properties"].get("label", ""), e["grade"], _ev(e)]
                  for e in by["flow"]]),
            _sec("Business capabilities", "Capabilities and their one accountable team. In a decomposition, these decide domain ownership.",
                 ["ID", "Capability", "Accountable team", "Domain", "Description", "Grade", "Evidence"],
                 [[e["id"], e["name"], e["properties"].get("owner_team", ""), _dom(c, e), e["definition"], e["grade"], _ev(e)]
                  for e in by["capability"]]),
        ]
    if agent == "da":
        secs = [
            _sec("Entities", "Logical entities lifted from tables, dictionaries and code, with their owning domain where the monolith is being split.",
                 ["ID", "Entity", "Physical table", "System", "Domain", "Attributes", "Grade", "Ownership basis", "Evidence"],
                 [[e["id"], e["name"], e["properties"].get("physical", ""), e["properties"].get("system", ""), _dom(c, e),
                   len(e["properties"].get("attribute_ids", [])), e["grade"], e["properties"].get("domain_basis", ""), _ev(e)]
                  for e in by["entity"]]),
            _sec("Attributes", "Every attribute with its physical column and type.",
                 ["ID", "Entity", "Attribute", "Physical column", "Type", "Nullable", "Description", "Domain", "Grade", "Evidence"],
                 [[e["id"], e["properties"].get("entity"), e["properties"].get("attribute"), e["properties"].get("physical", ""),
                   e["properties"].get("data_type", ""), e["properties"].get("nullable", ""), e["properties"].get("description", ""),
                   _dom(c, e), e["grade"], _ev(e, 1)] for e in by["attribute"]]),
            _sec("Identifiers", "Keys, and who issues them. A grade of X means sources name different issuers.",
                 ["ID", "Identifier", "Entity", "Key type", "Issued by", "Grade", "Evidence"],
                 [[e["id"], e["name"], e["properties"].get("entity", ""), e["properties"].get("key", ""),
                   e["properties"].get("issued_by") or " vs ".join(_j(v["value"]) for cf in e["conflicts"] for v in cf["variants"]),
                   e["grade"], _ev(e)] for e in by["identifier"]]),
            _sec("Relationships", "How entities link, with cardinality. Cross-domain links become service calls after a split.",
                 ["ID", "From", "To", "Cardinality", "Via", "Cross-domain", "Grade", "Evidence"],
                 [[e["id"], e["properties"].get("from"), e["properties"].get("to"), e["properties"].get("cardinality", ""),
                   e["properties"].get("via", ""), "yes" if e["properties"].get("cross_domain") else "", e["grade"], _ev(e)]
                  for e in by["relationship"]]),
        ]
        stt = c.get("stt")
        if stt:
            secs.append(_sec("Source-to-target mapping", "Where every monolith column goes in the target domains.", stt[0], stt[1:]))
        return secs
    if agent == "eng":
        return [
            _sec("Calculations", "Batch jobs and stored procedures, with the tables they read and change. Changes across domains are what the split must replace.",
                 ["ID", "Program", "Title", "Capability", "Team", "Domain", "Reads", "Changes", "Columns changed", "Frequency", "Grade", "Evidence"],
                 [[e["id"], e["name"], e["properties"].get("title", ""), e["properties"].get("capability", ""),
                   e["properties"].get("owner_team", ""), _dom(c, e), _j(e["properties"].get("reads", [])),
                   _j(e["properties"].get("writes", [])), _j(e["properties"].get("writes_columns", [])),
                   e["properties"].get("frequency", ""), e["grade"], _ev(e)] for e in by["calculation"]]),
            _sec("Interfaces", "APIs, messages, files and events in and out of the systems.",
                 ["ID", "Interface", "Source", "Target", "Mechanism", "Frequency", "Payload", "Grade", "Evidence"],
                 [[e["id"], e["name"], e["properties"].get("source", ""), e["properties"].get("target", ""),
                   e["properties"].get("mechanism", ""), e["properties"].get("frequency", ""), e["properties"].get("payload", ""),
                   e["grade"], _ev(e)] for e in by["interface"]]),
            _sec("Events", "Business events published today.", ["ID", "Event", "Producer", "Consumer", "Grade", "Evidence"],
                 [[e["id"], e["name"], e["properties"].get("producer", ""), e["properties"].get("consumer", ""), e["grade"], _ev(e)]
                  for e in by["event"]]),
            _sec("Rules enforced in code", "Validation found in code, as plain sentences.", ["ID", "Rule", "Grade", "Evidence"],
                 [[e["id"], e["name"], e["grade"], _ev(e)] for e in by["rule"] if "eng" in e["proposed_by"]]),
        ]
    if agent == "steward":
        dec, ch = c["dec"], c["changes"]
        secs = [
            _sec("Open questions", "Precise questions and evidence requests, each sent to the person who can answer it. Answering these is what moves the next loop forward.",
                 ["ID", "Priority", "Type", "Question", "Why", "Owner", "Affects"],
                 [[u["id"], u["priority"], u["type"].replace("_", " "), u["question"], u["why"], u["owner"],
                   _j(f"{a} {by_id[a]['name']}" for a in u["affects"] if a in by_id)] for u in c["unknowns"]]),
            _sec("Contradictions", "Where sources disagree. Kept, not resolved: the named owner decides.",
                 ["ID", "Element", "Property", "Versions and sources"],
                 [[e["id"], f"{e['kind']} {e['name']}", cf["property"].replace("_", " "),
                   " | ".join(f"{_j(v['value'])} ← {_j(v['files'])}" for v in cf["variants"])] for e in c["els"] for cf in e["conflicts"]]),
            _sec("Resolved contradictions", "Settled by an owner's answer or a real system artefact; the losing versions are kept for audit.",
                 ["ID", "Element", "Property", "Now", "Decided by", "Superseded"],
                 [[e["id"], f"{e['kind']} {e['name']}", r["property"], _j(r["value"]), _j(r["resolved_by"]),
                   " / ".join(_j(v["value"]) for v in r["superseded"])] for e in c["els"] for r in e.get("resolutions", [])]),
            _sec("Review flags", "Possible synonyms, homonyms, undefined terms and other things to review.",
                 ["Type", "Detail", "Affects"], [[f["type"].replace("_", " "), f["detail"], _j(f["affects"])] for f in c["model"].get("flags", [])]),
        ]
        if dec:
            names = {d["key"]: d["name"] for d in dec["domains"]}
            secs += [
                _sec("Domain ownership", "Which domain owns each monolith table, and why.",
                     ["Entity", "Table", "Domain", "Basis", "Grade"],
                     [[e["name"], e["properties"].get("physical", ""), names.get(e["properties"].get("domain"), "unassigned"),
                       e["properties"].get("domain_basis", ""), e["grade"]] for e in c["by"]["entity"] if e["origin"] != "assumed"]),
                _sec("Business services", "The access layer: commands change data, queries let other domains read it, events let them react.",
                     ["Domain", "Service", "Type", "Used by", "Replaces / implements"],
                     [[names[k], s["name"], s["type"], _j(names[x] for x in s.get("consumers", [])),
                       _j(s.get("calculations", []) or s.get("replaces", []))] for k in dec["services"] for s in dec["services"][k]]),
                _sec("Moves and events", "Columns that move domain, and direct cross-domain writes that become events.",
                     ["Kind", "What", "From", "To", "Why"],
                     [["column moves", f"{s['entity']}.{s['column']}", names[s["from"]], names[s["to"]], f"created by {s['capability']}"] for s in dec["splits"]]
                     + [["write becomes event", x["event"], names[x["writer"]], names[x["owner"]], f"{x['calculation']} changes {x['entity']}"]
                        for x in dec["cross_domain_writes"]]),
            ]
        if ch:
            secs.append(_sec(f"Changes since {ch['from_loop']}", "Every grade change since the previous loop, for approvers to sign.",
                             ["ID", "Element", "From", "To", "Why"],
                             [[r["id"], f"{r['kind']} {r['name']}", r["from"], r["to"], r["reason"]] for r in ch["regraded"]]))
        return secs
    if agent == "conformance":
        g = Counter(e["grade"] for e in c["els"])
        rows = []
        for approver, items in (c["approvals"].get("approvers") or {}).items():
            for it in items:
                rows.append([approver, it["id"], it["kind"], it["name"], it["grade"], it["decision"], it.get("by", ""), it.get("reason", "")])
        ev = defaultdict(list)
        for e in c["els"]:
            for x in e["evidence"]:
                ev[(x["file"], x.get("locator"), x.get("id"))].append(e["id"])
        return [
            _sec("Evidence grades", "How every element is graded, by rule.", ["Grade", "Meaning", "Elements"],
                 [[k, GRADE_TEXT[k], g.get(k, 0)] for k in "ABCDX"]),
            _sec("Gate criteria", "Automated exit checks per phase. Provisional means failures are covered by open questions, or evidence is below grade B.",
                 ["Phase", "Criterion", "Result", "Failing", "Covered by open questions"],
                 [[f"{ph['phase']} {ph['name']}", f"{cr['id']} {cr['text']}", cr["status"], _j(cr["failing"]), _j(cr["covered_by_unknowns"])]
                  for ph in c["gates"] for cr in ph["criteria"]]),
            _sec("Decisions by approver", "What each named role is asked to decide. Agents never fill these in.",
                 ["Approver", "ID", "Kind", "Element", "Grade", "Decision", "By", "Reason"], rows),
            _sec("Evidence register", "Every cited source line and the elements it supports.",
                 ["Evidence", "File", "Locator", "Provenance", "Stale", "Supports"],
                 [[k[2], k[0], k[1], c["sources"].get(k[0], {}).get("provenance", ""), "yes" if c["sources"].get(k[0], {}).get("stale") else "",
                   _j(v)] for k, v in sorted(ev.items(), key=lambda kv: kv[0][2] or "")]),
        ]
    return []


# ------------------------------------------------------------------ HTML

CSS = """
:root{--bg:#F5F6F8;--surface:#fff;--sunk:#EEF0F4;--ink:#18202A;--muted:#5A6372;--line:#D9DDE4;--accent:#3A4AA8;--accent-soft:#E6E9F7;
--gA:#1D7A44;--gB:#2867A0;--gC:#9A6210;--gD:#6B7483;--gX:#B23824}
@media (prefers-color-scheme:dark){:root{--bg:#10141A;--surface:#171C24;--sunk:#0D1116;--ink:#E5E8EE;--muted:#98A1AF;--line:#2A313C;
--accent:#929FF2;--accent-soft:#222A4C;--gA:#52C283;--gB:#66A9E2;--gC:#E2A64B;--gD:#9AA3B1;--gX:#F27D64;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",Inter,Roboto,sans-serif}
.wrap{max-width:1240px;margin:0 auto;padding:28px max(16px,env(safe-area-inset-left)) 64px max(16px,env(safe-area-inset-right))}
a{color:var(--accent)}h1,h2,h3{line-height:1.2;margin:0}h1{font-size:1.9rem}h2{font-size:1.3rem;margin-top:8px}
.eyebrow{font:500 .72rem ui-monospace,Menlo,Consolas,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.muted{color:var(--muted)}.lead{color:var(--muted);max-width:75ch}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.pill{display:inline-flex;gap:6px;align-items:center;padding:4px 11px;border-radius:999px;
border:1px solid var(--line);background:var(--surface);font-size:.85rem;text-decoration:none;color:var(--ink)}a.pill:hover{border-color:var(--accent)}
.g{display:inline-block;min-width:1.8em;text-align:center;border-radius:5px;padding:0 5px;font:600 .8rem ui-monospace,Menlo,monospace;
color:var(--gc);background:color-mix(in srgb,var(--gc) 15%,transparent);border:1px solid color-mix(in srgb,var(--gc) 40%,transparent)}
.g-A{--gc:var(--gA)}.g-B{--gc:var(--gB)}.g-C{--gc:var(--gC)}.g-D{--gc:var(--gD)}.g-X{--gc:var(--gX)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px 18px;display:grid;gap:8px;align-content:start;min-width:0}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,360px),1fr));gap:14px}
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}.stat{background:var(--surface);border:1px solid var(--line);
border-radius:10px;padding:10px 14px}.stat b{display:block;font-size:1.5rem}
.gbar{display:flex;height:16px;border-radius:6px;overflow:hidden;border:1px solid var(--line)}.gbar i{display:block}
section{display:grid;gap:10px;margin-top:26px}.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--surface);max-height:640px}
table{border-collapse:collapse;width:100%;font-size:.86rem}th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{position:sticky;top:0;background:var(--sunk);font:600 .72rem ui-monospace,Menlo,monospace;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
td:first-child{white-space:nowrap}td.ev{color:var(--muted);font-size:.8rem;max-width:340px}input.f{font:inherit;padding:6px 10px;border-radius:8px;border:1px solid var(--line);
background:var(--surface);color:var(--ink);width:min(100%,320px)}
nav.toc{display:flex;flex-wrap:wrap;gap:6px}.diag{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;overflow-x:auto}
pre.mermaid{margin:0}pre.raw{white-space:pre-wrap;font-size:.75rem;color:#333}.notes{background:var(--surface);border:1px solid var(--line);
border-radius:10px;padding:14px 18px;max-height:700px;overflow:auto}.notes h1,.notes h2,.notes h3{margin:14px 0 6px}
footer{margin-top:40px;font-size:.8rem;color:var(--muted)}
"""

JS = """
document.querySelectorAll('input.f').forEach(inp=>inp.addEventListener('input',()=>{const q=inp.value.toLowerCase();
document.querySelectorAll('#'+inp.dataset.t+' tbody tr').forEach(r=>r.hidden=q&&!r.textContent.toLowerCase().includes(q))}));
"""
MERMAID_JS = f"""<script src="{MERMAID_CDN}"></script>
<script>if(window.mermaid){{mermaid.initialize({{startOnLoad:true,securityLevel:'loose',theme:'default'}})}}
else{{document.querySelectorAll('pre.mermaid').forEach(p=>{{p.classList.remove('mermaid');p.classList.add('raw');
p.insertAdjacentHTML('beforebegin','<p class=muted>Diagram source (connect to the internet to render it, or open the .mmd file in any Mermaid viewer):</p>')}})}}</script>"""


def _e(s):
    return html.escape("" if s is None else str(s))


def _cell(col, v):
    if col == "Grade" and str(v) in GRADE_TEXT:
        return f'<td><span class="g g-{v}" title="{_e(GRADE_TEXT[str(v)])}">{v}</span></td>'
    return f'<td class="ev">{_e(v)}</td>' if col == "Evidence" else f"<td>{_e(v)}</td>"


def _gbar(g, total):
    col = {"A": "var(--gA)", "B": "var(--gB)", "C": "var(--gC)", "D": "var(--gD)", "X": "var(--gX)"}
    return '<div class="gbar">' + "".join(f'<i style="width:{g.get(k, 0) / max(total, 1) * 100:.2f}%;background:{col[k]}" title="{k}: {g.get(k, 0)}"></i>'
                                          for k in "ABCDX" if g.get(k)) + "</div>"


def _md(text: str) -> str:
    """Tiny Markdown-to-HTML for the review notes (headings, lists, tables, paragraphs, bold, code)."""
    out, para, table = [], [], []

    def inline(s):
        s = _e(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        return re.sub(r"`(.+?)`", r"<code>\1</code>", s)

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()
        if table:
            rows = [r for r in table if not re.match(r"^\|?\s*[-:| ]+\|?\s*$", r)]
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            if cells:
                out.append('<div class="tw"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in cells[0]) + "</tr></thead><tbody>"
                           + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in cells[1:]) + "</tbody></table></div>")
            table.clear()
    for line in text.splitlines():
        if line.startswith("|"):
            if para:
                flush()
            table.append(line)
            continue
        if table:
            flush()
        if m := re.match(r"^(#{1,4})\s+(.*)", line):
            flush()
            lvl = min(len(m.group(1)) + 1, 4)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
        elif m := re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*)", line):
            flush()
            out.append(f"<li>{inline(m.group(1))}</li>")
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out)


def _page(title, body, diagrams=False):
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{_e(title)}</title><style>{CSS}</style></head><body><div class=wrap>{body}"
            f"<footer>Generated by ontokit on {dt.date.today().isoformat()} from the graded model. Grades: "
            + " · ".join(f"{k} {v.lower()}" for k, v in GRADE_TEXT.items()) + f"</footer></div><script>{JS}</script>"
            + (MERMAID_JS if diagrams else "") + "</body></html>")


def agent_html(paths, c, key, name, question, about, diags, secs, files) -> str:
    toc = "".join(f'<a class=pill href="#s{i}">{_e(s["title"])} ({len(s["rows"])})</a>' for i, s in enumerate(secs))
    dl = " ".join(f'<a class=pill href="{_e(f)}">{lbl}</a>' for lbl, f in files)
    body = [f'<p class=eyebrow><a href="index.html">← All agents</a> · {_e(paths.loop)}</p><h1>{_e(name)}</h1>',
            f'<p class=lead><b>{_e(question)}</b> {_e(about)}</p><div class=bar>{dl}</div><nav class=toc>{toc}</nav>']
    shown = [d for d in diags if d in c["diagrams"]]
    if shown:
        body.append("<section><h2>Diagrams</h2><p class=muted>Generated from the evidence; colours show grade.</p>")
        for d in shown:
            body.append(f'<h3 class=muted>{_e(d)}</h3><div class=diag><pre class="mermaid">{_e(c["diagrams"][d])}</pre></div>')
        body.append("</section>")
    for i, s in enumerate(secs):
        tid = f"t{i}"
        body.append(f'<section id="s{i}"><h2>{_e(s["title"])} <span class=muted>({len(s["rows"])})</span></h2><p class=lead>{_e(s["intro"])}</p>')
        if s["rows"]:
            body.append(f'<input class=f data-t="{tid}" placeholder="Filter {len(s["rows"])} rows" aria-label="Filter {_e(s["title"])}">'
                        f'<div class=tw><table id="{tid}"><thead><tr>' + "".join(f"<th>{_e(col)}</th>" for col in s["columns"])
                        + "</tr></thead><tbody>" + "".join("<tr>" + "".join(_cell(col, v) for col, v in zip(s["columns"], r)) + "</tr>"
                                                          for r in s["rows"]) + "</tbody></table></div>")
        else:
            body.append("<p class=muted>None in this loop.</p>")
        body.append("</section>")
    if key in c["notes"]:
        body.append(f'<section><h2>{"Steward review notes" if key == "steward" else "Conformance briefing"}</h2>'
                    f'<div class=notes>{_md(c["notes"][key])}</div></section>')
    if key == "steward" and c["agent_notes"]:
        body.append(f'<section><h2>Observations from the specialist agents</h2><div class=notes>{_md(c["agent_notes"])}</div></section>')
    return _page(f"{name} · {paths.loop}", "\n".join(body), diagrams=bool(shown))


# ------------------------------------------------------------------ Excel and Word

def _xlsx(path, name, loop, secs) -> bool:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError:
        return False
    wb = Workbook()
    ws = wb.active
    ws.title = "About"
    ws.append([f"{name} · {loop}"])
    ws["A1"].font = Font(bold=True, size=14)
    ws.append(["Generated by ontokit from the graded model. One sheet per table; every row has its grade and evidence."])
    ws.append([])
    ws.append(["Grade", "Meaning"])
    for k, v in GRADE_TEXT.items():
        ws.append([k, v])
        ws.cell(ws.max_row, 1).fill = PatternFill("solid", fgColor=GRADE_FILL[k])
    ws.append([])
    ws.append(["Sheet", "Rows"])
    for s in secs:
        ws.append([s["title"], len(s["rows"])])
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 34, 60
    used = set()
    for s in secs:
        t = re.sub(r"[\[\]:*?/\\]", "", s["title"])[:31]
        while t in used:
            t = t[:29] + "_" + str(len(used))
        used.add(t)
        sh = wb.create_sheet(t)
        sh.append(s["columns"])
        for cell in sh[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="3A4AA8")
        for r in s["rows"]:
            sh.append([v if isinstance(v, (int, float)) else ("" if v is None else str(v)) for v in r])
        if "Grade" in s["columns"]:
            gi = s["columns"].index("Grade") + 1
            for row in sh.iter_rows(min_row=2, min_col=gi, max_col=gi):
                for cell in row:
                    if cell.value in GRADE_FILL:
                        cell.fill = PatternFill("solid", fgColor=GRADE_FILL[cell.value])
        for i, col in enumerate(s["columns"], 1):
            longest = max([len(str(col))] + [len(str(r[i - 1])) for r in s["rows"][:200]])
            sh.column_dimensions[get_column_letter(i)].width = max(8, min(60, longest + 2))
        for row in sh.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        sh.freeze_panes = "B2"
        if s["rows"]:
            sh.auto_filter.ref = sh.dimensions
    wb.save(path)
    return True


def _docx(path, name, question, about, loop, org, secs, diags, notes) -> bool:
    try:
        from docx import Document
        from docx.enum.section import WD_ORIENT
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Pt
    except ImportError:
        return False
    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = sec.page_height, sec.page_width
    doc.styles["Normal"].font.size = Pt(10)
    doc.add_heading(f"{name} report", 0)
    doc.add_paragraph(f"{org or ''} · discovery {loop} · generated {dt.date.today().isoformat()}").italic = True
    doc.add_paragraph().add_run(question).bold = True
    doc.add_paragraph(about)
    doc.add_heading("Summary", 1)
    for s in secs:
        doc.add_paragraph(f"{s['title']}: {len(s['rows'])}", style="List Bullet")
    doc.add_paragraph("Grades: " + "; ".join(f"{k} = {v.lower()}" for k, v in GRADE_TEXT.items()) + ".")
    if diags:
        doc.add_heading("Diagrams", 1)
        doc.add_paragraph("The diagrams for this agent are rendered in the HTML report and stored as Mermaid files: "
                          + ", ".join(f"diagrams/{d}.mmd" for d in diags) + ".")
    for s in secs:
        doc.add_heading(s["title"], 1)
        doc.add_paragraph(s["intro"])
        if not s["rows"]:
            doc.add_paragraph("None in this loop.")
            continue
        cols = [c for c in s["columns"] if c != "Evidence"]
        idx = [s["columns"].index(c) for c in cols]
        t = doc.add_table(rows=1, cols=len(cols))
        t.style = "Table Grid"
        for i, c in enumerate(cols):
            cell = t.rows[0].cells[i]
            cell.text = c
            cell.paragraphs[0].runs[0].bold = True
            shd = OxmlElement("w:shd")
            shd.set(qn("w:fill"), "E6E9F7")
            cell._tc.get_or_add_tcPr().append(shd)
        for r in s["rows"]:
            cells = t.add_row().cells
            for i, j in enumerate(idx):
                v = r[j]
                cells[i].text = "" if v is None else str(v)
                if s["columns"][j] == "Grade" and str(v) in GRADE_FILL:
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:fill"), GRADE_FILL[str(v)])
                    cells[i]._tc.get_or_add_tcPr().append(shd)
    if notes:
        doc.add_heading("Review notes", 1)
        for line in notes.splitlines():
            m = re.match(r"^(#{1,4})\s+(.*)", line)
            if m:
                doc.add_heading(m.group(2), min(len(m.group(1)) + 1, 4))
            elif re.match(r"^\s*[-*]\s+", line):
                doc.add_paragraph(re.sub(r"^\s*[-*]\s+", "", line).replace("**", ""), style="List Bullet")
            elif line.strip() and not line.startswith("|"):
                doc.add_paragraph(line.replace("**", ""))
    doc.save(path)
    return True


# ------------------------------------------------------------------ publish

def publish(paths: LoopPaths, trace: Trace) -> Path:
    c = _ctx(paths)
    out = paths.outputs / "reports"
    out.mkdir(parents=True, exist_ok=True)
    stt_f = paths.outputs / "decomposition" / "source-to-target.csv"
    if stt_f.exists():
        import csv
        c["stt"] = list(csv.reader(stt_f.read_text(encoding="utf-8").splitlines()))
    org = read_json(paths.work / "sources.json").get("organisation")
    made, office = [], True
    for key, name, question, about, diags in AGENTS:
        secs = sections(key, c)
        x = _xlsx(out / f"{key}.xlsx", name, paths.loop, secs)
        w = _docx(out / f"{key}.docx", name, question, about, paths.loop, org, secs, [d for d in diags if d in c["diagrams"]],
                  c["notes"].get(key))
        office = office and x and w
        files = [("Excel workbook", f"{key}.xlsx")] * x + [("Word document", f"{key}.docx")] * w + \
                [("Diagram files", "../diagrams/README.md")] * bool([d for d in diags if d in c["diagrams"]])
        (out / f"{key}.html").write_text(agent_html(paths, c, key, name, question, about, diags, secs, files), encoding="utf-8")
        made.append((key, name, question, about, diags, secs, x, w))
    (out / "index.html").write_text(_index(paths, c, made, office), encoding="utf-8")
    _root_index(paths)
    trace.emit("M. Reports", "Publisher", "report packs written",
               f"{len(made)} agents × HTML" + (", Excel, Word" if office else " (Excel/Word skipped: pip install openpyxl python-docx)")
               + "; index at reports/index.html")
    return out / "index.html"


def _index(paths, c, made, office) -> str:
    g = Counter(e["grade"] for e in c["els"])
    total = len(c["els"])
    high = [u for u in c["unknowns"] if u["priority"] == "high"]
    gates = " ".join(f'<span class=pill>Phase {ph["phase"]}: <b>{ph["status"]}</b></span>' for ph in c["gates"])
    org = read_json(paths.work / "sources.json").get("organisation") or "Discovery"
    o = paths.outputs
    others = [(lbl, f) for lbl, f in [
        ("Loop summary", "../summary.md"), ("As-is ontology (LinkML)", "../as-is-ontology.yaml"), ("Glossary", "../glossary.md"),
        ("System inventory", "../system-inventory.md"), ("Unknowns register", "../unknowns-register.md"),
        ("Jira-ready questions", "../jira-issues.json"), ("Gate report", "../gate-report.md"),
        ("Change register", "../change-register.md"), ("Agent notes", "../agent-notes.md"), ("All diagrams", "../diagrams/README.md"),
        ("Evidence register (JSON)", "../evidence-register.json"), ("Decomposition report", "../decomposition/decomposition-report.md"),
        ("Source-to-target mapping", "../decomposition/source-to-target.csv"), ("Comparison: live vs simulated", "../live-vs-simulated.md"),
        ("Stand-in schemas", "../standins/")] if (o / f.replace("../", "")).exists()]
    if (o / "decomposition" / "domains").exists():
        others += [(f"Domain ontology: {p.stem}", f"../decomposition/domains/{p.name}") for p in sorted((o / "decomposition" / "domains").glob("*.yaml"))]
        others += [(f"Service contract: {p.name.split('.')[0]}", f"../decomposition/services/{p.name}") for p in sorted((o / "decomposition" / "services").glob("*.yaml"))]
    cards = []
    for key, name, question, about, diags, secs, x, w in made:
        n = " · ".join(f"{len(s['rows'])} {s['title'].lower()}" for s in secs[:3])
        links = [f'<a class=pill href="{key}.html"><b>Open report</b></a>'] + \
                ([f'<a class=pill href="{key}.xlsx">Excel</a>'] if x else []) + ([f'<a class=pill href="{key}.docx">Word</a>'] if w else []) + \
                [f'<a class=pill href="../diagrams/{d}.mmd">{_e(d)}</a>' for d in diags if d in c["diagrams"]]
        cards.append(f'<div class=card><span class=eyebrow>Agent</span><h2><a href="{key}.html">{_e(name)}</a></h2>'
                     f'<p class=muted style="margin:0"><b>{_e(question)}</b> {_e(about)}</p><p style="margin:0;font-size:.85rem">{_e(n)}</p>'
                     f'<div class=bar>{"".join(links)}</div></div>')
    toc = "".join(f'<a class=pill href="{k}.html">{_e(nm)}</a>' for k, nm, *_ in made)
    body = f"""<p class=eyebrow><a href="../../index.html">All loops</a> · {_e(org)} · {_e(paths.loop)}</p>
<h1>Ontology discovery results</h1>
<p class=lead>Everything the agents produced in {_e(paths.loop)}: one report per agent, as an HTML explainer, an Excel workbook and a Word
document, plus diagrams and every other output. Agents recommend; named people approve.</p>
<nav class=toc>{toc}</nav>
<section><h2>At a glance</h2><div class=stats>
<div class=stat><b>{len(c['sources'])}</b><span class=muted>source files</span></div>
<div class=stat><b>{total}</b><span class=muted>elements</span></div>
<div class=stat><b>{sum(1 for e in c['els'] if e['conflicts'])}</b><span class=muted>contradictions</span></div>
<div class=stat><b>{len(c['unknowns'])}</b><span class=muted>open questions ({len(high)} high)</span></div>
<div class=stat><b>{len((c['dec'] or {}).get('domains', [])) or '—'}</b><span class=muted>target domains</span></div></div>
{_gbar(g, total)}<p class=muted style="margin:0">{' · '.join(f'<span class="g g-{k}">{k}</span> {g.get(k, 0)} {GRADE_TEXT[k].lower()}' for k in 'ABCDX')}</p>
<div class=bar>{gates}</div></section>
<section><h2>Agent reports</h2>{'' if office else '<p class=muted>Excel and Word files were not produced because openpyxl and python-docx are not installed. Run <code>pip install openpyxl python-docx</code>, then <code>python -m ontokit reports --root ... --loop ...</code>.</p>'}
<div class=cards>{''.join(cards)}</div></section>
<section><h2>Highest-priority questions</h2><div class=tw><table><thead><tr><th>ID</th><th>Question</th><th>Owner</th></tr></thead><tbody>
{''.join(f"<tr><td>{_e(u['id'])}</td><td>{_e(u['question'])}</td><td>{_e(u['owner'])}</td></tr>" for u in high) or '<tr><td colspan=3>None</td></tr>'}
</tbody></table></div><p class=muted>All questions: <a href="steward.html#s0">Ontology Steward report</a>.</p></section>
<section><h2>All other outputs</h2><div class=bar>{''.join(f'<a class=pill href="{_e(f)}">{_e(l)}</a>' for l, f in others)}</div></section>"""
    return _page(f"Discovery results · {paths.loop}", body)


def _root_index(paths) -> None:
    root = paths.outputs.parent
    loops = sorted(p.name for p in root.iterdir() if (p / "reports" / "index.html").exists())
    rows = []
    for l in loops:
        s = (root / l / "summary.md").read_text(encoding="utf-8").splitlines() if (root / l / "summary.md").exists() else []
        rows.append(f'<div class=card><h2><a href="{l}/reports/index.html">{_e(l)}</a></h2>'
                    + "".join(f"<p class=muted style='margin:0'>{_e(x.lstrip('- '))}</p>" for x in s if x.startswith("- "))
                    + "</div>")
    (root / "index.html").write_text(_page("Discovery results", "<h1>Discovery results</h1><p class=lead>One page per evidence loop. "
                                           "Open a loop to reach every agent's report, workbook, document and diagrams.</p>"
                                           f"<div class=cards>{''.join(rows)}</div>"), encoding="utf-8")

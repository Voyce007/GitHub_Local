"""Architecture drill-down: domains → business services → data, calculations and technical services.

Built from a decomposition (a root with target_domains.yaml). For every business service:
  data          the entities (and their tables and attributes) the service changes, reads or returns
  calculations  the batch jobs and stored procedures that implement it in the monolith today
  technical     the target technical service: an API operation (command or query) or an event,
                and where it runs today (program, system, schedule)
Produces:
  * diagrams/aggregate-architecture.mmd, one diagram for all domains (via diagrams.py)
  * reports/architecture.html, an interactive drill-down: all domains, then one domain, then one service
"""
from __future__ import annotations

import json
from collections import defaultdict

from .common import human, norm, tokens


def _kebab(s: str) -> str:
    return "-".join(tokens(s))


def _id(s: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_]", "_", s)


def _lbl(s) -> str:
    return str(s).replace('"', "'").replace("[", "(").replace("]", ")").replace("|", "/")


def build(model: dict, sources: dict) -> dict | None:
    dec = model.get("decomposition")
    if not dec:
        return None
    els = model["elements"]
    by_id = {e["id"]: e for e in els}
    ents = {e["name"]: e for e in els if e["kind"] == "entity" and e["origin"] != "assumed"}
    by_table = {e["properties"].get("physical", "").upper(): e for e in ents.values() if e["properties"].get("physical")}
    calcs = {e["name"]: e for e in els if e["kind"] == "calculation"}
    names = {d["key"]: d["name"] for d in dec["domains"]}

    def ent_info(e):
        attrs = []
        for aid in e["properties"].get("attribute_ids", []):
            a = by_id.get(aid)
            if a:
                p = a["properties"]
                attrs.append({"name": p.get("attribute"), "column": p.get("physical", ""), "type": p.get("data_type", ""),
                              "grade": a["grade"], "domain": p.get("domain"), "moved": bool(p.get("split_from"))})
        return {"id": e["id"], "name": e["name"], "table": e["properties"].get("physical", ""), "domain": e["properties"].get("domain"),
                "grade": e["grade"], "basis": e["properties"].get("domain_basis", ""), "attributes": attrs}

    def calc_info(c):
        p = c["properties"]
        systems = sorted({sources.get(x["file"], {}).get("system_hint") for x in c["evidence"]} - {None})
        return {"id": c["id"], "program": c["name"], "title": p.get("title") or c["name"], "domain": p.get("domain"),
                "reads": p.get("reads", []), "writes": p.get("writes", []), "columns": p.get("writes_columns", []),
                "frequency": p.get("frequency", ""), "job": p.get("job_id", ""), "team": p.get("owner_team", ""),
                "system": ", ".join(systems) or "the monolith", "grade": c["grade"]}

    domains = []
    for d in dec["domains"]:
        k = d["key"]
        services = []
        for s in dec["services"][k]:
            data, cl = [], []
            if s["type"] == "command":
                cl = [calcs[n] for n in s.get("calculations", []) if n in calcs]
                for c in cl:
                    for t in c["properties"].get("writes", []):
                        if (e := by_table.get(t.upper())):
                            data.append((e["name"], "changes"))
                    for t in c["properties"].get("reads", []):
                        if (e := by_table.get(t.upper())) and (e["name"], "changes") not in data:
                            data.append((e["name"], "reads"))
                tech = {"kind": "API", "method": "POST", "path": f"/{_kebab(s['name'])}", "summary": "Changes data owned by this domain"}
            elif s["type"] == "query":
                ret = s.get("returns", "")
                if ret in ents:
                    data.append((ret, "returns"))
                    cl = [c for c in calcs.values() if c["properties"].get("domain") == k and any(
                        by_table.get(t.upper(), {}).get("name") == ret for t in c["properties"].get("writes", []))]
                else:   # a moved column, e.g. the NI Number
                    sp = next((x for x in dec.get("splits", []) if x.get("attribute") == ret), None)
                    if sp:
                        data.append((sp["entity"], f"returns {sp['column']}"))
                        cl = [calcs[sp["calculation"]]] if sp["calculation"] in calcs else []
                tech = {"kind": "API", "method": "GET", "path": f"/{_kebab(ret)}/{{id}}", "summary": f"Lets other domains read {ret}"}
            else:
                for r in s.get("replaces", []):
                    prog, _, ent = r.partition(" writing ")
                    if ent in ents:
                        data.append((ent, "triggers change in"))
                    if prog in calcs and calcs[prog] not in cl:
                        cl.append(calcs[prog])
                tech = {"kind": "Event", "method": "PUBLISH", "path": s["name"], "summary": "Other domains react with their own services"}
            seen, uniq = set(), []
            for n, acc in data:
                if (n, acc) not in seen:
                    seen.add((n, acc))
                    uniq.append({"entity": n, "access": acc, "owner": ents[n]["properties"].get("domain") if n in ents else None})
            services.append({"name": s["name"], "type": s["type"], "grade": s.get("grade"),
                             "consumers": [names[x] for x in s.get("consumers", [])], "data": uniq,
                             "calcs": [calc_info(c) for c in cl], "technical": tech})
        deps_out = [dd for dd in dec["dependencies"] if dd["consumer"] == k]
        deps_in = [dd for dd in dec["dependencies"] if dd["provider"] == k]
        domains.append({"key": k, "name": d["name"], "owner": d.get("owner", ""),
                        "entities": [ent_info(e) for e in ents.values() if e["properties"].get("domain") == k],
                        "services": services,
                        "depends_on": [{"domain": names[x["provider"]], "data": x["entities"]} for x in deps_out],
                        "used_by": [{"domain": names[x["consumer"]], "data": x["entities"]} for x in deps_in]})
    arch = {"monolith": dec.get("monolith"), "domains": domains, "ents": {n: ent_info(e) for n, e in ents.items()}}
    for d in domains:
        d["diagram"] = mermaid(arch, [d["key"]])
    arch["diagram"] = mermaid(arch, None)
    return arch


SHAPE = {"command": ('["', '"]'), "query": ('(["', '"])'), "event": ('[["', '"]]')}


def mermaid(arch: dict, only: list[str] | None) -> str:
    """All domains (only=None) or one domain; each domain box holds its technical services, business services,
    today's calculations and the data it owns. Data owned by a domain not drawn is shown dashed, outside."""
    L = ["flowchart LR"]
    grades, edges, ext = defaultdict(list), [], {}
    doms = [d for d in arch["domains"] if only is None or d["key"] in only]
    drawn = {d["key"] for d in doms}
    by_table = {e["table"].upper(): e for e in arch["ents"].values() if e["table"]}
    calc_dom = {}
    for d in arch["domains"]:
        for s in d["services"]:
            for c in s["calcs"]:
                calc_dom.setdefault(c["program"], (c.get("domain") or d["key"], c))

    def ent_ref(name):
        e = arch["ents"].get(name)
        if e and e["domain"] not in drawn:
            ext[name] = e
        return f"E_{_id(name)}"

    for d in doms:
        k = d["key"]
        L.append(f'  subgraph D_{_id(k)}["{_lbl(d["name"])} · {_lbl(d["owner"])}"]')
        L.append("    direction LR")
        for i, s in enumerate(d["services"]):
            sid, aid = f"S_{_id(k)}_{i}", f"A_{_id(k)}_{i}"
            o, c = SHAPE[s["type"]]
            L.append(f'    {aid}>"{_lbl(s["technical"]["method"])} {_lbl(s["technical"]["path"])}"]')
            L.append(f'    {sid}{o}<b>{_lbl(s["name"])}</b>{c}')
            edges.append(f"  {aid} --- {sid}")
            if s.get("grade"):
                grades[s["grade"]].append(sid)
            for cc in s["calcs"]:
                edges.append(f"  {sid} -. today .-> C_{_id(cc['program'])}")
            if not s["calcs"]:
                for dd in s["data"]:
                    edges.append(f'  {sid} -->|"{_lbl(dd["access"])}"| {ent_ref(dd["entity"])}')
            if s["type"] == "event":
                for dd in s["data"]:
                    edges.append(f'  {sid} -. "{_lbl(dd["access"])}" .-> {ent_ref(dd["entity"])}')
        for prog, (ck, cc) in calc_dom.items():
            if ck == k:
                L.append(f'    C_{_id(prog)}{{{{"{_lbl(cc["title"])}<br/><small>{_lbl(prog)} · {_lbl(cc["system"])}</small>"}}}}')
                grades[cc["grade"]].append(f"C_{_id(prog)}")
        for e in d["entities"]:
            L.append(f'    E_{_id(e["name"])}[("{_lbl(human(e["name"]))}<br/><small>{_lbl(e["table"])}</small>")]')
            grades[e["grade"]].append(f"E_{_id(e['name'])}")
        L.append("  end")
    for prog, (ck, cc) in calc_dom.items():
        if ck not in drawn:
            if not any(f"C_{_id(prog)}" in x for x in edges):
                continue
            L.append(f'  C_{_id(prog)}{{{{"{_lbl(cc["title"])}<br/><small>{_lbl(prog)}, another domain</small>"}}}}')
        for t in cc["writes"]:
            if (e := by_table.get(t.upper())):
                cols = [x.split(".", 1)[1] for x in cc["columns"] if x.upper().startswith(t.upper() + ".")]
                edges.append(f"  C_{_id(prog)} ==>" + (f'|"{_lbl(", ".join(cols))}"|' if cols else "") + f" {ent_ref(e['name'])}")
        for t in cc["reads"]:
            if t not in cc["writes"] and (e := by_table.get(t.upper())):
                edges.append(f"  {ent_ref(e['name'])} -.-> C_{_id(prog)}")
    for name, e in ext.items():
        L.append(f'  E_{_id(name)}[("{_lbl(human(name))}<br/><small>owned by another domain</small>")]')
    L += edges
    L.append("  classDef ext fill:#ffffff,stroke:#8a93a3,stroke-dasharray:5 4,color:#5a6372")
    L.append("  classDef gA fill:#1d7a4426,stroke:#1d7a44,stroke-width:2px")
    L.append("  classDef gB fill:#2867a026,stroke:#2867a0,stroke-width:2px")
    L.append("  classDef gC fill:#9a621026,stroke:#9a6210,stroke-width:1.5px,stroke-dasharray:4 3")
    L.append("  classDef gD fill:#6b748326,stroke:#6b7483,stroke-dasharray:2 3")
    L.append("  classDef gX fill:#b2382426,stroke:#b23824,stroke-width:2.5px")
    ext_ids = {f"E_{_id(n)}" for n in ext}
    for g, ids in grades.items():
        ids = sorted(set(ids) - ext_ids)
        if g and ids:
            L.append(f"  class {','.join(ids)} g{g}")
    if ext_ids:
        L.append(f"  class {','.join(sorted(ext_ids))} ext")
    return "\n".join(L)


# ------------------------------------------------------------------ HTML page

PAGE_CSS = """
.tabs{display:flex;flex-wrap:wrap;gap:8px}.tabs button{font:600 .95rem system-ui,sans-serif;padding:8px 16px;border-radius:10px;
border:2px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}.tabs button[aria-pressed=true]{border-color:var(--accent);
background:var(--accent-soft);color:var(--accent)}.dhead{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
.svcs{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px}.svcs button{text-align:left;font:inherit;padding:10px 12px;
border-radius:10px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;display:grid;gap:2px}
.svcs button[aria-pressed=true]{border:2px solid var(--accent);background:var(--accent-soft)}.svcs small{color:var(--muted)}
.t{justify-self:start;display:inline-block;font:600 .7rem ui-monospace,Menlo,monospace;letter-spacing:.05em;text-transform:uppercase;padding:1px 6px;border-radius:5px;
background:var(--sunk);color:var(--muted)}.detail{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
@media (max-width:900px){.detail{grid-template-columns:1fr}}.detail .card h3{font-size:1rem}.item{border-top:1px solid var(--line);padding-top:8px;display:grid;gap:3px}
.item b{font-size:.92rem}.item small{color:var(--muted)}code.op{font:600 .9rem ui-monospace,Menlo,monospace;background:var(--sunk);padding:2px 8px;border-radius:6px}
details.attrs summary{cursor:pointer;color:var(--accent);font-size:.82rem}details.attrs table{font-size:.78rem}
.crumbs{font-size:.9rem;color:var(--muted)}.crumbs b{color:var(--ink)}
"""

PAGE_JS = r"""
(function(){
const A = JSON.parse(document.getElementById('arch').textContent);
const $ = s => document.querySelector(s), esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const g = x => x ? `<span class="g g-${x}">${x}</span>` : '';
const dn = k => (A.domains.find(d => d.key === k) || {}).name || 'another domain';
let cur = null, svc = 0, seq = 0;
function tabs(){ $('#tabs').innerHTML = A.domains.map(d => `<button type=button data-k="${d.key}" aria-pressed="${d.key === cur}">${esc(d.name)}</button>`).join(''); }
async function drawDomain(d){
  const box = $('#ddiag');
  box.innerHTML = `<div class=dtools hidden><button type=button data-z="-" aria-label="Zoom out">−</button><button type=button data-z="+" aria-label="Zoom in">+</button><button type=button data-z="fit">Fit</button><button type=button data-z="1">100%</button><button type=button data-z="fs">Full screen</button><span class=zl>100%</span><span class=hint>Drag to pan · Ctrl/⌘ + wheel to zoom</span></div><div class=dview tabindex=0></div>`;
  const view = box.querySelector('.dview');
  if (!window.mermaid) { view.innerHTML = `<pre class=raw>${esc(d.diagram)}</pre>`; return; }
  try { const { svg } = await mermaid.render('dd' + (++seq), d.diagram); view.innerHTML = svg; if (window.zoomViewer) zoomViewer(box); }
  catch (e) { view.innerHTML = `<pre class=raw>${esc(d.diagram)}</pre>`; }
}
function showDomain(k){
  cur = k; svc = 0; tabs(); const d = A.domains.find(x => x.key === k);
  try { history.replaceState(null, '', '#' + k); } catch (e) {}
  $('#dname').textContent = d.name;
  $('#dsum').innerHTML = `<div class=card><span class=eyebrow>Owner</span><b>${esc(d.owner)}</b></div>
    <div class=card><span class=eyebrow>Owns</span><span>${d.entities.map(e => esc(e.name.replace(/([a-z])([A-Z])/g,'$1 $2')) + ' ' + g(e.grade)).join(', ') || '—'}</span></div>
    <div class=card><span class=eyebrow>Depends on</span><span>${d.depends_on.map(x => `${esc(x.domain)} <small class=muted>(${esc(x.data.join(', '))})</small>`).join('<br>') || 'nothing'}</span></div>
    <div class=card><span class=eyebrow>Used by</span><span>${d.used_by.map(x => `${esc(x.domain)} <small class=muted>(${esc(x.data.join(', '))})</small>`).join('<br>') || 'nobody'}</span></div>`;
  drawDomain(d); services(d);
}
function services(d){
  $('#svcs').innerHTML = d.services.map((s, i) => `<button type=button data-i="${i}" aria-pressed="${i === svc}"><span class=t>${s.type}</span><b>${esc(s.name)}</b><small>${esc(s.technical.method)} ${esc(s.technical.path)}</small></button>`).join('');
  detail(d, d.services[svc]);
}
function entCard(x){
  const e = A.ents[x.entity]; const own = x.owner === cur ? '' : ` <small class=muted>owned by ${esc(dn(x.owner))}, read through its service</small>`;
  if (!e) return `<div class=item><b>${esc(x.entity)}</b><small>${esc(x.access)}</small></div>`;
  return `<div class=item><b>${esc(x.entity.replace(/([a-z])([A-Z])/g,'$1 $2'))} ${g(e.grade)}</b><small>${esc(x.access)} · table <code>${esc(e.table)}</code>${own}</small>
    <details class=attrs><summary>${e.attributes.length} attributes</summary><div class=tw><table><thead><tr><th>Attribute</th><th>Column</th><th>Type</th><th>Grade</th></tr></thead><tbody>
    ${e.attributes.map(a => `<tr><td>${esc(a.name)}${a.moved ? ' <span class=t>moves to ' + esc(dn(a.domain)) + '</span>' : ''}</td><td>${esc(a.column)}</td><td>${esc(a.type)}</td><td>${g(a.grade)}</td></tr>`).join('')}</tbody></table></div></details></div>`;
}
function detail(d, s){
  if (!s) { $('#detail').innerHTML = ''; return; }
  $('#crumb').innerHTML = `All domains › <b>${esc(d.name)}</b> › <b>${esc(s.name)}</b>`;
  $('#detail').innerHTML = `
  <div class=card><span class=eyebrow>Data</span><h3>What it changes, reads or returns</h3>${s.data.map(entCard).join('') || '<p class=muted>None found in the evidence.</p>'}</div>
  <div class=card><span class=eyebrow>Calculations</span><h3>What implements it today</h3>${s.calcs.map(c => `<div class=item><b>${esc(c.title)} ${g(c.grade)}</b>
    <small><code>${esc(c.program)}</code>${c.job ? ' · job ' + esc(c.job) : ''} · runs in ${esc(c.system)}${c.frequency ? ' · ' + esc(c.frequency) : ''}</small>
    <small>Changes: ${esc(c.writes.join(', ') || '—')}${c.columns.length ? ' (' + esc(c.columns.join(', ')) + ')' : ''}</small><small>Reads: ${esc(c.reads.join(', ') || '—')}</small></div>`).join('') || '<p class=muted>No calculation found. This service is new, or its implementation is not in the evidence.</p>'}</div>
  <div class=card><span class=eyebrow>Technical service</span><h3>What it becomes on the access layer</h3>
    <div class=item><b>${esc(s.technical.kind)}</b><span><code class=op>${esc(s.technical.method)} ${esc(s.technical.path)}</code></span><small>${esc(s.technical.summary)}</small></div>
    <div class=item><b>Used by</b><small>${esc(s.consumers.join(', ') || (s.type === 'command' ? 'channels and staff of this domain' : '—'))}</small></div>
    <div class=item><b>Contract</b><small><a href="../decomposition/services/${esc(cur)}.openapi.yaml">${esc(cur)}.openapi.yaml</a></small></div></div>`;
}
document.addEventListener('click', e => {
  const t = e.target.closest('#tabs button'); if (t) { showDomain(t.dataset.k); return; }
  const b = e.target.closest('#svcs button'); if (b) { const d = A.domains.find(x => x.key === cur); svc = +b.dataset.i; services(d);
    $('#detail').scrollIntoView({ behavior: 'smooth', block: 'start' }); }
});
window.addEventListener('load', () => { const h = location.hash.slice(1); showDomain(A.domains.some(d => d.key === h) ? h : A.domains[0].key); });
})();
"""


def page(paths, arch, page_fn, esc) -> str:
    n_svc = sum(len(d["services"]) for d in arch["domains"])
    n_calc = len({c["program"] for d in arch["domains"] for s in d["services"] for c in s["calcs"]})
    body = f"""<p class=eyebrow><a href="index.html">← All agent reports</a> · {esc(paths.loop)}</p>
<h1>Architecture drill-down</h1>
<p class=lead>{len(arch['domains'])} domains carved out of {esc(arch['monolith'])}, with {n_svc} business services. Each service drills down to the
<b>data</b> it changes or reads, the <b>calculations</b> that implement it today ({n_calc} programs), and the <b>technical service</b> it becomes
on the access layer. Colours show evidence grade; dashed data belongs to another domain.</p>
<section><h2>1 · All domains</h2><p class=muted>Read left to right: technical service → business service → today's calculation → data.
Thick arrows change data; dotted arrows read it.</p>
<div class=diag><div class=dtools hidden><button type=button data-z="-" aria-label="Zoom out">−</button><button type=button data-z="+" aria-label="Zoom in">+</button>
<button type=button data-z="fit">Fit</button><button type=button data-z="1">100%</button><button type=button data-z="fs">Full screen</button><span class=zl>100%</span>
<span class=hint>Drag to pan · Ctrl/⌘ + wheel to zoom · drag the corner to resize</span></div>
<div class=dview tabindex=0 aria-label="All domains diagram"><pre class="mermaid">{esc(arch['diagram'])}</pre></div></div></section>
<section><h2>2 · One domain</h2><div class=tabs id=tabs role=group aria-label="Choose a domain"></div>
<h3 id=dname></h3><div class=dhead id=dsum></div><div class=diag id=ddiag></div></section>
<section><h2>3 · One business service</h2><p class=muted>Choose a service to see its data, calculations and technical service.</p>
<div class=svcs id=svcs></div><p class=crumbs id=crumb></p><div class=detail id=detail></div></section>
<style>{PAGE_CSS}</style>
<script id=arch type="application/json">{json.dumps({k: v for k, v in arch.items() if k != 'diagram'}, ensure_ascii=False).replace('</', '<\\/')}</script>
<script>{PAGE_JS}</script>"""
    return page_fn(f"Architecture drill-down · {paths.loop}", body, diagrams=True)

"""Stage B — Simulated persona agents (deterministic, no LLM).

Each function reads the source index and returns proposals in exactly the
format the live Claude Code subagents write (schemas/proposal.schema.json).
They use parsers and patterns, so they only find what is written in a
recognisable form. Live agents replace them for real material; everything
downstream (validator, steward, grading, gates) is identical in both modes.

Evidence entries carry a `support` hint the grader uses:
  definition | structure | value-list | reference | mention
"""
from __future__ import annotations

import csv
import io
import re

from .common import LoopPaths, Trace, camel, const, human, norm, pascal, read_json, write_json

# ---------------------------------------------------------------- helpers

def _ev(file: str, lineno: int, line: str, support: str) -> dict:
    return {"file": file, "locator": f"line {lineno}", "quote": line.strip(), "support": support}


def _prop(kind: str, name: str, file: str, lineno: int, line: str, support: str, **kw) -> dict:
    p = {"kind": kind, "name": name, "evidence": [_ev(file, lineno, line, support)], "origin": "inferred"}
    for k in ("aliases", "definition", "notes", "confidence"):
        if k in kw:
            p[k] = kw.pop(k)
    if kw:
        p["properties"] = kw
    return p


def _files(index: dict, *, provenance=None, doc_type=None, suffix=None):
    for rel, src in index["sources"].items():
        if provenance and src["provenance"] not in provenance:
            continue
        if doc_type and src.get("doc_type") not in doc_type:
            continue
        if suffix and not rel.endswith(suffix):
            continue
        yield rel, src


def _csv_rows(src: dict):
    """Yield (line_number, raw_line, row_dict) for a CSV source."""
    lines = src["lines"]
    reader = csv.DictReader(io.StringIO("\n".join(lines)))
    for i, row in enumerate(reader, start=2):
        yield i, lines[i - 1], row


PROSE = ("document", "wiki", "sme-answer")

# ---------------------------------------------------------------- EA agent

SYS_PAREN = re.compile(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)+|[A-Z]{2,})\s*\(([^)]*)\)")
CHANNELS = re.compile(r"\bChannel \(([^)]+)\)")
REFERRED = re.compile(r"[Tt]he ([\w ]+?) is referred to as ([A-Z]{2,})")
ROLE_PATTERNS = [
    (re.compile(r"holds the (\w+) (?:record|register)"), lambda m: f"system of record (candidate): {m.group(1).capitalize()}"),
    (re.compile(r"raises (\w+?)s?\b"), lambda m: f"system of record (candidate): {m.group(1).capitalize()}"),
    (re.compile(r"maintains the ([\w ]+?)[.]"), lambda m: f"system of record (candidate): {m.group(1)}"),
    (re.compile(r"processes all ([\w ]+?)[.]"), lambda m: f"processing: {m.group(1)}"),
    (re.compile(r"captures and fulfils ([\w -]+?)[.]"), lambda m: f"processing: {m.group(1)}"),
    (re.compile(r"\ballocates ([\w ]+?)[.]"), lambda m: f"system of record (candidate): {m.group(1)}"),
    (re.compile(r"calculates ([\w ]+?)[.]"), lambda m: f"calculation: {m.group(1)}"),
]
CAPABILITY = re.compile(r"^- \*\*(.+?)\*\*: (.+?) Owner: (.+?)\.$")
MERMAID_NODE = re.compile(r'(\w+)\["([^"]+)"\]')
MERMAID_EDGE = re.compile(r'^\s*(\w+)(?:\["[^"]*"\])?\s*-->\|([^|]+)\|\s*(\w+)')
CONFIG_SYS = re.compile(r"^([a-z][\w-]*)\.(api|jdbc)\.")


def _split_aliases(text: str) -> list[str]:
    text = re.sub(r"^(also called|also known as)\s+", "", text.strip())
    parts = re.split(r",| or ", text)
    out = []
    for p in parts:
        p = p.strip().strip('"').strip()
        p = re.sub(r"^the\s+", "", p)
        if p:
            out.append(p)
    return out


def ea_agent(index: dict) -> list[dict]:
    props: list[dict] = []
    known: dict[str, set] = {}  # system name -> aliases (for the mention pass)

    def add_system(name, file, n, line, support, aliases=(), roles=()):
        p = _prop("system", name, file, n, line, support, aliases=list(aliases))
        if roles:
            p["properties"] = {"roles": list(roles)}
        props.append(p)
        known.setdefault(name, set()).update(aliases)

    # Prose: "X (also called Y)", channels, "referred to as", role phrases
    for rel, src in _files(index, provenance=PROSE):
        for n, line in enumerate(src["lines"], 1):
            for m in SYS_PAREN.finditer(line):
                rest = line[m.end():]
                roles = [fn(rm) for rx, fn in ROLE_PATTERNS if (rm := rx.search(rest))]
                add_system(m.group(1), rel, n, line, "definition", _split_aliases(m.group(2)), roles)
            for m in CHANNELS.finditer(line):
                for ch in _split_aliases(m.group(1)):
                    add_system(ch, rel, n, line, "definition", roles=["channel"])
            for m in REFERRED.finditer(line):
                add_system(m.group(2), rel, n, line, "definition", roles=[m.group(1)])

    # Capability map: one accountable owning team per capability
    for rel, src in _files(index, doc_type=("capability-map",)):
        for n, line in enumerate(src["lines"], 1):
            if m := CAPABILITY.match(line):
                props.append(_prop("capability", m.group(1), rel, n, line, "definition",
                                   definition=m.group(2).strip(), owner_team=m.group(3).strip()))

    # Diagram: nodes and edges
    for rel, src in _files(index, provenance=("diagram",)):
        ids: dict[str, str] = {}
        for n, line in enumerate(src["lines"], 1):
            for m in MERMAID_NODE.finditer(line):
                node_id, label = m.group(1), m.group(2)
                lm = re.match(r"^(.+?)\s*\((.+)\)$", label)
                name, aliases = (lm.group(1), _split_aliases(lm.group(2))) if lm else (label, [])
                if norm(node_id) != norm(name):
                    aliases.append(node_id)
                ids[node_id] = name
                roles = ["reporting / analytics (candidate)"] if re.search(r"warehouse|Mart\b", label) else []
                add_system(name, rel, n, line, "structure", aliases, roles)
        for n, line in enumerate(src["lines"], 1):
            if m := MERMAID_EDGE.match(line):
                s, label, t = ids.get(m.group(1), m.group(1)), m.group(2).strip(), ids.get(m.group(3), m.group(3))
                props.append(_prop("flow", f"{s} → {t}", rel, n, line, "structure", source=s, target=t, label=label))

    # Interface catalogue: endpoints are systems, rows are flows
    for rel, src in _files(index, doc_type=("interface-catalogue",)):
        for n, raw, row in _csv_rows(src):
            for end in ("source", "target"):
                add_system(row[end], rel, n, raw, "reference")
            props.append(_prop("flow", f"{row['source']} → {row['target']}", rel, n, raw, "structure",
                               source=row["source"], target=row["target"], label=row["interface_id"]))

    # Config: endpoints reveal systems and the calling system's dependencies
    for rel, src in _files(index, doc_type=("config",)):
        caller = src.get("system_hint")
        for n, line in enumerate(src["lines"], 1):
            if m := CONFIG_SYS.match(line):
                roles = [f"database: {db.group(1)}"] if (db := re.search(r"jdbc:(\w+)", line)) else []
                add_system(m.group(1), rel, n, line, "reference", roles=roles)
                if caller:
                    props.append(_prop("flow", f"{caller} → {m.group(1)}", rel, n, line, "reference",
                                       source=caller, target=m.group(1), label="runtime dependency (config)"))

    # Manifest hints: files that hold data structures belong to a data-holding application
    for rel, src in _files(index, doc_type=("data-dictionary", "ddl", "code")):
        if hint := src.get("system_hint"):
            first = next((l for l in src["lines"] if l.strip()), "")
            n = src["lines"].index(first) + 1
            add_system(hint, rel, n, first, "reference", roles=["data-holding application (candidate)"])

    # Mention pass: corroborate known systems wherever prose names them (first hit per file)
    for rel, src in _files(index, provenance=PROSE):
        for name, aliases in known.items():
            terms = [name, *aliases]
            for n, line in enumerate(src["lines"], 1):
                if any(re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", line) for t in terms if len(t) >= 2):
                    props.append(_prop("system", name, rel, n, line, "mention"))
                    break
    return props


# ---------------------------------------------------------------- BA agent

GLOSSARY = re.compile(r"^- \*\*(.+?)\*\*: (.+)$")
SYN_YES = re.compile(r'^"(.+?)" is a synonym of ([A-Z][\w ]*?)\.$')
SYN_NO = re.compile(r'^"(.+?)" is not a synonym of ([A-Z][\w ]*?)[;.]')
VALUES = re.compile(r"^(.+?) values: (.+?)\.$")


def ba_agent(index: dict) -> list[dict]:
    props: list[dict] = []
    terms: list[str] = []
    for rel, src in _files(index, provenance=PROSE):
        if src.get("doc_type") == "capability-map":
            continue
        heading = ""
        for n, line in enumerate(src["lines"], 1):
            if h := re.match(r"^#+\s+(.+)", line):
                heading = h.group(1)
            if m := GLOSSARY.match(line):
                term, body = m.group(1), m.group(2)
                syn = re.search(r"\s*Synonyms: (.+?)\.$", body)
                definition = body[: syn.start()].strip() if syn else body.strip()
                aliases = [s.strip() for s in syn.group(1).split(",")] if syn else []
                props.append(_prop("concept", term, rel, n, line, "definition", aliases=aliases, definition=definition))
                terms.append(term)
            elif m := SYN_YES.match(line.strip()):
                props.append(_prop("concept", m.group(2), rel, n, line, "definition", aliases=[m.group(1)],
                                   confirmed_synonyms=[m.group(1)]))
            elif m := SYN_NO.match(line.strip()):
                props.append(_prop("concept", m.group(2), rel, n, line, "definition", not_synonyms=[m.group(1)]))
            elif "rule" in heading.lower() and line.startswith("- "):
                stmt = line[2:].strip()
                props.append(_prop("rule", stmt, rel, n, line, "definition", statement=stmt))
            elif m := VALUES.match(line.strip()):
                vals = [const(v) for v in m.group(2).split(",")]
                props.append(_prop("taxonomy", pascal(m.group(1)), rel, n, line, "value-list", values=vals))

    # Mentions of glossary terms elsewhere (do not count as definitional support)
    for rel, src in _files(index, provenance=PROSE):
        for term in terms:
            for n, line in enumerate(src["lines"], 1):
                if GLOSSARY.match(line):
                    continue
                if re.search(rf"\b{re.escape(term)}\b", line):
                    props.append(_prop("concept", term, rel, n, line, "mention"))
                    break
    return props


# ---------------------------------------------------------------- DA agent

ISSUED_PROSE = re.compile(r"(?:The )?([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)*) is issued by ([A-Z][A-Za-z]+)")
ISSUED_GLOSS = re.compile(r"^- \*\*(.+?)\*\*:.*?\bissued by ([A-Z][A-Za-z]+)")
SQL_TABLE = re.compile(r"CREATE TABLE (\w+)", re.I)
SQL_COL = re.compile(r"^\s+(\w+)\s+([A-Z]+(?:\(\d+(?:,\s*\d+)?\))?)(.*?),?\s*$")
SQL_PK = re.compile(r"^\s*PRIMARY KEY \(([^)]+)\)", re.I)
SQL_REF = re.compile(r"REFERENCES (\w+)\((\w+)\)", re.I)
JAVA_CLASS = re.compile(r"public class (\w+)")
JAVA_FIELD = re.compile(r"private ([\w<>]+) (\w+);\s*(?://\s*(.*))?")
JAVA_ENUM = re.compile(r"enum (\w+) \{ ([^}]+) \}")


def _prefix_stripper(src: dict):
    pref = (src.get("table_prefix") or "").upper()
    return lambda t: t[len(pref):] if pref and t.upper().startswith(pref) and len(t) > len(pref) else t


def _entity_name(cls: str) -> str:
    return re.sub(r"(Record|Dto|DTO|Entity|Model)$", "", cls) or cls


def da_agent(index: dict) -> list[dict]:
    props: list[dict] = []
    id_attrs: dict[str, tuple[str, str]] = {}   # norm(attribute) -> (entity, identifier name)
    pending_refs: list[tuple] = []              # cross-reference candidates resolved at the end
    composites: list[tuple] = []                # (table, key columns, file, line no, line)

    # Data dictionary
    for rel, src in _files(index, doc_type=("data-dictionary",)):
        system = src.get("system_hint")
        strip = _prefix_stripper(src)
        seen_tables = set()
        for n, raw, row in _csv_rows(src):
            ent, attr = pascal(strip(row["table"])), camel(row["column"])
            if ent not in seen_tables:
                seen_tables.add(ent)
                props.append(_prop("entity", ent, rel, n, raw, "structure", system=system, physical=row["table"]))
            tax = pascal(row["description"]) if row.get("codes") else None
            props.append(_prop("attribute", f"{ent}.{attr}", rel, n, raw, "structure", entity=ent, attribute=attr,
                               physical=row["column"], data_type=row["data_type"], nullable=row["nullable"] == "Y",
                               description=row["description"], **({"range": tax} if tax else {})))
            if row["key"] == "PK":
                idn = human(row["description"] or row["column"])
                id_attrs[norm(attr)] = (ent, idn)
                props.append(_prop("identifier", idn, rel, n, raw, "structure", entity=ent, attribute=attr, key="primary"))
            if fk := re.match(r"FK:(\w+)\.(\w+)", row["key"] or ""):
                tgt = pascal(strip(fk.group(1)))
                props.append(_prop("relationship", f"{ent} → {tgt}", rel, n, raw, "structure",
                                   **{"from": ent, "to": tgt, "via": attr, "cardinality": "many-to-one"}))
            elif not row["key"]:
                pending_refs.append(("column", ent, attr, rel, n, raw))
            if row.get("codes"):
                codes = dict(c.split("=", 1) for c in row["codes"].split("|"))
                props.append(_prop("taxonomy", tax, rel, n, raw, "value-list",
                                   values=[const(v) for v in codes.values()], codes=codes))

    # DDL
    for rel, src in _files(index, doc_type=("ddl",)):
        system, table, cols, pk = src.get("system_hint"), None, [], []
        strip = _prefix_stripper(src)
        for n, line in enumerate(src["lines"], 1):
            if m := SQL_TABLE.search(line):
                table, cols, pk = pascal(strip(m.group(1))), [], []
                props.append(_prop("entity", table, rel, n, line, "structure", system=system, physical=m.group(1)))
            elif table and (m := SQL_PK.match(line)):
                pk = [camel(c.strip()) for c in m.group(1).split(",")]
                composites.append((table, pk, rel, n, line))
                for c in pk:
                    pending_refs.append(("composite", table, c, rel, n, line))
            elif table and (m := SQL_COL.match(line)) and m.group(1).upper() not in ("PRIMARY", "CONSTRAINT"):
                col, dtype, rest = m.group(1), m.group(2), m.group(3)
                attr = camel(col)
                props.append(_prop("attribute", f"{table}.{attr}", rel, n, line, "structure", entity=table,
                                   attribute=attr, physical=col, data_type=dtype, nullable="NOT NULL" not in rest.upper()))
                if "PRIMARY KEY" in rest.upper():
                    idn = human(col)
                    id_attrs[norm(attr)] = (table, idn)
                    props.append(_prop("identifier", idn, rel, n, line, "structure", entity=table, attribute=attr, key="primary"))
                if r := SQL_REF.search(rest):
                    tgt = pascal(strip(r.group(1)))
                    props.append(_prop("relationship", f"{table} → {tgt}", rel, n, line, "structure",
                                       **{"from": table, "to": tgt, "via": attr, "cardinality": "many-to-one"}))
                else:
                    pending_refs.append(("column", table, attr, rel, n, line))
            elif line.strip().startswith(");"):
                table = None

    # Example Java
    for rel, src in _files(index, doc_type=("code",), suffix=".java"):
        system = src.get("system_hint")
        enums = {m.group(1) for l in src["lines"] if (m := JAVA_ENUM.search(l))}
        ent, first_field = None, True
        for n, line in enumerate(src["lines"], 1):
            if m := JAVA_CLASS.search(line):
                ent, first_field = _entity_name(m.group(1)), True
                props.append(_prop("entity", ent, rel, n, line, "structure", system=system, physical=m.group(1)))
            elif ent and (m := JAVA_FIELD.search(line)):
                jtype, field, comment = m.group(1), m.group(2), (m.group(3) or "").strip()
                if lm := re.match(r"List<(\w+)>", jtype):
                    tgt = lm.group(1)
                    props.append(_prop("entity", tgt, rel, n, line, "reference", system=system,
                                       implied_by=f"{ent}.{field}"))
                    props.append(_prop("relationship", f"{ent} → {tgt}", rel, n, line, "structure",
                                       **{"from": ent, "to": tgt, "via": field, "cardinality": "one-to-many"}))
                else:
                    extra = {"range": jtype} if jtype in enums else {}
                    props.append(_prop("attribute", f"{ent}.{field}", rel, n, line, "structure", entity=ent,
                                       attribute=field, data_type=jtype, **extra,
                                       **({"comment": comment} if comment else {})))
                    if re.search(r"(Number|Id)$", field) and (first_field or "issued" in comment):
                        idn = human(field)
                        id_attrs.setdefault(norm(field), (ent, idn))
                        props.append(_prop("identifier", idn, rel, n, line, "structure", entity=ent, attribute=field,
                                           key="business", **({"note": comment} if comment else {})))
                    else:
                        pending_refs.append(("column", ent, field, rel, n, line))
                first_field = False

    # Prose: who issues identifiers
    for rel, src in _files(index, provenance=PROSE):
        for n, line in enumerate(src["lines"], 1):
            m = ISSUED_GLOSS.match(line) or ISSUED_PROSE.search(line)
            if m:
                props.append(_prop("identifier", m.group(1), rel, n, line, "definition", issued_by=m.group(2)))

    # Cross-reference pass: columns that carry another entity's identifier
    seen = set()
    for kind, ent, attr, rel, n, line in pending_refs:
        a = norm(attr)
        for id_attr, (owner, idn) in id_attrs.items():
            if owner == ent or not (a == id_attr or (a.endswith(id_attr) and len(id_attr) >= 8)):
                continue
            if (ent, owner, rel, n) in seen:
                continue
            seen.add((ent, owner, rel, n))
            role = a[: -len(id_attr)] or None
            props.append(_prop("relationship", f"{ent} → {owner}", rel, n, line, "reference",
                               **{"from": ent, "to": owner, "via": attr, "cardinality": "many-to-one",
                                  "note": "reference by identifier value; no foreign key in this source",
                                  **({"role": role} if role else {})}))
            props.append(_prop("identifier", idn, rel, n, line, "reference", entity=owner, seen_in=f"{ent}.{attr}"))

    # Link entities: a two-column composite key joining two entities = many-to-many
    for table, cols, rel, n, line in composites:
        owners = [id_attrs[norm(c)][0] for c in cols if norm(c) in id_attrs and id_attrs[norm(c)][0] != table]
        if len(owners) == 2:
            a, b = sorted(owners, key=lambda o: (o != "Customer", o))
            props.append(_prop("relationship", f"{a} ↔ {b}", rel, n, line, "structure",
                               **{"from": a, "to": b, "via": table, "cardinality": "many-to-many"}))
    return props


# ---------------------------------------------------------------- Engineering agent

IFACE_ID = re.compile(r"\b([A-Z]{2,}(?:-[A-Z]{2,})*-\d{2})\b")
EVENT_PROSE = re.compile(r"publishes an? ([A-Z]\w+) event")
PROC_START = re.compile(r"CREATE PROCEDURE (\w+)", re.I)
PROC_CAP = re.compile(r"--\s*Capability:\s*(.+)$")
PROC_WRITE = re.compile(r"\b(?:INSERT INTO|UPDATE)\s+(\w+)", re.I)
PROC_UPDATE_SET = re.compile(r"\bUPDATE\s+(\w+)\s+SET\s+(.+?)(?:\bWHERE\b|$)", re.I)
PROC_READ = re.compile(r"\b(?:FROM|JOIN)\s+(\w+)", re.I)
JAVA_RULE = re.compile(r'throw new \w+Exception\("(.+?)"\)')


def eng_agent(index: dict) -> list[dict]:
    props: list[dict] = []
    for rel, src in _files(index, doc_type=("interface-catalogue",)):
        for n, raw, row in _csv_rows(src):
            props.append(_prop("interface", row["interface_id"], rel, n, raw, "definition", title=row["name"],
                               source=row["source"], target=row["target"], mechanism=row["mechanism"],
                               frequency=row["frequency"], payload=row["payload"], owner=row["owner"]))
            if row["mechanism"].lower() == "event":
                props.append(_prop("event", row["payload"], rel, n, raw, "definition",
                                   producer=row["source"], consumer=row["target"], interface=row["interface_id"]))
    for rel, src in _files(index, provenance=("diagram",) + PROSE):
        for n, line in enumerate(src["lines"], 1):
            for m in IFACE_ID.finditer(line):
                props.append(_prop("interface", m.group(1), rel, n, line, "mention"))
            if m := EVENT_PROSE.search(line):
                props.append(_prop("event", m.group(1), rel, n, line, "definition"))
            if src["provenance"] == "diagram" and (m := MERMAID_EDGE.match(line)):
                if re.fullmatch(r"[A-Z][a-z]+(?:[A-Z][a-z]+)+", m.group(2).strip()):
                    props.append(_prop("event", m.group(2).strip(), rel, n, line, "structure"))
    # Batch-job catalogue: each job runs one calculation program
    for rel, src in _files(index, doc_type=("job-catalogue",)):
        split = lambda v: [x.strip().upper() for x in (v or "").split(";") if x.strip()]
        for n, raw, row in _csv_rows(src):
            props.append(_prop("calculation", row["program"], rel, n, raw, "structure", title=row["job_name"],
                               program=row["program"], capability=row.get("capability", ""), reads=split(row.get("reads")),
                               writes=split(row.get("writes")), owner_team=row.get("owner", ""),
                               frequency=row.get("frequency", ""), job_id=row.get("job_id", "")))
    # Stored procedures: which tables and columns each program really reads and writes
    for rel, src in _files(index, doc_type=("procedures",)):
        cur = None
        for n, line in enumerate(src["lines"], 1):
            if m := PROC_START.search(line):
                cur = {"name": m.group(1), "n": n, "line": line, "reads": set(), "writes": set(), "cols": set(), "cap": ""}
            elif cur is not None:
                if m := PROC_CAP.search(line):
                    cur["cap"] = m.group(1).strip()
                for m in PROC_WRITE.finditer(line):
                    cur["writes"].add(m.group(1).upper())
                if m := PROC_UPDATE_SET.search(line):
                    for col in re.findall(r"(\w+)\s*=", m.group(2)):
                        cur["cols"].add(f"{m.group(1).upper()}.{col.upper()}")
                for m in PROC_READ.finditer(line):
                    cur["reads"].add(m.group(1).upper())
                if line.strip().upper().startswith("END;"):
                    props.append(_prop("calculation", cur["name"], rel, cur["n"], cur["line"], "structure", program=cur["name"],
                                       capability=cur["cap"], reads=sorted(cur["reads"] - cur["writes"]),
                                       writes=sorted(cur["writes"]), writes_columns=sorted(cur["cols"])))
                    cur = None
    for rel, src in _files(index, doc_type=("code",), suffix=".java"):
        for n, line in enumerate(src["lines"], 1):
            if m := JAVA_ENUM.search(line):
                props.append(_prop("taxonomy", m.group(1), rel, n, line, "value-list",
                                   values=[v.strip() for v in m.group(2).split(",")]))
            if m := JAVA_RULE.search(line):
                props.append(_prop("rule", m.group(1), rel, n, line, "structure", statement=m.group(1),
                                   enforced_in=rel))
    return props


AGENTS = {"ea": ea_agent, "ba": ba_agent, "da": da_agent, "eng": eng_agent}
AGENT_LABEL = {"ea": "EA agent", "ba": "BA agent", "da": "DA agent", "eng": "Engineering agent"}


def run_sim_agents(paths: LoopPaths, trace: Trace) -> None:
    index = read_json(paths.work / "sources.json")
    for key, fn in AGENTS.items():
        proposals = fn(index)
        write_json(paths.proposals / f"{key}.json", {"agent": key, "loop": paths.loop, "proposals": proposals})
        by_kind: dict[str, int] = {}
        for p in proposals:
            by_kind[p["kind"]] = by_kind.get(p["kind"], 0) + 1
        summary = ", ".join(f"{v} {k}" for k, v in sorted(by_kind.items()))
        trace.emit("B. Agents propose", AGENT_LABEL[key], "proposed", f"{len(proposals)} proposals ({summary})",
                   agent=key, counts=by_kind)

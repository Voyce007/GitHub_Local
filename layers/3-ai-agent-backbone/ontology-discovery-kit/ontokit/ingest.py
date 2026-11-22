"""Stage A — Intake: read the manifest, load every listed file, mark staleness.

Produces work/<loop>/sources.json, the citable source index every agent
and the validator use. Files not in the manifest cannot be cited.
"""
from __future__ import annotations

import datetime as dt
import re

import yaml

from .common import LoopPaths, Trace, write_json


def _as_date(value) -> dt.date | None:
    if value is None:
        return None
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def _entries(inputs_root, loop: str, seen: set) -> list[tuple[str, str, dict]]:
    """(citation key, location under inputs/, manifest entry) for a loop and everything it carries forward."""
    if loop in seen:
        return []
    seen.add(loop)
    manifest = yaml.safe_load((inputs_root / loop / "manifest.yaml").read_text(encoding="utf-8"))
    out = []
    for prior in manifest.get("carry_forward", []) or []:
        for key, loc, entry in _entries(inputs_root, prior, seen):
            cited = key if re.match(r"loop-\d+/", key) else f"{prior}/{key}"
            out.append((cited, loc, {**entry, "carried_from": entry.get("carried_from", prior)}))
    for entry in manifest["files"]:
        out.append((entry["path"], f"{loop}/{entry['path']}", entry))
    return out


def ingest(paths: LoopPaths, trace: Trace) -> dict:
    manifest_path = paths.inputs / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    received = _as_date(manifest.get("received")) or dt.date.today()
    stale_years = manifest.get("staleness_years", 4)
    inputs_root = paths.inputs.parent

    sources: dict[str, dict] = {}
    missing = []
    carried = 0
    for rel, location, entry in _entries(inputs_root, paths.loop, set()):
        fp = inputs_root / location
        if not fp.exists():
            missing.append(rel)
            continue
        text = fp.read_text(encoding="utf-8")
        date = _as_date(entry.get("date"))
        age_years = round((received - date).days / 365.25, 1) if date else None
        stale = bool(entry.get("stale")) or (age_years is not None and age_years > stale_years)
        sources[rel] = {
            **{k: (str(v) if isinstance(v, dt.date) else v) for k, v in entry.items()},
            "path": rel,
            "location": location,
            "age_years": age_years,
            "stale": stale,
            "lines": text.splitlines(),
        }
        if entry.get("carried_from"):
            carried += 1
        else:
            trace.emit("A. Intake", "Intake", "ingested", rel,
                       provenance=entry["provenance"], doc_type=entry.get("doc_type"),
                       stale=stale, lines=len(text.splitlines()))
        if stale and not entry.get("carried_from"):
            trace.emit("A. Intake", "Intake", "flagged stale",
                       f"{rel} is {age_years} years old (threshold {stale_years}); it will not count towards grade B")
    if carried:
        trace.emit("A. Intake", "Intake", "carried forward",
                   f"{carried} files from {', '.join(manifest.get('carry_forward', []))} remain citable", carried=carried)

    index = {
        "batch": manifest.get("batch", paths.loop),
        "organisation": manifest.get("organisation"),
        "received": str(received),
        "staleness_years": stale_years,
        "carry_forward": manifest.get("carry_forward", []),
        "missing": missing,
        "sources": sources,
    }
    write_json(paths.work / "sources.json", index)
    trace.emit("A. Intake", "Intake", "source index written",
               f"{len(sources)} files citable ({carried} carried forward), {len(missing)} missing",
               files=len(sources), carried=carried, missing=missing)
    return index


_ws = re.compile(r"\s+")


def quote_found(index: dict, file: str, quote: str) -> bool:
    """Anti-hallucination check: the quote must appear verbatim (whitespace-insensitive)."""
    src = index["sources"].get(file)
    if not src or not quote.strip():
        return False
    hay = _ws.sub(" ", "\n".join(src["lines"]))
    return _ws.sub(" ", quote.strip()) in hay

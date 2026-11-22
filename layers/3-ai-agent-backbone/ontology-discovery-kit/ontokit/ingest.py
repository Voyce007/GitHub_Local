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


def ingest(paths: LoopPaths, trace: Trace) -> dict:
    manifest_path = paths.inputs / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    received = _as_date(manifest.get("received")) or dt.date.today()
    stale_years = manifest.get("staleness_years", 4)

    sources: dict[str, dict] = {}
    missing = []
    for entry in manifest["files"]:
        rel = entry["path"]
        fp = paths.inputs / rel
        if not fp.exists():
            missing.append(rel)
            continue
        text = fp.read_text(encoding="utf-8")
        date = _as_date(entry.get("date"))
        age_years = round((received - date).days / 365.25, 1) if date else None
        stale = bool(entry.get("stale")) or (age_years is not None and age_years > stale_years)
        sources[rel] = {
            **{k: (str(v) if isinstance(v, dt.date) else v) for k, v in entry.items()},
            "age_years": age_years,
            "stale": stale,
            "lines": text.splitlines(),
        }
        trace.emit("A. Intake", "Intake", "ingested", rel,
                   provenance=entry["provenance"], doc_type=entry.get("doc_type"),
                   stale=stale, lines=len(text.splitlines()))
        if stale:
            trace.emit("A. Intake", "Intake", "flagged stale",
                       f"{rel} is {age_years} years old (threshold {stale_years}); it will not count towards grade B")

    index = {
        "batch": manifest.get("batch", paths.loop),
        "organisation": manifest.get("organisation"),
        "received": str(received),
        "staleness_years": stale_years,
        "missing": missing,
        "sources": sources,
    }
    write_json(paths.work / "sources.json", index)
    trace.emit("A. Intake", "Intake", "source index written",
               f"{len(sources)} files citable, {len(missing)} missing", files=len(sources), missing=missing)
    return index


_ws = re.compile(r"\s+")


def quote_found(index: dict, file: str, quote: str) -> bool:
    """Anti-hallucination check: the quote must appear verbatim (whitespace-insensitive)."""
    src = index["sources"].get(file)
    if not src or not quote.strip():
        return False
    hay = _ws.sub(" ", "\n".join(src["lines"]))
    return _ws.sub(" ", quote.strip()) in hay

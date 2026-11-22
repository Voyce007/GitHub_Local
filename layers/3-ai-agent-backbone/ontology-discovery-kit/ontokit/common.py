"""Shared helpers: paths, config loading, name normalisation, trace log, JSON I/O."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

KIT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = KIT_ROOT / "config"

# Abbreviations expanded before matching names across sources
# (CUSTOMER_NO / customer_no / customerNumber all normalise to "customernumber").
ABBREV = {
    "no": "number", "num": "number", "nbr": "number",
    "addr": "address", "cust": "customer", "acct": "account",
    "ts": "timestamp", "dob": "dateofbirth", "amt": "amount",
}


def tokens(name: str) -> list[str]:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    s = re.sub(r"[^A-Za-z0-9]+", " ", s)
    toks = [t.lower() for t in s.split() if t]
    if toks and toks[0] == "the":
        toks = toks[1:]
    return [ABBREV.get(t, t) for t in toks]


def norm(name: str) -> str:
    """Matching key: case-, separator- and abbreviation-insensitive."""
    return "".join(tokens(name))


def pascal(name: str) -> str:
    return "".join(t.capitalize() for t in tokens(name))


def camel(name: str) -> str:
    p = pascal(name)
    return p[:1].lower() + p[1:]


def human(name: str) -> str:
    return " ".join(t.capitalize() for t in tokens(name))


def const(value: str) -> str:
    """Enumeration value form: 'Sole trader' -> 'SOLE_TRADER'."""
    return re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").upper()


def load_config(name: str) -> dict:
    with open(CONFIG_DIR / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@dataclass
class LoopPaths:
    loop: str
    root: Path  # the discovery/ folder

    @property
    def inputs(self) -> Path:
        return self.root / "inputs" / self.loop

    @property
    def work(self) -> Path:
        return self.root / "work" / self.loop

    @property
    def proposals(self) -> Path:
        return self.work / "proposals"

    @property
    def outputs(self) -> Path:
        return self.root / "outputs" / self.loop

    def ensure(self) -> None:
        for p in (self.work, self.proposals, self.outputs):
            p.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class Trace:
    """Ordered event log of a run. Drives the storyboard/simulation playback."""
    events: list[dict] = field(default_factory=list)

    def emit(self, stage: str, actor: str, action: str, detail: str = "", **data: Any) -> None:
        self.events.append({
            "seq": len(self.events) + 1,
            "stage": stage,
            "actor": actor,
            "action": action,
            "detail": detail,
            **({"data": data} if data else {}),
        })

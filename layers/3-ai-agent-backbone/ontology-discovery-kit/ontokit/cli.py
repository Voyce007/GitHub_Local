"""ontokit command line.

  python -m ontokit simulate            # whole loop with simulated agents and simulated approvals
  python -m ontokit run                 # whole loop from proposals already written by live agents
  python -m ontokit ingest | sim-agents | validate | reconcile | unknowns | gate | approve | publish

Common options: --loop loop-01  --root discovery
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import approvals, gates, grading, ingest, prior, publish, sim_agents, steward, unknowns, validate
from .common import KIT_ROOT, LoopPaths, Trace, read_json, write_json


def _trace(paths: LoopPaths, fresh: bool) -> Trace:
    fp = paths.work / "trace.json"
    t = Trace()
    if not fresh and fp.exists():
        t.events = read_json(fp)
    return t


def _save(paths: LoopPaths, t: Trace) -> None:
    write_json(paths.work / "trace.json", t.events)
    if paths.outputs.exists():
        write_json(paths.outputs / "trace.json", t.events)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ontokit", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["simulate", "run", "ingest", "sim-agents", "validate", "reconcile",
                                        "unknowns", "gate", "approve", "publish"])
    ap.add_argument("--loop", default="loop-01")
    ap.add_argument("--root", default=str(KIT_ROOT / "discovery"), help="discovery folder (inputs/, work/, outputs/)")
    ap.add_argument("--simulate-approvals", action="store_true", help="approve: fill decisions with the simulator")
    a = ap.parse_args(argv)

    paths = LoopPaths(a.loop, Path(a.root))
    if not (paths.inputs / "manifest.yaml").exists():
        print(f"No manifest at {paths.inputs / 'manifest.yaml'}", file=sys.stderr)
        return 2
    paths.ensure()
    fresh = a.command in ("simulate", "run", "ingest")
    t = _trace(paths, fresh)
    cmd = a.command

    def reconcile_all():
        steward.reconcile(paths, t)
        grading.grade(paths, t)
        prior.apply_prior(paths, t)

    if cmd in ("simulate", "run"):
        ingest.ingest(paths, t)
        if cmd == "simulate":
            sim_agents.run_sim_agents(paths, t)
        validate.validate(paths, t)
        reconcile_all()
        unknowns.build_unknowns(paths, t)
        gates.run_gates(paths, t)
        approvals.prepare(paths, t, simulate=(cmd == "simulate") or a.simulate_approvals)
        publish.publish(paths, t)
    elif cmd == "ingest":
        ingest.ingest(paths, t)
    elif cmd == "sim-agents":
        sim_agents.run_sim_agents(paths, t)
    elif cmd == "validate":
        validate.validate(paths, t)
    elif cmd == "reconcile":
        reconcile_all()
    elif cmd == "unknowns":
        unknowns.build_unknowns(paths, t)
    elif cmd == "gate":
        gates.run_gates(paths, t)
    elif cmd == "approve":
        approvals.prepare(paths, t, simulate=a.simulate_approvals)
    elif cmd == "publish":
        publish.publish(paths, t)
    _save(paths, t)

    if cmd in ("simulate", "run", "publish"):
        print((paths.outputs / "summary.md").read_text(encoding="utf-8"))
    else:
        for e in t.events[-6:]:
            print(f"[{e['stage']}] {e['actor']}: {e['action']} — {e['detail']}")
    return 0

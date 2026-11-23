#!/usr/bin/env python3
"""Install the Ontology Discovery Kit for Claude Code. Works on macOS, Linux and Windows.

    python install.py standalone              # use this folder as its own Claude Code project (checks and self-test)
    python install.py project <path>          # add the agents and skill to an existing project's .claude/
    python install.py user                    # add them to ~/.claude/ for every project on this machine
    python install.py uninstall project <path> | uninstall user

Options:
    --no-pip     do not pip-install ontokit; make it importable with a .pth file instead
    --no-tests   skip the self-test

The kit folder itself stays where it is. project/user installs point the agents
and skill at it, so keep the folder in place (or re-run the installer after moving it).
"""
from __future__ import annotations

import argparse
import shutil
import site
import subprocess
import sys
import sysconfig
from pathlib import Path

KIT = Path(__file__).resolve().parent
AGENTS = sorted((KIT / ".claude" / "agents").glob("*.md"))
SKILL = KIT / ".claude" / "skills" / "ontology-discovery-loop"
MARK = "<!-- ontokit-kit-home -->"


def say(msg: str) -> None:
    print(f"  {msg}")


def check_python() -> None:
    if sys.version_info < (3, 10):
        sys.exit(f"Python 3.10 or newer is needed (found {sys.version.split()[0]}).")
    try:
        import yaml  # noqa: F401
    except ImportError:
        say("PyYAML is missing; installing it")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "PyYAML>=6.0"])
    try:
        import docx  # noqa: F401
        import openpyxl  # noqa: F401
    except ImportError:
        say("installing openpyxl and python-docx for the Excel and Word report packs")
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "openpyxl>=3.1", "python-docx>=1.1"],
                           capture_output=True, text=True)
        if r.returncode:
            say("could not install them; reports will be HTML only until you run: pip install openpyxl python-docx")


def make_importable(no_pip: bool) -> None:
    """So `python -m ontokit` works from any folder."""
    if not no_pip:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "-e", str(KIT)], capture_output=True, text=True)
        if r.returncode == 0:
            say("ontokit installed (editable) with pip")
            return
        say("pip install did not work here; using a .pth file instead")
    for target in (sysconfig.get_paths()["purelib"], site.getusersitepackages()):
        try:
            Path(target).mkdir(parents=True, exist_ok=True)
            (Path(target) / "ontokit-kit.pth").write_text(str(KIT) + "\n", encoding="utf-8")
            say(f"ontokit made importable via {Path(target) / 'ontokit-kit.pth'}")
            return
        except OSError:
            continue
    say("Could not make ontokit importable. Run commands from the kit folder instead.")


def with_kit_home(text: str) -> str:
    """Insert a 'kit location' note after the front matter, so relative paths resolve."""
    note = (f"{MARK}\n> **Kit location:** `{KIT}`. Paths in these instructions such as `config/`, `schemas/`, "
            f"`.claude/agents/`, `tools/` and `scenarios/` are relative to that folder. `python -m ontokit` "
            f"works from any folder; always pass `--root` (for example `--root discovery` in this project).\n\n")
    if MARK in text:
        text = text[:text.index(MARK)] + text[text.index("\n", text.index("`--root discovery`")) + 1:]
    if text.startswith("---"):
        end = text.index("\n---", 3) + 4
        return text[:end] + "\n\n" + note + text[end:].lstrip("\n")
    return note + "\n" + text


def install_to(dot_claude: Path) -> None:
    (dot_claude / "agents").mkdir(parents=True, exist_ok=True)
    for a in AGENTS:
        (dot_claude / "agents" / a.name).write_text(with_kit_home(a.read_text(encoding="utf-8")), encoding="utf-8")
        say(f"agent   {dot_claude / 'agents' / a.name}")
    dst = dot_claude / "skills" / SKILL.name
    dst.mkdir(parents=True, exist_ok=True)
    (dst / "SKILL.md").write_text(with_kit_home((SKILL / "SKILL.md").read_text(encoding="utf-8")), encoding="utf-8")
    say(f"skill   {dst / 'SKILL.md'}")


def uninstall_from(dot_claude: Path) -> None:
    for a in AGENTS:
        f = dot_claude / "agents" / a.name
        if f.exists() and MARK in f.read_text(encoding="utf-8"):
            f.unlink()
            say(f"removed {f}")
    d = dot_claude / "skills" / SKILL.name
    if (d / "SKILL.md").exists() and MARK in (d / "SKILL.md").read_text(encoding="utf-8"):
        shutil.rmtree(d)
        say(f"removed {d}")


def self_test() -> None:
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=KIT, capture_output=True, text=True)
    last = (r.stderr.strip().splitlines() or ["?"])[-1]
    say(f"self-test: {last}")
    if r.returncode:
        sys.exit("Self-test failed. See: python -m unittest discover -s tests")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["standalone", "project", "user", "uninstall"])
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--no-pip", action="store_true")
    ap.add_argument("--no-tests", action="store_true")
    a = ap.parse_args()

    print("Ontology Discovery Kit installer")
    if a.mode == "uninstall":
        if a.rest[:1] == ["user"]:
            uninstall_from(Path.home() / ".claude")
        elif a.rest[:1] == ["project"] and len(a.rest) == 2:
            uninstall_from(Path(a.rest[1]).resolve() / ".claude")
        else:
            sys.exit("Usage: python install.py uninstall project <path> | uninstall user")
        print("Done.")
        return

    check_python()
    if a.mode == "standalone":
        say(f"Open this folder as the project in Claude Code: {KIT}")
        say("Its .claude/ folder holds the six agents and the ontology-discovery-loop skill.")
    else:
        make_importable(a.no_pip)
        if a.mode == "project":
            if len(a.rest) != 1:
                sys.exit("Usage: python install.py project <path-to-your-project>")
            proj = Path(a.rest[0]).resolve()
            if not proj.is_dir():
                sys.exit(f"Not a folder: {proj}")
            install_to(proj / ".claude")
            (proj / "discovery" / "inputs" / "loop-01").mkdir(parents=True, exist_ok=True)
            sc = proj / "discovery" / "scenario.yaml"
            if not sc.exists():
                sc.write_text("# Optional settings for this discovery root.\n"
                              "# Concepts the phase-2 gate must find, e.g. [Customer, Order]. Leave empty to skip that check.\n"
                              "key_concepts: []\n"
                              "# To split a monolith, add a target_domains.yaml next to this file\n"
                              f"# (pattern: {KIT / 'scenarios' / 'northmere' / 'target_domains.yaml'}).\n", encoding="utf-8")
                say(f"settings file:  {sc}")
            say(f"evidence folder ready: {proj / 'discovery' / 'inputs' / 'loop-01'} (add files and a manifest.yaml)")
        else:
            install_to(Path.home() / ".claude")
    if not a.no_tests:
        self_test()
    print("\nDone. In Claude Code, try:\n"
          "  Run the ontology discovery loop for loop-01 with --root discovery, following the ontology-discovery-loop skill.\n"
          "Or, to see it work on a sample first:\n"
          f"  python -m ontokit simulate --root \"{KIT / 'scenarios' / 'northmere'}\" --loop loop-01")


if __name__ == "__main__":
    main()

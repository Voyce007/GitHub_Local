# Installing the Ontology Discovery Kit

There are two bundles. Pick the one that matches how you use Claude.

| You use | Bundle | Agents run as |
|---|---|---|
| **Claude Code** (terminal, desktop app, VS Code or JetBrains, or claude.ai/code on the web) | `ontology-discovery-kit-<version>.zip` | Six real subagents, four of them in parallel |
| **Claude apps with skills** (claude.ai, Claude desktop chat) | `ontology-discovery-skill-<version>.zip` | One Claude playing each role in turn |

Both use the same pipeline and the same checks. Every claim must quote its source, grades are computed, and only named people approve.

**Requirements:** Python 3.10 or newer, PyYAML, and, for the Excel and Word report packs, openpyxl and python-docx. The installer adds any that are missing. No hosted services and no API keys.

**After every run, open `outputs/<loop>/reports/index.html`.** It links every agent's HTML explainer, Excel workbook, Word document and diagrams, plus every other output.

---

## Claude Code

Unzip `ontology-discovery-kit-<version>.zip` anywhere, then choose one of three ways to install it.

### A. Standalone: the kit is the project
```bash
cd ontology-discovery-kit
python install.py standalone        # checks Python and runs the self-test
```
Open the `ontology-discovery-kit` folder in Claude Code. The agents and skill in its `.claude/` folder load automatically.

### B. Into an existing project
```bash
python ontology-discovery-kit/install.py project /path/to/your-project
```
This makes three changes:
- copies the six agents and the skill into `your-project/.claude/`, each with a note saying where the kit lives
- makes `python -m ontokit` work from any folder
- creates `your-project/discovery/inputs/loop-01/` for your evidence.

### C. For every project on this machine
```bash
python ontology-discovery-kit/install.py user
```
This puts the agents and skill in `~/.claude/`.

For options B and C, keep the kit folder where it is. If you move it, run the installer again.

### Check it works
```bash
python -m ontokit simulate --root ontology-discovery-kit/scenarios/northmere --loop loop-01
```
Then, in Claude Code:
> Run the ontology discovery loop for loop-01 with `--root discovery`, following the ontology-discovery-loop skill.

### Uninstall
```bash
python ontology-discovery-kit/install.py uninstall project /path/to/your-project
python ontology-discovery-kit/install.py uninstall user
```
Uninstalling removes only the files the installer added.

### Cloud and web sessions
On claude.ai/code, commit the kit, or a project with option B applied, to your repository. Add `pip install PyYAML` to the environment's setup script if it isn't already installed.

---

## Claude apps (claude.ai or Claude desktop chat)

1. Make sure code execution and skills are turned on for your account. An organisation owner may need to allow them.
2. Go to **Settings → Capabilities → Skills → Upload skill**, and upload `ontology-discovery-skill-<version>.zip` unchanged.
3. Start a conversation and say, for example:
   > Use the ontology-discovery skill to run the Northmere demo.

   or, after uploading your documents:
   > Use the ontology-discovery skill on these files. We want to split our legacy data store into Customer, Billing and Support domains.

**What is different in the apps:**
- The roles run one after another, not in parallel.
- The sandbox does not keep files between conversations. Claude offers a zip of the work at the end of each session, so upload it again to start the next loop.

---

## What is in the kit

| Path | What it is |
|---|---|
| `.claude/agents/` | The six agents |
| `.claude/skills/ontology-discovery-loop/` | The run procedure |
| `ontokit/` | The pipeline |
| `config/` | The playbook as data |
| `scenarios/` | Three worked examples: a generic company, Meridale and Northmere, plus the Northmere live run |
| `docs/*.html` | The storyboards |
| `tools/` | Storyboard and bundle builders |
| `tests/` | The self-test |
| `README.md` and `CLAUDE.md` | Details |

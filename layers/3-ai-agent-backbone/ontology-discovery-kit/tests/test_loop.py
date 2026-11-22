"""End-to-end checks on the sample loop-01 batch. Run: python -m unittest discover -s tests"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from ontokit.cli import main

KIT = Path(__file__).resolve().parent.parent


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(KIT / "discovery" / "inputs", self.tmp / "inputs")
        self.root = str(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _model(self):
        return json.loads((self.tmp / "work/loop-01/model.json").read_text())

    def test_simulation_finds_planted_issues(self):
        self.assertEqual(main(["simulate", "--root", self.root]), 0)
        els = {(e["kind"], e["name"]): e for e in self._model()["elements"]}
        # alias resolution
        custhub = els[("system", "CustHub")]
        self.assertTrue({"Customer Hub", "CRM", "CH"} <= set(custhub["aliases"]))
        # the three planted contradictions
        for key in [("taxonomy", "CustomerType"), ("taxonomy", "PaymentStatus"), ("identifier", "Customer Number")]:
            self.assertEqual(els[key]["grade"], "X", key)
        # agreement across three sources
        self.assertEqual(els[("taxonomy", "KycStatus")]["grade"], "B")
        # unknown system found only in config
        self.assertEqual(els[("system", "mandate-svc")]["grade"], "C")
        # reference gaps are assumptions, never as-is
        self.assertEqual(els[("entity", "Person")]["origin"], "assumed")
        self.assertEqual(els[("entity", "Person")]["grade"], "D")
        # no grade A without real artefacts
        self.assertFalse(any(e["grade"] == "A" for e in els.values()))
        unknowns = json.loads((self.tmp / "work/loop-01/unknowns.json").read_text())
        qs = " ".join(u["question"] for u in unknowns)
        self.assertIn("Account Holder", qs)
        self.assertIn("mandate-svc", qs)
        gates = json.loads((self.tmp / "work/loop-01/gates.json").read_text())
        self.assertTrue(all(g["status"] == "provisional" for g in gates))
        for f in ["as-is-ontology.yaml", "system-inventory.md", "glossary.md", "unknowns-register.md",
                  "jira-issues.json", "gate-report.md", "standins/cust_hub.sql", "trace.json"]:
            self.assertTrue((self.tmp / "outputs/loop-01" / f).exists(), f)

    def test_validator_rejects_bad_live_agent_output(self):
        main(["ingest", "--root", self.root])
        main(["sim-agents", "--root", self.root])
        ba = self.tmp / "work/loop-01/proposals/ba.json"
        data = json.loads(ba.read_text())
        data["proposals"] += [
            {"kind": "concept", "name": "Invented", "definition": "x", "origin": "inferred",
             "evidence": [{"file": "wiki/glossary-export.md", "quote": "This sentence is not in the file."}]},
            {"kind": "system", "name": "OutOfScope", "origin": "inferred",
             "evidence": [{"file": "wiki/glossary-export.md", "quote": "Page owner: Data Governance."}]},
            {"kind": "concept", "name": "SelfApproved", "origin": "confirmed",
             "evidence": [{"file": "wiki/glossary-export.md", "quote": "Page owner: Data Governance."}]},
        ]
        ba.write_text(json.dumps(data))
        main(["validate", "--root", self.root])
        rejected = json.loads((self.tmp / "work/loop-01/validated.json").read_text())["rejected"]
        names = {r["name"]: r["problems"][0] for r in rejected}
        self.assertIn("quote not found", names["Invented"])
        self.assertIn("RACI write scope", names["OutOfScope"])
        self.assertIn("cannot mark", names["SelfApproved"])

    def test_run_from_files_leaves_approvals_pending(self):
        main(["ingest", "--root", self.root])
        main(["sim-agents", "--root", self.root])
        self.assertEqual(main(["run", "--root", self.root]), 0)
        # `run` must not invent human decisions
        text = (self.tmp / "work/loop-01/approvals.yaml").read_text()
        self.assertIn("decision: pending", text)
        self.assertNotIn("simulated reviewer", text)


if __name__ == "__main__":
    unittest.main()

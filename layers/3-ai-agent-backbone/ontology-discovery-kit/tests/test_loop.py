"""End-to-end checks on the sample batches. Run: python -m unittest discover -s tests"""
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

    def _j(self, rel):
        return json.loads((self.tmp / rel).read_text())

    def _els(self, loop):
        return {(e["kind"], e["name"]): e for e in self._j(f"outputs/{loop}/elements.json")}

    def test_loop1_finds_planted_issues(self):
        self.assertEqual(main(["simulate", "--root", self.root]), 0)
        els = self._els("loop-01")
        self.assertTrue({"Customer Hub", "CRM", "CH"} <= set(els[("system", "CustHub")]["aliases"]))
        self.assertTrue({"ERP", "GL"} <= set(els[("system", "LedgerOne")]["aliases"]))
        for key in [("taxonomy", "CustomerType"), ("taxonomy", "OrderStatus"), ("identifier", "Customer Number")]:
            self.assertEqual(els[key]["grade"], "X", key)
        for key in [("taxonomy", "CreditStatus"), ("taxonomy", "RiskRating"), ("taxonomy", "ControlType")]:
            self.assertEqual(els[key]["grade"], "B", key)
        self.assertEqual(els[("system", "tax-engine")]["grade"], "C")
        self.assertTrue(els[("entity", "CustomerEntity")]["properties"].get("link_entity"))
        self.assertEqual(els[("entity", "Person")]["origin"], "assumed")
        self.assertFalse(any(e["grade"] == "A" for e in els.values()))
        qs = " ".join(u["question"] for u in self._j("outputs/loop-01/unknowns.json"))
        self.assertIn("'Account' a synonym of Customer", qs)
        self.assertIn("tax-engine", qs)
        self.assertNotIn("bank", qs.lower())
        self.assertTrue(all(g["status"] == "provisional" for g in self._j("work/loop-01/gates.json")))
        for f in ["as-is-ontology.yaml", "system-inventory.md", "glossary.md", "unknowns-register.md",
                  "jira-issues.json", "gate-report.md", "standins/cust_hub.sql", "trace.json"]:
            self.assertTrue((self.tmp / "outputs/loop-01" / f).exists(), f)
        self.assertFalse((self.tmp / "outputs/loop-01/change-register.md").exists())

    def test_loop2_iterates_on_loop1(self):
        main(["simulate", "--root", self.root, "--loop", "loop-01"])
        before = self._els("loop-01")
        self.assertEqual(main(["simulate", "--root", self.root, "--loop", "loop-02"]), 0)
        after = self._els("loop-02")
        # ids are stable across loops
        for key in [("system", "CustHub"), ("taxonomy", "CustomerType"), ("entity", "Customer"), ("entity", "Person")]:
            self.assertEqual(before[key]["id"], after[key]["id"], key)
        # SME answers resolve contradictions; superseded variants are kept for audit
        ct = after[("taxonomy", "CustomerType")]
        self.assertEqual(ct["grade"], "B")
        self.assertEqual(ct["properties"]["values"], ["INDIVIDUAL", "SOLE_TRADER", "COMPANY"])
        self.assertEqual(ct["resolutions"][0]["superseded"][0]["value"], ["INDIVIDUAL", "BUSINESS"])
        self.assertEqual(after[("identifier", "Customer Number")]["properties"]["issued_by"], "CustHub")
        # the real schema export reaches grade A; documents alone still cannot
        self.assertEqual(after[("entity", "Customer")]["grade"], "A")
        self.assertNotEqual(after[("entity", "Invoice")]["grade"], "A")
        # carried-forward files stay citable under their loop prefix
        self.assertIn("loop-01/docs/order-to-cash-overview.md", self._j("work/loop-02/sources.json")["sources"])
        ch = self._j("outputs/loop-02/changes.json")
        self.assertEqual(ch["summary"]["contradictions_resolved"], 3)
        self.assertGreater(ch["summary"]["graded_up"], 10)
        self.assertEqual(ch["summary"]["graded_down"], 0)
        self.assertGreaterEqual(ch["summary"]["unknowns_closed"], 3)
        self.assertTrue((self.tmp / "outputs/loop-02/change-register.md").exists())

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
        rejected = self._j("work/loop-01/validated.json")["rejected"]
        names = {r["name"]: r["problems"][0] for r in rejected}
        self.assertIn("quote not found", names["Invented"])
        self.assertIn("RACI write scope", names["OutOfScope"])
        self.assertIn("cannot mark", names["SelfApproved"])

    def test_run_from_files_leaves_approvals_pending(self):
        main(["ingest", "--root", self.root])
        main(["sim-agents", "--root", self.root])
        self.assertEqual(main(["run", "--root", self.root]), 0)
        text = (self.tmp / "work/loop-01/approvals.yaml").read_text()
        self.assertIn("decision: pending", text)
        self.assertNotIn("simulated reviewer", text)

class MeridaleScenarioTests(unittest.TestCase):
    """The executive storyboard scenario: two loops, synonym decisions, stable ids through renames."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(KIT / "scenarios" / "meridale" / "inputs", self.tmp / "inputs")
        self.root = str(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_two_loops(self):
        self.assertEqual(main(["simulate", "--root", self.root, "--loop", "loop-01"]), 0)
        self.assertEqual(main(["simulate", "--root", self.root, "--loop", "loop-02"]), 0)
        els = {(e["kind"], e["name"]): e for e in json.loads((self.tmp / "outputs/loop-02/elements.json").read_text())}
        self.assertEqual(els[("identifier", "Customer Number")]["properties"]["issued_by"], "FinCore")
        self.assertEqual(els[("entity", "Client")]["properties"]["realises"], els[("concept", "Customer")]["id"])
        self.assertIn("separate_from", els[("entity", "Account")]["properties"])
        self.assertNotIn("Account", els[("concept", "Customer")]["aliases"])
        self.assertIn("credit-score-svc", els[("system", "CreditScore")]["aliases"])
        ch = json.loads((self.tmp / "outputs/loop-02/changes.json").read_text())
        self.assertEqual(ch["summary"]["contradictions_resolved"], 3)
        self.assertEqual(ch["removed"], [])
        gates = json.loads((self.tmp / "work/loop-02/gates.json").read_text())
        self.assertTrue(all(g["status"] == "provisional" for g in gates))

class NorthmereDecompositionTests(unittest.TestCase):
    """Monolith decomposition: TAXCORE split into Customer, PAYE, NI and Childcare domains."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        src = KIT / "scenarios" / "northmere"
        shutil.copytree(src / "inputs", self.tmp / "inputs")
        for f in ("target_domains.yaml", "reference_ontology.yaml", "scenario.yaml"):
            shutil.copy(src / f, self.tmp / f)
        self.root = str(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_decomposition(self):
        self.assertEqual(main(["simulate", "--root", self.root, "--loop", "loop-01"]), 0)
        dec = json.loads((self.tmp / "outputs/loop-01/decomposition/decomposition.json").read_text())
        owner = {e: k for k, s in dec["summary"].items() for e in s["entities"]}
        self.assertEqual(owner["Person"], "customer")
        self.assertEqual(owner["PayPeriod"], "paye")
        self.assertEqual(owner["NiRecord"], "ni")
        self.assertEqual(owner["ChildcareAccount"], "childcare")
        self.assertEqual([(s["column"], s["to"]) for s in dec["splits"]], [("NI_NUMBER", "ni")])
        self.assertEqual({x["event"] for x in dec["cross_domain_writes"]}, {"LifeEventRecorded"})
        self.assertIn({"consumer": "childcare", "provider": "paye"}, [{k: d[k] for k in ("consumer", "provider")} for d in dec["dependencies"]])
        self.assertEqual(dec["unassigned"], [])
        for k in ("customer", "paye", "ni", "childcare"):
            self.assertTrue((self.tmp / f"outputs/loop-01/decomposition/domains/{k}.yaml").exists())
            self.assertTrue((self.tmp / f"outputs/loop-01/decomposition/services/{k}.openapi.yaml").exists())
        gates = json.loads((self.tmp / "work/loop-01/gates.json").read_text())
        self.assertTrue(all(g["status"] == "provisional" for g in gates))
        diag = self.tmp / "outputs/loop-01/diagrams"
        for name in ("ba-concept-map", "ea-system-context", "ea-capability-map", "da-entity-relationship",
                     "eng-calculation-flow", "steward-aliases", "steward-decomposition", "conformance-grades", "conformance-gates"):
            self.assertTrue((diag / f"{name}.mmd").exists(), name)
        self.assertIn("erDiagram", (diag / "da-entity-relationship.mmd").read_text())


if __name__ == "__main__":
    unittest.main()

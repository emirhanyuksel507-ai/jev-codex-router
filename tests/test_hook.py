"""Unit and integration tests for Jev-Codex-Router."""

import json
import unittest
import subprocess
import sys
import os

from jev_codex_router.engine import JevDecisionEngine
from jev_codex_router.assembler import ContextAssembler
from jev_codex_router.hook import parse_input, run_hook
from jev_codex_router.constants import MAX_INJECTED_CONTEXT_CHARS


class TestJevCodexRouter(unittest.TestCase):

    def setUp(self):
        self.engine = JevDecisionEngine()
        self.assembler = ContextAssembler()

    def test_parse_valid_json_input(self):
        raw = '{"session_id": "123", "prompt": "build auth service"}'
        parsed = parse_input(raw)
        self.assertEqual(parsed.get("prompt"), "build auth service")

    def test_parse_plain_text_fallback(self):
        raw = "simple prompt string"
        parsed = parse_input(raw)
        self.assertEqual(parsed.get("prompt"), "simple prompt string")

    def test_empty_input_handling(self):
        res = run_hook("")
        self.assertEqual(res["hookSpecificOutput"]["additionalContext"], "")

    def test_trivial_greeting_pruned(self):
        decision = self.engine.evaluate("merhaba")
        self.assertTrue(decision.is_trivial)
        context = self.assembler.assemble(decision, "merhaba")
        self.assertEqual(context, "")

    def test_backend_domain_classification(self):
        prompt = "Create a FastAPI auth route and jwt middleware controller"
        decision = self.engine.evaluate(prompt)
        self.assertEqual(decision.domain, "backend")
        context = self.assembler.assemble(decision, prompt)
        self.assertIn("BACKEND", context)
        self.assertIn("asynchronous handlers", context)

    def test_database_domain_classification(self):
        prompt = "Optimize postgres query and write reversible SQL migration with index"
        decision = self.engine.evaluate(prompt)
        self.assertEqual(decision.domain, "database")
        context = self.assembler.assemble(decision, prompt)
        self.assertIn("DATABASE", context)
        self.assertIn("parameterized queries", context)

    def test_frontend_domain_classification(self):
        prompt = "Fix React modal CSS button layout and styling"
        decision = self.engine.evaluate(prompt)
        self.assertEqual(decision.domain, "frontend")
        context = self.assembler.assemble(decision, prompt)
        self.assertIn("FRONTEND", context)
        self.assertIn("accessible", context)

    def test_devops_domain_classification(self):
        prompt = "Write Dockerfile and github action CI pipeline script"
        decision = self.engine.evaluate(prompt)
        self.assertEqual(decision.domain, "devops")
        context = self.assembler.assemble(decision, prompt)
        self.assertIn("DEVOPS", context)
        self.assertIn("Pin dependency versions", context)

    def test_memory_vault_flag(self):
        prompt = "İkinci beyin vault notlarındaki önceki karar neydi?"
        decision = self.engine.evaluate(prompt)
        self.assertTrue(decision.needs_vault)
        context = self.assembler.assemble(decision, prompt)
        self.assertIn("Historical vault decisions may be relevant", context)

    def test_character_budget_enforced(self):
        decision = self.engine.evaluate("Explain database architecture")
        context = self.assembler.assemble(decision, "Explain database architecture")
        self.assertLessEqual(len(context), MAX_INJECTED_CONTEXT_CHARS)

    def test_cli_execution_via_stdin(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        env = os.environ.copy()
        env["PYTHONPATH"] = project_root

        payload = json.dumps({"prompt": "create fastapi endpoint"})
        proc = subprocess.run(
            [sys.executable, "-m", "jev_codex_router.hook"],
            input=payload,
            capture_output=True,
            text=True,
            cwd=project_root,
            env=env,
        )

        self.assertEqual(proc.returncode, 0)
        output = json.loads(proc.stdout)
        self.assertIn("hookSpecificOutput", output)
        self.assertIn("additionalContext", output["hookSpecificOutput"])
        self.assertEqual(output["hookSpecificOutput"]["domain"], "backend")


if __name__ == "__main__":
    unittest.main()

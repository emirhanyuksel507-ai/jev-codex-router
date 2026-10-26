"""Context Assembler: Prunes and compiles relevant rules within character budgets."""

import os
from typing import Optional
from jev_codex_router.constants import MAX_INJECTED_CONTEXT_CHARS
from jev_codex_router.engine import DecisionResult


class ContextAssembler:
    """Selects and formats domain rules based on Jev decisions."""

    def __init__(self, rules_dir: Optional[str] = None):
        if rules_dir:
            self.rules_dir = rules_dir
        else:
            self.rules_dir = os.path.join(os.path.dirname(__file__), "rules")

    def assemble(self, decision: DecisionResult, prompt: str) -> str:
        """Assembles pruned context payload matching decision parameters."""
        if decision.is_trivial:
            return ""

        rule_content = self._load_rule(decision.domain)
        if not rule_content and decision.domain != "general":
            rule_content = self._load_rule("general")

        header = f"[Jev-Router] Injected Domain Context ({decision.domain.upper()}) | Complexity: {decision.complexity}"
        
        vault_notice = ""
        if decision.needs_vault:
            vault_notice = "\n> [Notice]: Historical vault decisions may be relevant for this task."

        full_context = f"{header}{vault_notice}\n{rule_content}".strip()

        # Enforce hard character budget
        if len(full_context) > MAX_INJECTED_CONTEXT_CHARS:
            full_context = full_context[:MAX_INJECTED_CONTEXT_CHARS - 3] + "..."

        return full_context

    def _load_rule(self, domain: str) -> str:
        rule_path = os.path.join(self.rules_dir, f"{domain}.md")
        if os.path.exists(rule_path):
            try:
                with open(rule_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                return ""
        return ""

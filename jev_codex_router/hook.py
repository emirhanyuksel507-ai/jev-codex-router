"""Codex CLI UserPromptSubmit Hook Entrypoint."""

import sys
import json
import logging
from typing import Dict, Any

from jev_codex_router.engine import JevDecisionEngine
from jev_codex_router.assembler import ContextAssembler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("jev_codex_router")


def parse_input(raw_input: str) -> Dict[str, Any]:
    """Parses Codex CLI JSON or falls back to plain string."""
    raw_stripped = raw_input.strip()
    if not raw_stripped:
        return {"prompt": ""}
    try:
        data = json.loads(raw_stripped)
        if isinstance(data, dict):
            return data
        return {"prompt": str(data)}
    except Exception:
        return {"prompt": raw_stripped}


def run_hook(raw_stdin: str) -> Dict[str, Any]:
    """Main routing and context injection routine."""
    input_data = parse_input(raw_stdin)
    prompt = input_data.get("prompt", "")

    if not prompt:
        return {"hookSpecificOutput": {"additionalContext": ""}}

    try:
        engine = JevDecisionEngine()
        decision = engine.evaluate(prompt)

        assembler = ContextAssembler()
        injected_context = assembler.assemble(decision, prompt)

        return {
            "hookSpecificOutput": {
                "additionalContext": injected_context,
                "domain": decision.domain,
                "complexity": decision.complexity,
                "decisionSource": decision.source,
            }
        }
    except Exception as exc:
        # Graceful fallback: never crash developer workflow
        logger.warning("Router encountered error during processing: %s", exc)
        return {"hookSpecificOutput": {"additionalContext": ""}}


def main():
    try:
        raw_input = sys.stdin.read()
    except Exception:
        raw_input = ""

    result = run_hook(raw_input)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    sys.exit(0)


if __name__ == "__main__":
    main()

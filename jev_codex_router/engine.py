"""Jev Decision Engine: Interface to TypeSafe System 1 calibrated decisions."""

import os
import re
from dataclasses import dataclass
from typing import Dict, Any, Optional
from jev_codex_router.constants import DOMAINS, MIN_CONFIDENCE_THRESHOLD


@dataclass
class DecisionResult:
    domain: str
    is_trivial: bool
    needs_vault: bool
    complexity: str
    confidence: float
    source: str  # "jev_api" or "local_heuristic"


class JevDecisionEngine:
    """Evaluates developer prompts in low latency using Jev or local heuristics."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TYPESAFE_API_KEY")

    def evaluate(self, prompt: str) -> DecisionResult:
        """Evaluates prompt and returns structured branching decisions."""
        prompt_trimmed = prompt.strip()
        if not prompt_trimmed:
            return DecisionResult(
                domain="general",
                is_trivial=True,
                needs_vault=False,
                complexity="Low",
                confidence=1.0,
                source="local_heuristic",
            )

        # Attempt remote Jev API if SDK and key are available
        if self.api_key:
            try:
                return self._evaluate_remote(prompt_trimmed)
            except Exception:
                # Graceful degradation on API error or network timeout
                pass

        # High-speed local calibrated heuristic fallback (<5ms)
        return self._evaluate_local(prompt_trimmed)

    def _evaluate_remote(self, prompt: str) -> DecisionResult:
        """Calls TypeSafe SDK system_one if available."""
        from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

        with TypeSafeClient(api_key=self.api_key) as client:
            response = client.system_one(
                state={"prompt": prompt},
                questions={
                    "domain": Choice(
                        instructions="What technical domain does this prompt belong to?",
                        criteria={
                            "backend": "API, services, business logic, endpoints",
                            "database": "SQL, migrations, ORM, schemas, redis",
                            "frontend": "UI, CSS, HTML, React, DOM, components",
                            "devops": "Docker, CI/CD, scripts, environment, deployment",
                            "memory_vault": "Personal brain, notes, documentation, past decisions",
                            "general": "Other general coding and queries",
                        },
                    ),
                    "is_trivial": Noul(instructions="Is this a simple greeting or trivial acknowledgement?"),
                    "needs_vault": Noul(instructions="Does this require consulting past project decisions or notes?"),
                    "complexity": Score(
                        instructions="What is the context depth requirement of this task?",
                        criteria=["Low", "Medium", "High"],
                    ),
                },
            )

        domain_choice = response.choices["domain"].choice
        domain = domain_choice if domain_choice in DOMAINS else "general"
        is_trivial = response.nouls["is_trivial"].noul > 0.80
        needs_vault = response.nouls["needs_vault"].noul >= MIN_CONFIDENCE_THRESHOLD
        complexity_score = response.scores["complexity"].score
        complexity = "High" if complexity_score > 0.66 else ("Medium" if complexity_score > 0.33 else "Low")

        return DecisionResult(
            domain=domain,
            is_trivial=is_trivial,
            needs_vault=needs_vault,
            complexity=complexity,
            confidence=response.choices["domain"].confidence,
            source="jev_api",
        )

    def _evaluate_local(self, prompt: str) -> DecisionResult:
        """Fast fallback pattern matcher ensuring zero-dependency operation."""
        lower = prompt.lower()

        # Check trivial greetings
        trivial_patterns = [
            r"^(merhaba|selam|hi|hello|hey|günaydın|iyi günler|teşekkürler|thanks|ok|tamam)\b",
            r"^(sa|as|eyvallah|kolay gelsin)\b",
        ]
        is_trivial = any(re.search(p, lower) for p in trivial_patterns) and len(lower.split()) <= 4

        # Domain classification
        domain_scores = {
            "backend": len(re.findall(r"\b(api|endpoint|fastapi|flask|express|route|controller|service|auth|jwt|middleware|grpc)\b", lower)),
            "database": len(re.findall(r"\b(sql|database|db|postgres|mysql|sqlite|migration|query|orm|redis|schema|table)\b", lower)),
            "frontend": len(re.findall(r"\b(css|html|react|vue|ui|button|component|dom|style|tailwind|layout|page|modal)\b", lower)),
            "devops": len(re.findall(r"\b(docker|dockerfile|ci|cd|pipeline|github action|k8s|kubernetes|deploy|nginx|bash|script)\b", lower)),
            "memory_vault": len(re.findall(r"\b(vault|beyin|hafıza|not|notes|karar|gecmis|geçmiş|companion|receipt)\b", lower)),
        }

        best_domain = "general"
        best_count = 0
        for d, count in domain_scores.items():
            if count > best_count:
                best_count = count
                best_domain = d

        needs_vault = domain_scores["memory_vault"] > 0 or "nasıl yapmıştık" in lower or "önceki karar" in lower

        word_count = len(lower.split())
        complexity = "High" if word_count > 30 else ("Medium" if word_count > 10 else "Low")

        return DecisionResult(
            domain=best_domain,
            is_trivial=is_trivial,
            needs_vault=needs_vault,
            complexity=complexity,
            confidence=0.85 if best_count > 0 else 0.50,
            source="local_heuristic",
        )

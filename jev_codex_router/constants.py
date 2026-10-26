"""Constants and thresholds for Jev-Codex-Router."""

JEV_MODEL_ALIAS = "jev-latest"
API_BASE_URL = "https://api.typesafe.ai/v1"
MAX_HOOK_TIMEOUT_SECONDS = 2.0
TARGET_LATENCY_MS = 150

MAX_INJECTED_CONTEXT_CHARS = 2000
MIN_CONFIDENCE_THRESHOLD = 0.70

DOMAINS = [
    "backend",
    "database",
    "frontend",
    "memory_vault",
    "devops",
    "general",
]

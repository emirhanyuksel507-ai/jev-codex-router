# Backend Domain Rules
- Prefer asynchronous handlers (async/await) for I/O bound operations.
- Enforce strict input validation using schemas (Pydantic / Zod / dataclasses).
- Always include structured error handling and log correlation IDs.
- Keep route handlers thin; delegate business logic to service layers.

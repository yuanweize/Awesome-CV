# Evidence-First CV for Dify

Dify Tool Plugin for validated career memory, JD-to-claim selection, and strict
application-manifest checks. See [`../README.md`](../README.md) for deployment,
Chatflow setup, privacy boundaries, and the conversation contract.

```bash
uv sync --frozen
uv run python -m main       # remote debugging after private .env setup
```

From the repository root, use `make dify-package` so the archive is staged without
the local virtual environment and inspected before use.

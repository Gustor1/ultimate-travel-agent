# Contributing to Ultimate Travel Agent

Thank you for your interest in contributing to `ultimate-travel-agent`! We welcome contributions that align with our core principles: privacy-first, evidence-based, generic travel planning, and safe multi-agent execution.

---

## Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Core Guidelines

1. **Privacy & Security First**:
   - Never commit API keys, personal credentials, private trip records, or PII.
   - Never introduce automated booking, payment, or irreversible actions.
   - External dependencies must be audited and minimal.

2. **Verification Standards**:
   - All mock or curated data must include an explicit `verification_level`.
   - Prefer official links for booking and entry regulations over commercial aggregators.

3. **Multi-Agent Decoupling**:
   - Keep agents specialized with clear input/output contracts.
   - Do not introduce circular agent dependencies.

---

## Development Workflow

1. **Fork and Clone** the repository.
2. **Create a branch**: `git checkout -b feature/your-feature-name`.
3. **Install dev dependencies**:
   ```bash
   pip install -e ".[dev,mcp]"
   ```
4. **Run code quality checks**:
   ```bash
   ruff check src tests
   ruff format --check src tests
   mypy src
   pytest
   ```
5. **Commit and Push**: Ensure commit messages are descriptive and concise.
6. **Open a Pull Request**: Detail what changed, why, and how you verified it.

---

## Reporting Issues

- For bug reports or feature requests, open an issue on GitHub with reproduction steps.
- For security vulnerabilities, please follow our [Security Policy](SECURITY.md) and do not report publicly.

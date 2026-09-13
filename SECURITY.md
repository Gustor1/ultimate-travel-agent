# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |

---

## Security Principles

`ultimate-travel-agent` is designed with security and privacy by design:

1. **Zero Financial / Booking Execution**: The system strictly refuses to perform financial transactions, enter credit card details, or trigger automated bookings. All bookings must be completed manually by the user via official links.
2. **Offline-First & Local Sovereignty**: All baseline models, validation rules, and agent logic execute locally without sending personal travel records to third parties.
3. **No Credential Storage**: No secrets, tokens, or personal identifiers (passports, national IDs) should ever be committed to the repository.
4. **Input Sanitization & Injection Defense**: External inputs, web scrapes, and user prompts are strictly sanitized and checked by the `mcp-skill-auditor` to prevent indirect prompt injections.

---

## Reporting a Vulnerability

If you discover a security vulnerability, please do NOT create a public issue.

Instead, please send an email to:
`security@ultimate-travel-agent.local` (or file a private security advisory through GitHub).

Please include:
- A description of the vulnerability.
- Steps or a minimal proof-of-concept to reproduce the issue.
- Potential impact and affected components.

We will acknowledge your report within 48 hours and coordinate remediation.

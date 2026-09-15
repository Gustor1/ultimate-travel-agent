# Workflow: Audit External Tool or MCP

## 1. Purpose
Audits candidate Model Context Protocol (MCP) servers, third-party skills, or external APIs prior to enabling them in a traveler's AI environment.
Guarantees compliance with project safety invariants: zero automatic purchases, zero private credential storage, and strict sandbox isolation.

## 2. Agents Involved
- `mcp-skill-auditor` (Lead)
- `mcp-skill-auditing` (Skill)

## 3. Input / Output Contracts
- **Input**: Tool manifest, MCP server schema, SKILL.md file, or API documentation.
- **Output**: Security and privacy evaluation report with safety rating and adoption recommendation.

## 4. Step-by-Step Execution Process
1. **Permission Scope Analysis**: Check requested tool capabilities (filesystem write, network sockets, command execution, environment variable reads).
2. **Financial & Booking Risk Audit**: Verify that the tool has NO capability to execute automated bookings, enter credit card details, or trigger financial transactions.
3. **Data Privacy & Credential Review**: Confirm that user personal data, passport numbers, and API tokens are not transmitted to third-party endpoints.
4. **Prompt Injection & Integrity Check**: Inspect system prompts and tool descriptions for potential prompt injection vectors or safety bypasses.
5. **Verdict Generation**: Deliver a formal verdict: APPROVED, RESTRICTED_LOCAL_ONLY, or REJECTED.

## 5. Deliverables
- Tool Security Audit Report
- Permission & Data Flow Analysis
- Official Verdict & Integration Guidelines

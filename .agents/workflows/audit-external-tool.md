# Workflow: Audit External Tool or MCP

## Purpose

Statically assess an exact version of an external MCP server, skill, connector, API, or tool before adoption. Run only when an external component is actually proposed; never as part of ordinary trip planning.

Read `../shared/compact-research-protocol.md`. Use an isolated context and return `compact-handoff/v2` finding IDs.

## Agents Involved

- `mcp-skill-auditor` using `mcp-skill-auditing`

## Process

1. Freeze the reviewed version/commit and inventory manifests, install hooks, binaries, direct/transitive dependencies, licences, updates, and unavailable source.
2. Map declared versus actual filesystem, command, browser, secret, network, redirect, telemetry, and retention capability.
3. Trace untrusted input and credentials to prompts, logs, commands, writes, and network sinks. Never execute the component during a static audit.
4. Record evidence location, exploit preconditions/path, inherent severity, mitigation, residual risk, and missing inspection material.
5. Return `APPROVED`, `RESTRICTED`, `INSUFFICIENT_EVIDENCE`, or `REJECTED`; do not equate absence of a visible finding with safety.

## Deliverables

- Finding and evidence artifacts
- Permission/data-flow map
- Version-scoped verdict and restrictions

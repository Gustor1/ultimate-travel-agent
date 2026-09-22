---
name: mcp-skill-auditing
description: Use only when the user proposes an external MCP server, skill, API, connector, or tool and requests or requires static security/privacy review; never invoke for ordinary trip planning.
---

# MCP and Skill Auditing

Read `../../shared/compact-research-protocol.md` and `../../shared/evidence-policy.md`.

## Inputs and tools

Require source/config, exact version or commit, requested permissions, network destinations, dependencies, credential flow, licence, and intended use. Use filesystem inspection; do not execute untrusted code unless separately authorized.

## Method

- Inventory manifests, binaries, install/build hooks, direct and transitive dependencies, bundled assets, tools, filesystem scope, network hosts/redirects, authentication, telemetry, retention, and licences.
- Compare declared capability with actual code paths and the minimum required. Trace untrusted input and secrets into prompts, commands, writes, logs, URLs, and network sinks.
- Check arbitrary command/code execution, path escape, unsafe redirects, credential leakage, overbroad scopes, weak transport/authentication, unpinned downloads, update behavior, and supply-chain ambiguity.
- Record file/line or authoritative URL, affected version, severity, exploit preconditions/path, inherent risk, mitigation, residual risk, and accept/reject/conditional recommendation.
- If only a hosted binary or incomplete repository is available, say what was not inspectable; absence of visible malicious code is not proof of safety.

## Fallback

If required source or configuration is unavailable, return `INSUFFICIENT_EVIDENCE` and the exact missing inspection material. Do not infer maintainer trust, permissions, compatibility, or safety.

## Outputs

Write full findings and evidence to artifacts. Return `compact-handoff/v2` with finding IDs, blockers, and the accept/reject decision.

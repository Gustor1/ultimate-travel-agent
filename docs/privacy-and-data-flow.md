# Privacy and Data Flow

The pack stores no traveler database. Most tools are local. Network access occurs only
through the explicitly open-world `connector-read`, `connector-fetch`, and
`notify-webhook` tools, or through web tools supplied by the host agent runtime.

## Local data

Trip briefs, generated dossiers, installation manifests, and local exports remain wherever the user or host runtime saves them. The repository does not implement analytics, telemetry, accounts, or cloud storage.

## Queries through host tools

Use only the minimum operational fields needed for research:

- route, dates, party count, cabin or room requirements;
- destination, mobility category, dietary category, or general interests;
- no names, passport numbers, birth dates, payment data, loyalty identifiers, medical diagnoses, home addresses, or private calendar descriptions.

Nationality may be necessary for visa research. Use a generic query such as `official entry rules for Canadian passport holder Costa Rica`, not a traveler identity.

## Evidence retention

`TravelDossier v1` records source URLs, retrieval dates, expiry dates, and supported claims. It does not require cookies, browser sessions, credentials, or raw page archives.

## Secrets

- Keep credentials outside prompts and dossiers.
- `.gitignore` reduces accidental commits but is not a runtime secret-control system.
- Use host secret stores for optional external tools.
- MCP connector and webhook credentials are read from named environment variables;
  their values are not accepted as tool arguments or returned in results.
- Audit every connector's scopes, logging, retention, and subprocess behavior before enabling it.

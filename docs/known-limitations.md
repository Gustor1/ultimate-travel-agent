# Known Limitations

- Output quality depends on the host model and its available tools.
- Agent and tool names are not standardized across runtimes; platform adapters remain experimental.
- Prompt instructions reduce risk but cannot enforce sandboxing or defeat every indirect prompt injection.
- Official sites may block automation, require JavaScript, redirect by locale, or expose no stable deep link.
- Comparison engines and airline sites may disagree; only the final direct-operator result supports booking readiness.
- Travel policies and prices expire quickly. `TravelDossier v1` blocks booking-ready status when critical evidence is stale or absent.
- Offline mode provides structure and arithmetic, not live travel facts.
- Legacy dossiers are accepted but stay in inspiration mode until migrated to claim-level evidence.
- The active branch contains a secure provider-neutral JSON connector, but provider-specific OAuth acquisition, response normalization, quotas, and commercial API accounts remain deployment responsibilities.
- The project has no browser UI, payment capability, or autonomous purchasing. Booking handoffs always return control to the user on the provider website.
- Human review remains mandatory before any purchase, reservation, visa decision, medical decision, or non-refundable commitment.

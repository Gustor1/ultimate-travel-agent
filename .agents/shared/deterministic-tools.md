# Deterministic tool routing

Prefer packaged commands over model-generated arithmetic or ad hoc scripts. Use `ultimate-travel-agent <command> --help` when invocation details are needed.

| Need | Command |
|---|---|
| Validate final evidence/readiness | `validate-dossier` |
| Validate an agent handoff | `validate-handoff` |
| Measure prompt corpus regression | `prompt-audit` |
| Canonicalize a source URL | `normalize-source-url` |
| Generate/check flight matrix | `flight-search-plan`, `flight-search-coverage` |
| Generate/check hotel coverage | `hotel-search-plan`, `hotel-search-coverage` |
| Compare hotel rates | `hotel-compare` |
| Score hotel-to-anchor mobility | `hotel-mobility` |
| Score neighborhood evidence | `neighborhood-score` |
| Compare true door-to-door costs | `compare-total-cost` |
| Build revalidation tasks | `revalidation-plan` |
| Assess a price watch | `price-watch` |
| Build disruption recovery | `disruption-plan` |
| Build adaptive day variants | `adaptive-day` |
| Optimize time-window route | `route-optimize` |
| Prepare explicit booking handoff | `booking-handoff` |
| Resolve group preferences | `group-decide` |

Store command inputs and outputs as artifacts. A command validates or calculates supplied evidence; it does not make missing live facts true.

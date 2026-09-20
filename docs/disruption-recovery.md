# Targeted Disruption Recovery

`disruption-plan` handles a sourced closure, cancellation, delay, strike, or weather event without rebuilding the entire trip.

```console
ultimate-travel-agent disruption-plan disruption.yaml
```

The input contains the current `itinerary`, one sourced `disruption`, and candidate recovery `options`. Only explicitly affected item IDs are replaceable. Unaffected items are returned unchanged, and replacement options that overlap a fixed item are rejected.

A recovery plan is complete only when every affected item has an available, verified, source-linked, conflict-free replacement. Selection is deterministic: lowest extra cost, then earliest start, then stable option ID. The command performs no booking and never treats an unverified suggestion as confirmed availability.

Use `--cascade` when itinerary items declare `depends_on_item_ids` and `minimum_connection_minutes`. A delayed replacement then propagates to every train, hotel, activity, or other reservation whose safe connection is no longer possible. Every propagated item also requires its own verified replacement; otherwise the recovery plan remains blocked.

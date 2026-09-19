# Door-to-Door Optimization

Version 1.8 adds two deterministic checks that operate on sourced research data. They do not scrape or invent live information.

## Hotel mobility

`hotel-mobility` evaluates journeys from a shortlisted hotel to weighted trip anchors such as the airport, station, city center, and principal activities. Its score includes total time, walking, transfers, frequency, bus-only dependence, required service hours, and step-free access.

Required anchors without a journey are blockers. A journey outside the walking limit, outside verified operating hours, or without required step-free access is also blocked. Every journey carries a source URL and verification date.

```console
ultimate-travel-agent hotel-mobility mobility.yaml --maximum-walking-minutes 12
```

## True travel cost

`compare-total-cost` ranks only options covering every declared required category. Components use exact decimals and verified components require source IDs. The result separates direct supplier cost, optional time cost, and the configurable reserve applied to separate tickets or self-transfers.

```console
ultimate-travel-agent compare-total-cost options.yaml
```

The input contains `options`, `required_categories`, optional `value_of_time_per_hour`, and optional `separate_ticket_reserve_percent`. Typical required categories are `airfare`, `baggage`, and `airport_transfer`; add lodging, local transport, breakfast, or an extra night whenever the comparison requires them.

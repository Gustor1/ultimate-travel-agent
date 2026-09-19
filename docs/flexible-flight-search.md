# Flexible flight search

The flight-search system uses four deterministic passes:

1. requested airports and exact dates;
2. exact dates with bounded alternative gateways;
3. principal airports with the complete requested date grid (`±1` to `±3` days);
4. every valid date pair combined with every alternative route.

For a seven-night round trip with `flex_days: 3`, Pass 3 generates 48 new date pairs in addition to the baseline. Two alternative gateways produce 96 Pass 4 cells. The matrix is complete before any price result is ranked.

## Gateway rules

An alternative is not just an airport code. It includes its onward connection to the real destination: mode, time, likely cost, last departure, border crossing, separate ticket, baggage recheck, safe buffer, and entry/visa verification.

Each matrix cell can search direct, one-stop, and two-stop flight itineraries. Retained offers store ordered flight segments with timezone-aware timestamps, so domestic connections, layover duration, route continuity, and self-transfer exposure can be checked mechanically.

This supports searches such as:

- Hong Kong through HKG, Shenzhen SZX, or Guangzhou CAN;
- Shanghai through PVG and real regional gateways such as Hangzhou HGH, Nanjing NKG, or Wuxi WUX followed by the stated rail/road segment.

These examples define combinations to investigate; they do not assert current service, price, entry eligibility, or connection availability.

## Generate a search plan

```bash
ultimate-travel-agent flight-search-plan request.yaml flight-plan.json
```

The generated cells initially have `status: pending`. A browser-enabled host records each one as `searched`, `unavailable`, or `skipped`. The latter two require a reason.

```bash
ultimate-travel-agent flight-search-coverage flight-plan.json
ultimate-travel-agent flight-search-coverage flight-plan.json --booking-ready
```

`--booking-ready` also requires source evidence on searched cells. Matrix generation and arithmetic work offline; live prices still require browser/API access and direct-airline verification.

# Claim-Flow Telemetry Summary — Epsilon Children's Hospital

Synthetic 30-day hourly claim telemetry (window starting 2026-01-01T00:00:00Z, 720 hourly
buckets) for provider `epsilon` on the ClearFlow Payment Network.

## Baseline (Day 0, pre-incident)

- Monthly claim volume: ~96,000 claims; baseline throughput ~133 claims/hour.
- Intraday pattern: business hours (08:00-18:00) run at 1.4x the base rate; nights at 0.6x.
- Day-0 total: 3,073 claims. Anomaly score steady at 0.12; anomaly flag false.

## Cascade anomaly (Day 1 onward)

- Starting 2026-01-02T00:00:00Z, claim flow is suppressed to **35%** of baseline (a sustained ~65%
  drop) across all hours — the signature correlated across all six ClearFlow provider
  customers that triggers Reversal 1.
- Suppressed daily throughput: ~1,066 claims/day.
- Anomaly score jumps to at least **0.75** and oscillates weekly up to 0.921;
  anomaly flag true on every bucket from Day 1 through Day 29 with no recovery trend.
- Concentration: electronic remittance and eligibility transaction flows.

---
*Synthetic corpus document for the CascadeCare Network Command demonstration. Aggregates the
deterministic `ClaimTelemetry` Data Fabric records for `epsilon` exactly; no real claim data.*

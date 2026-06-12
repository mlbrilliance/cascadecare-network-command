#!/usr/bin/env python3
"""Generate the Context Grounding corpus documents from the canonical seed data.

Two corpora, both derived from scripts/seed_data_fabric.py so retrieval answers
always agree with the structured Data Fabric records:

  data/context-grounding/baa-corpus/<baa-id>.txt
      Synthetic full-text Business Associate Agreement per provider, embedding
      the exact seeded terms (notification window, permitted/forbidden
      disclosures, pre-disclosure consultation, indemnification, governing
      law). Ingested into the BAA-corpus index read by the BAA Boundary
      Reasoner. All entities are fictional (synthetic-baa-author constraints).

  data/context-grounding/claimtelemetry-corpus/telemetry-<provider>.txt
      (.txt because Context Grounding extraction silently skips .md — proven
      live 2026-06-12: ingestion reports Successful but search returns 0)
      Narrative rollup of the deterministic 30-day hourly telemetry (baseline,
      Day-1 cascade suppression, anomaly profile) per provider. Ingested into
      the ClaimTelemetry-corpus index.

Deterministic: same seed tables in -> same bytes out. Re-run after any change
to PROVIDERS/BAAS/telemetry in seed_data_fabric.py; the gate test
(tests/unit/scripts/test_gen_cg_corpus.py) fails on drift.

Usage:
  python3 scripts/gen_cg_corpus.py            # writes under data/context-grounding/
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "data" / "context-grounding"

_spec = importlib.util.spec_from_file_location(
    "seed_data_fabric", Path(__file__).resolve().parent / "seed_data_fabric.py"
)
assert _spec is not None
assert _spec.loader is not None
seed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(seed)

DISCLOSURE_LABELS = {
    "regulator": "state insurance regulators with jurisdiction over Covered Entity operations",
    "federal_regulator": "federal regulators and federal program integrity contractors",
    "insurer": "the Business Associate's cyber liability insurer and its appointed panel",
    "counsel": "outside legal counsel engaged for breach response",
    "media": "media organizations or any public communication channel",
    "payer_without_consent": "payer organizations absent prior written consent of Covered Entity",
}


def _disclosure_lines(terms: list[str]) -> str:
    return "\n".join(
        f"- `{t}` — {DISCLOSURE_LABELS.get(t, t)}" for t in terms
    )


def build_baa_docs() -> dict[str, str]:
    providers = {pid: row for row in seed.PROVIDERS for pid in [row[0]]}
    docs: dict[str, str] = {}
    for (bid, prov, ver, notif, consult, permitted, forbidden, indem, law) in seed.BAAS:
        p = providers[prov]
        display, vertical, hospitals = p[1], p[2], p[3]
        consult_clause = (
            "Business Associate shall complete a pre-disclosure consultation with Covered "
            "Entity's designated privacy officer and shall NOT notify any third party, "
            "including regulators, before joint forensic review concludes, except where "
            "disclosure is compelled by law."
            if consult
            else "No pre-disclosure consultation is required; Business Associate may proceed "
            "with notifications inside the window above."
        )
        pediatric = (
            "\n## 9. Special Handling — Pediatric Data\n\n"
            "All Protected Health Information of minor patients is subject to heightened "
            "safeguards. Disclosure of pediatric PHI to any federal body (`federal_regulator`) "
            "is expressly prohibited without a court order, and all permitted disclosures "
            "must be minimum-necessary with pediatric identifiers masked.\n"
            if prov == "epsilon"
            else ""
        )
        docs[f"{bid}.txt"] = f"""# Business Associate Agreement — {display}

**Agreement ID:** {bid} · **Version:** version {ver} · **Governing law:** State of {law}

This Business Associate Agreement ("BAA") is entered into between **{display}**
("Covered Entity", a {vertical.replace("_", " ")} operating {hospitals} hospital facility(ies))
and **ClearFlow Health Network** ("Business Associate"), a healthcare payment intermediary
providing claim pricing (ClearFlow Pricing Engine) and payment routing (ClearFlow Payment
Network) services. All parties, identifiers, and terms herein are synthetic demonstration data.

## 1. Definitions

"Breach", "Protected Health Information (PHI)", "Security Incident", and "Subcontractor"
carry the meanings given in 45 CFR Parts 160 and 164. "Claim metadata" includes transaction
identifiers, routing records, and anomaly telemetry processed on behalf of Covered Entity.

## 2. Breach Notification Window

Business Associate shall notify Covered Entity of any Breach of unsecured PHI, or any
Security Incident materially affecting claim flow integrity, **within {notif} hours** of
discovery. Notification shall include the nature of the Breach, the classes of PHI involved,
and interim containment measures.

## 3. Pre-Disclosure Consultation

{consult_clause}

## 4. Permitted Disclosures

Business Associate may disclose Breach-related information, including claim metadata that
may constitute PHI, to the following parties only:

{_disclosure_lines(permitted)}

## 5. Prohibited Disclosures

Business Associate shall NOT disclose Breach-related information or PHI to:

{_disclosure_lines(forbidden)}

## 6. Indemnification

{indem}.

## 7. Subcontractor Flow-Down

Business Associate shall ensure that any Subcontractor with access to Covered Entity PHI —
including the Nimbus Patient Engagement Platform integration — is bound in writing to
restrictions no less protective than this BAA, and shall treat a Subcontractor-originated
Breach as its own for the purposes of Section 2.

## 8. Regulatory Cooperation

Where Section 4 permits regulator disclosure, Business Associate shall cooperate with duly
issued civil investigative demands and subpoenas, subject to Sections 3 and 5, and shall
notify Covered Entity before producing records that identify Covered Entity patients.
{pediatric}
---
*Synthetic corpus document for the CascadeCare Network Command demonstration. Mirrors Data
Fabric record `{bid}` exactly; not legal advice; no real entities.*
"""
    return docs


def build_telemetry_docs() -> dict[str, str]:
    rows = seed._claim_telemetry_records()  # noqa: SLF001 — same script family, single source of truth
    docs: dict[str, str] = {}
    for (pid, display, _v, _h, _npi, monthly_vol, *_rest) in seed.PROVIDERS:
        hourly_base = max(1, monthly_vol // (30 * 24))
        mine = [r for r in rows if r["provider_id"] == pid]
        day0 = [r for r in mine if not r["anomaly_flag"]]
        after = [r for r in mine if r["anomaly_flag"]]
        day0_total = sum(r["claim_count"] for r in day0)
        after_daily = sum(r["claim_count"] for r in after) // 29
        peak_score = max(r["anomaly_score"] for r in after)
        first_anom = min(r["period_start"] for r in after)
        docs[f"telemetry-{pid}.txt"] = f"""# Claim-Flow Telemetry Summary — {display}

Synthetic 30-day hourly claim telemetry (window starting 2026-01-01T00:00:00Z, 720 hourly
buckets) for provider `{pid}` on the ClearFlow Payment Network.

## Baseline (Day 0, pre-incident)

- Monthly claim volume: ~{monthly_vol:,} claims; baseline throughput ~{hourly_base} claims/hour.
- Intraday pattern: business hours (08:00-18:00) run at 1.4x the base rate; nights at 0.6x.
- Day-0 total: {day0_total:,} claims. Anomaly score steady at 0.12; anomaly flag false.

## Cascade anomaly (Day 1 onward)

- Starting {first_anom}, claim flow is suppressed to **35%** of baseline (a sustained ~65%
  drop) across all hours — the signature correlated across all six ClearFlow provider
  customers that triggers Reversal 1.
- Suppressed daily throughput: ~{after_daily:,} claims/day.
- Anomaly score jumps to at least **0.75** and oscillates weekly up to {peak_score};
  anomaly flag true on every bucket from Day 1 through Day 29 with no recovery trend.
- Concentration: electronic remittance and eligibility transaction flows.

---
*Synthetic corpus document for the CascadeCare Network Command demonstration. Aggregates the
deterministic `ClaimTelemetry` Data Fabric records for `{pid}` exactly; no real claim data.*
"""
    return docs


def main() -> None:
    for sub, docs in (
        ("baa-corpus", build_baa_docs()),
        ("claimtelemetry-corpus", build_telemetry_docs()),
    ):
        out = OUT_DIR / sub
        out.mkdir(parents=True, exist_ok=True)
        for name, text in sorted(docs.items()):
            (out / name).write_text(text)
            print(f"wrote {out / name}")  # noqa: T201


if __name__ == "__main__":
    main()

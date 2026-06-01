#!/usr/bin/env python3
"""Generate (and optionally apply) the CascadeCare Data Fabric seed.

WHY THIS EXISTS — Slice 019 (c). Every agent that reads Provider / Payer / BAA /
ClaimTelemetry data runs against an empty Data Fabric until this seed lands. The
R1→R5 narrative needs the 9 entities + the 2 Context Grounding indexes populated
with the synthetic, IP-clean reference data specified in
`specs/003-uipath-native/data-model.md`.

Two modes (driven by `scripts/seed_data_fabric.sh`):
  --emit-json   (default, OFFLINE)  Print the full seed document to stdout. This
                is what the Slice-019 gate validates — no tenant required.
  --apply       (LIVE, gated by UIPATH_LIVE=1 + a prior `uip login`)  Create the
                entity schemas, insert the records, and create the CG indexes via
                the `uip df` / `uip context-grounding` CLI.

Deterministic by construction (no randomness, fixed base date) so the seed and
its gate are reproducible. Reads only `data-model.md`-specified shapes; never
writes to `knowledge/`. No secrets — live auth comes from the uip session.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

# Forbidden real-company tokens (CLAUDE.md / constitution II). Mirrored from the
# existing doc gates; consolidation into a shared conftest constant is the
# tracked polish-slice candidate.
FORBIDDEN = (
    "zelis", "aetna", "cigna", "unitedhealth", "cotiviti", "optum",
    "change healthcare", "wex ", "rivet", "bcbs", "hartley", "zipp", "zapp",
)

# Our field types → Data Fabric field types (live `uip df entities create`).
TYPE_MAP = {
    "string": "Text", "int": "Number", "float": "Decimal",
    "decimal": "Decimal", "bool": "YesNo", "datetime": "DateTime",
    "array<string>": "Text",  # serialized JSON in a Text field for the demo
    "uuid": "Text",
}

# Fixed base for deterministic ClaimTelemetry timestamps (narrative "Day 1").
BASE_DAY = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
TELEMETRY_DAYS = 30
TELEMETRY_HOURS = 24

# --------------------------------------------------------------------------- #
# Reference data tables (synthetic; canonical names per CLAUDE.md + data-model) #
# --------------------------------------------------------------------------- #

PROVIDERS = [
    # id, display_name, vertical, hospital_count, npi_count, monthly_claim_volume,
    # monthly_revenue_band, risk_profile, runway_days
    ("northstar", "Northstar Regional Health", "integrated_delivery_network", 7, 4200, 480_000, "enterprise", "high_acuity", 45),
    ("alpha", "Alpha Academic Medical Center", "academic", 1, 3100, 260_000, "large", "high_acuity", 60),
    ("beta", "Beta Community Hospital", "rural", 1, 220, 18_000, "small", "primary_care_dominant", 10),
    ("gamma", "Gamma Health Partners", "for_profit_chain", 1, 1900, 210_000, "large", "primary_care_dominant", 30),
    ("delta", "Delta Surgical Institute", "specialty_surgical", 1, 140, 24_000, "medium", "surgical_concentrated", 20),
    ("epsilon", "Epsilon Children's Hospital", "childrens", 1, 900, 96_000, "medium", "pediatric", 15),
]

PAYERS = [
    # id, display_name, payer_type, activity_level, regulatory_jurisdiction, outstanding_payments_band
    ("apex", "Apex Health Plan", "commercial", "active_antagonist", "multi_state", "large"),
    ("summitblue", "SummitBlue Medicare Advantage", "medicare_advantage", "active_federal", "federal", "very_large"),
    ("union-prairie", "Union Prairie Benefits", "tpa", "named_only", "state", "small"),
    ("lakeshore", "Lakeshore TPA Services", "self_funded_admin", "named_only", "state", "medium"),
]

VENDOR = {
    "id": "nimbus",
    "display_name": "Nimbus Patient Engagement Platform",
    "vendor_type": "patient_engagement_saas",
    "connected_providers": [p[0] for p in PROVIDERS],
    "breach_evidence_signal_strength": "weak",
}

REGULATOR = {
    "id": "tn-doi",
    "display_name": "Tennessee Department of Insurance",
    "regulator_type": "state_insurance_dept",
    "jurisdiction": "Tennessee",
    "subpoena_template_id": "tn-doi-subpoena-2026",
    "response_deadline_days": 14,
}

INSURER = {
    "id": "aurora-specialty",
    "display_name": "Aurora Specialty",
    "insurer_type": "cyber_specialty",
    "policy_limits_band": "large",
    "policy_directives": [
        "no public statement without counsel review",
        "retain Northwall Forensics",
        "preserve all logs",
    ],
}

COUNSEL = {
    "id": "hawthorne-mercer",
    "display_name": "Hawthorne Mercer LLP",
    "counsel_type": "cyber_breach_response",
    "privilege_directives": [
        "subpoena-response grandchildren: work-product privilege",
        "fiduciary-conflict grandchildren: attorney-client privilege",
    ],
}

# BAAs — heterogeneous on purpose. Encodes the 3 engineered conflict patterns:
#  1. northstar requires 24h notification; alpha forbids notification before
#     forensic review (pre_disclosure_consultation=true) → Day-5 conflict.
#  2. apex demands payer disclosure that alpha forbids without consent → R4.
#  3. summitblue federal reporting beta PERMITS but epsilon FORBIDS.
BAAS = [
    # id, provider_id, version, notif_hours, pre_consult, permitted, forbidden, indemnification, governing_law
    ("baa-northstar", "northstar", "2024.03", 24, False,
     ["regulator", "insurer", "counsel"], ["media"],
     "ClearFlow indemnifies provider for vector-attributable breach", "TN"),
    ("baa-alpha", "alpha", "2023.11", 72, True,
     ["counsel"], ["payer_without_consent", "media"],
     "Mutual indemnification capped at annual fees", "IL"),
    ("baa-beta", "beta", "2024.06", 48, False,
     ["regulator", "federal_regulator", "insurer", "counsel"], ["media"],
     "Provider waives consequential damages", "DE"),
    ("baa-gamma", "gamma", "2024.01", 48, False,
     ["regulator", "insurer", "counsel"], ["media"],
     "ClearFlow indemnifies for gross negligence only", "TN"),
    ("baa-delta", "delta", "2023.09", 72, True,
     ["counsel"], ["payer_without_consent", "media"],
     "Mutual indemnification, no cap for willful misconduct", "NY"),
    ("baa-epsilon", "epsilon", "2024.04", 24, False,
     ["regulator", "insurer", "counsel"], ["federal_regulator", "media"],
     "ClearFlow indemnifies; pediatric data special handling", "NY"),
]

REGULATOR_TEMPLATE = {
    "id": "tn-doi-subpoena-2026",
    "regulator_id": "tn-doi",
    "template_type": "subpoena",
    "legal_basis": "TCA 56-7-1003 et seq.",
    "discovery_requests": [
        "all claim-flow telemetry for affected TN-domiciled providers",
        "breach-vector forensic findings",
        "BAA notification timeline",
        "vendor (Nimbus) connection inventory",
    ],
    "response_form_url": "datafabric://regulator-templates/tn-doi-subpoena-2026-form.pdf",
}

# Entity schemas (field -> our type). Drives the live `uip df entities create`.
SCHEMAS: dict[str, dict[str, str]] = {
    "Provider": {
        "id": "string", "display_name": "string", "vertical": "string",
        "hospital_count": "int", "npi_count": "int", "monthly_claim_volume": "int",
        "monthly_revenue_band": "string", "risk_profile": "string", "baa_id": "string",
        "business_continuity_runway_days": "int",
    },
    "Payer": {
        "id": "string", "display_name": "string", "payer_type": "string",
        "activity_level": "string", "regulatory_jurisdiction": "string",
        "outstanding_payments_band": "string",
    },
    "Vendor": {
        "id": "string", "display_name": "string", "vendor_type": "string",
        "connected_providers": "array<string>", "breach_evidence_signal_strength": "string",
    },
    "Regulator": {
        "id": "string", "display_name": "string", "regulator_type": "string",
        "jurisdiction": "string", "subpoena_template_id": "string",
        "response_deadline_days": "int",
    },
    "Insurer": {
        "id": "string", "display_name": "string", "insurer_type": "string",
        "policy_limits_band": "string", "policy_directives": "array<string>",
    },
    "Counsel": {
        "id": "string", "display_name": "string", "counsel_type": "string",
        "privilege_directives": "array<string>",
    },
    "BAA": {
        "id": "string", "provider_id": "string", "version": "string",
        "notification_window_hours": "int", "requires_pre_disclosure_consultation": "bool",
        "permitted_disclosures": "array<string>", "forbidden_disclosures": "array<string>",
        "indemnification_clause": "string", "governing_law": "string",
        "document_blob_url": "string",
    },
    "ClaimTelemetry": {
        "id": "uuid", "provider_id": "string", "period_start": "datetime",
        "claim_count": "int", "total_billed_amount": "decimal",
        "anomaly_score": "float", "anomaly_flag": "bool",
    },
    "RegulatorTemplate": {
        "id": "string", "regulator_id": "string", "template_type": "string",
        "legal_basis": "string", "discovery_requests": "array<string>",
        "response_form_url": "string",
    },
}

CONTEXT_GROUNDING_INDEXES = ["BAA-corpus", "ClaimTelemetry-corpus"]


# --------------------------------------------------------------------------- #
# Record builders                                                             #
# --------------------------------------------------------------------------- #

def _provider_records() -> list[dict]:
    return [
        {
            "id": pid, "display_name": name, "vertical": vertical,
            "hospital_count": hosp, "npi_count": npi, "monthly_claim_volume": vol,
            "monthly_revenue_band": band, "risk_profile": risk,
            "baa_id": f"baa-{pid}", "business_continuity_runway_days": runway,
        }
        for (pid, name, vertical, hosp, npi, vol, band, risk, runway) in PROVIDERS
    ]


def _payer_records() -> list[dict]:
    return [
        {
            "id": pid, "display_name": name, "payer_type": ptype,
            "activity_level": act, "regulatory_jurisdiction": juris,
            "outstanding_payments_band": band,
        }
        for (pid, name, ptype, act, juris, band) in PAYERS
    ]


def _baa_records() -> list[dict]:
    return [
        {
            "id": bid, "provider_id": prov, "version": ver,
            "notification_window_hours": notif,
            "requires_pre_disclosure_consultation": consult,
            "permitted_disclosures": permitted, "forbidden_disclosures": forbidden,
            "indemnification_clause": indem, "governing_law": law,
            "document_blob_url": f"datafabric://baa-corpus/{bid}.pdf",
        }
        for (bid, prov, ver, notif, consult, permitted, forbidden, indem, law) in BAAS
    ]


def _claim_telemetry_records() -> list[dict]:
    """30 days x 24 hours x 6 providers = 4320 deterministic rows.

    Day 0 is pre-incident baseline (low anomaly); Day 1+ carries the sustained
    cascade anomaly (flag set, score >= 0.75) that triggers Reversal 1.
    """
    rows: list[dict] = []
    for pid, _name, _v, _h, _npi, monthly_vol, _band, _risk, _runway in PROVIDERS:
        hourly_base = max(1, monthly_vol // (30 * 24))
        for day in range(TELEMETRY_DAYS):
            for hour in range(TELEMETRY_HOURS):
                ts = BASE_DAY + timedelta(days=day, hours=hour)
                # Deterministic intraday pattern: busier 8:00–18:00.
                day_factor = 1.4 if 8 <= hour <= 18 else 0.6
                anomalous = day >= 1
                drop = 0.35 if anomalous else 1.0  # cascade suppresses claim flow
                claim_count = int(hourly_base * day_factor * drop)
                billed = round(claim_count * 182.5, 2)  # synthetic avg billed/claim
                score = 0.12 if not anomalous else round(0.75 + 0.2 * ((day % 7) / 7.0), 3)
                rows.append({
                    "id": f"ct-{pid}-{day:02d}-{hour:02d}",
                    "provider_id": pid,
                    "period_start": ts.isoformat().replace("+00:00", "Z"),
                    "claim_count": claim_count,
                    "total_billed_amount": billed,
                    "anomaly_score": score,
                    "anomaly_flag": anomalous,
                })
    return rows


def _schema_document(entity: str) -> list[dict]:
    """Live-mode schema body: [{name, type}] with DF field types."""
    return [
        {"name": field, "type": TYPE_MAP[our_type]}
        for field, our_type in SCHEMAS[entity].items()
    ]


def build_seed() -> dict:
    records = {
        "Provider": _provider_records(),
        "Payer": _payer_records(),
        "Vendor": [VENDOR],
        "Regulator": [REGULATOR],
        "Insurer": [INSURER],
        "Counsel": [COUNSEL],
        "BAA": _baa_records(),
        "ClaimTelemetry": _claim_telemetry_records(),
        "RegulatorTemplate": [REGULATOR_TEMPLATE],
    }
    entities = {
        name: {"schema": _schema_document(name), "records": rows}
        for name, rows in records.items()
    }
    return {"entities": entities, "contextGroundingIndexes": CONTEXT_GROUNDING_INDEXES}


# --------------------------------------------------------------------------- #
# IP-safety self-check                                                        #
# --------------------------------------------------------------------------- #

def assert_ip_clean(seed: dict) -> None:
    blob = json.dumps(seed).lower()
    hits = [tok for tok in FORBIDDEN if tok in blob]
    if hits:
        raise SystemExit(f"IP-SAFETY VIOLATION in seed content: {hits}")


# --------------------------------------------------------------------------- #
# Live apply (UIPATH_LIVE=1)                                                  #
# --------------------------------------------------------------------------- #

def _uip(*args: str) -> None:
    print(f"    $ uip {' '.join(args)}", file=sys.stderr)
    subprocess.run(["uip", *args], check=True)


def apply_live(seed: dict) -> None:
    if os.environ.get("UIPATH_LIVE") != "1":
        raise SystemExit("Refusing to apply: set UIPATH_LIVE=1 and run `uip login` first.")
    for name, payload in seed["entities"].items():
        print(f"==> Ensuring entity {name} ({len(payload['records'])} records)", file=sys.stderr)
        _uip("df", "entities", "create", name, "--body", json.dumps(payload["schema"]))
        # Records are inserted by entity name; the live operator confirms the
        # entity id returned by `create`/`list` maps to this name.
        _uip("df", "records", "insert", name, "--body", json.dumps(payload["records"]))
    for index in seed["contextGroundingIndexes"]:
        print(f"==> Creating Context Grounding index {index}", file=sys.stderr)
        _uip("context-grounding", "create", index)
    print("==> Live seed complete.", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CascadeCare Data Fabric seed generator")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--emit-json", action="store_true", help="print seed JSON (offline, default)")
    group.add_argument("--apply", action="store_true", help="apply to tenant (requires UIPATH_LIVE=1)")
    args = parser.parse_args(argv)

    seed = build_seed()
    assert_ip_clean(seed)

    if args.apply:
        apply_live(seed)
        return 0
    # Default: emit.
    json.dump(seed, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Business Associate Agreement — Epsilon Children's Hospital

**Agreement ID:** baa-epsilon · **Version:** version 2024.04 · **Governing law:** State of NY

This Business Associate Agreement ("BAA") is entered into between **Epsilon Children's Hospital**
("Covered Entity", a childrens operating 1 hospital facility(ies))
and **ClearFlow Health Network** ("Business Associate"), a healthcare payment intermediary
providing claim pricing (ClearFlow Pricing Engine) and payment routing (ClearFlow Payment
Network) services. All parties, identifiers, and terms herein are synthetic demonstration data.

## 1. Definitions

"Breach", "Protected Health Information (PHI)", "Security Incident", and "Subcontractor"
carry the meanings given in 45 CFR Parts 160 and 164. "Claim metadata" includes transaction
identifiers, routing records, and anomaly telemetry processed on behalf of Covered Entity.

## 2. Breach Notification Window

Business Associate shall notify Covered Entity of any Breach of unsecured PHI, or any
Security Incident materially affecting claim flow integrity, **within 24 hours** of
discovery. Notification shall include the nature of the Breach, the classes of PHI involved,
and interim containment measures.

## 3. Pre-Disclosure Consultation

No pre-disclosure consultation is required; Business Associate may proceed with notifications inside the window above.

## 4. Permitted Disclosures

Business Associate may disclose Breach-related information, including claim metadata that
may constitute PHI, to the following parties only:

- `regulator` — state insurance regulators with jurisdiction over Covered Entity operations
- `insurer` — the Business Associate's cyber liability insurer and its appointed panel
- `counsel` — outside legal counsel engaged for breach response

## 5. Prohibited Disclosures

Business Associate shall NOT disclose Breach-related information or PHI to:

- `federal_regulator` — federal regulators and federal program integrity contractors
- `media` — media organizations or any public communication channel

## 6. Indemnification

ClearFlow indemnifies; pediatric data special handling.

## 7. Subcontractor Flow-Down

Business Associate shall ensure that any Subcontractor with access to Covered Entity PHI —
including the Nimbus Patient Engagement Platform integration — is bound in writing to
restrictions no less protective than this BAA, and shall treat a Subcontractor-originated
Breach as its own for the purposes of Section 2.

## 8. Regulatory Cooperation

Where Section 4 permits regulator disclosure, Business Associate shall cooperate with duly
issued civil investigative demands and subpoenas, subject to Sections 3 and 5, and shall
notify Covered Entity before producing records that identify Covered Entity patients.

## 9. Special Handling — Pediatric Data

All Protected Health Information of minor patients is subject to heightened safeguards. Disclosure of pediatric PHI to any federal body (`federal_regulator`) is expressly prohibited without a court order, and all permitted disclosures must be minimum-necessary with pediatric identifiers masked.

---
*Synthetic corpus document for the CascadeCare Network Command demonstration. Mirrors Data
Fabric record `baa-epsilon` exactly; not legal advice; no real entities.*

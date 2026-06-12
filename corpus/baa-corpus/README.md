# BAA Corpus — Source Documents for the `BAA-corpus` Context Grounding Index

Synthetic Business Associate Agreements (BAAs) between **ClearFlow Health Network**
(the Business Associate) and each Covered Entity provider customer. These are the
source documents ingested into the `BAA-corpus` Context Grounding index used by the
**BAA Boundary Reasoner** agent.

## IP safety

100% synthetic. Party names use only the committed fictional names from `CLAUDE.md`
(Northstar Regional Health; Provider Alpha–Epsilon; Nimbus Patient Engagement
Platform; Apex Health Plan; SummitBlue Medicare Advantage). Regulatory references are
to public statute/regulation only (HIPAA, 45 CFR Part 164, HITECH) — no real company,
patient, claim, NPI, or litigation reference appears.

## Why the terms diverge on purpose

The demo's value is the agent **detecting cross-BAA conflicts** when a single event
(a state DOI subpoena, Reversal 3; payer demands, Reversal 4) hits ClearFlow's whole
book of business at once. So each BAA varies on the clauses that collide:

| Provider | Breach-notice window | Pre-disclosure notice to provider | Subpoena posture | Subcontractor (Nimbus) |
|---|---|---|---|---|
| Northstar Regional Health | 5 business days | 10 calendar days before any disclosure | BA must object & give provider time to quash | Flow-down required; provider pre-approval |
| Provider Alpha (urban academic) | 15 calendar days | None for "required by law" | BA may disclose on legal process, notice after | Permitted with notice |
| Provider Beta (rural community) | 60 calendar days (HIPAA default) | 5 business days | BA must object on provider's behalf | Prohibited without written consent |
| Provider Gamma (multi-state for-profit) | 72 hours | None | Multi-state law; broad disclosure | Permitted; indemnified |
| Provider Delta (specialty surgical) | 10 business days | 7 calendar days | BA may comply; minimum necessary | Flow-down required |
| Provider Epsilon (children's hospital) | 24 hours | 14 calendar days + court approval | BA must seek protective order (minor PHI) | Prohibited |

The headline conflict: a subpoena with a short production deadline collides with
Northstar's 10-day and Epsilon's 14-day-plus-court-approval pre-disclosure
requirements — ClearFlow cannot satisfy both at once.

## Files

- `BAA-Northstar-Regional-Health.md`
- `BAA-Provider-Alpha.md`
- `BAA-Provider-Beta.md`
- `BAA-Provider-Gamma.md`
- `BAA-Provider-Delta.md`
- `BAA-Provider-Epsilon.md`

## Ingestion

Upload all six BAA files into the `BAA-corpus` index in the **Shared** folder
(Studio Web → Indexes → BAA-corpus → ingest, or Orchestrator → Storage → Context
Grounding). If the index rejects `.md`, copy to `.txt` — content is identical.

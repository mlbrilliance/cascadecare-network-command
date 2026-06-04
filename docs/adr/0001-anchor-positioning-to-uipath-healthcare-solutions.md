# ADR-0001: Anchor positioning to UiPath Healthcare Agentic Solutions

- **Status:** accepted
- **Date:** 2026-06-03

## Context
CascadeCare competes in AgentHack 2026 Track 1 (Maestro Case). The strongest judging
lever we under-exploited is "Business Impact & Adoption" (20%). Our prior framing — a
brand-new category, "multi-customer cyber cascade" — is creative but reads as niche/abstract
to a judge deciding whether UiPath's Healthcare vertical would actually adopt it. At ViVE 2026
(2026-02-23) UiPath shipped named **Healthcare Agentic Solutions**: Medical Records
Summarization (MRS), Claim Denial Prevention & Resolution, and Prior Authorization. Maestro
Case itself reached **Controlled GA on 2026-03-30**.

## Decision
Position CascadeCare as the **Maestro Case orchestration layer ABOVE** UiPath's own Healthcare
Agentic Solutions. When a multi-customer cyber/financial shockwave hits, the individual denials,
prior-auths, and record summaries become one coordinated, multi-party crisis case. Slice S024
mocks MRS / Claim Denial Prevention / Prior Authorization as stage tasks so the crisis visibly
orchestrates them. README, Devpost, and the demo narrative lead with this framing.

## Rationale
Ties our adoption story to products UiPath already sells, making "the Healthcare vertical would
adopt this" concrete rather than aspirational — directly lifting the 20% Business-Impact axis
without diluting the genuinely novel three-level cascade (which remains the Creativity story).

## Alternatives considered
- Deepen the novel category only — higher creativity, but adoption stays abstract/niche.
- Generic reusable "ecosystem shockwave" template — broadest, but less sharp than a single,
  named vertical with existing UiPath products to orchestrate.

## Consequences
- S024 adds IP-safe `solution-*` mock tasks; README/positioning rewritten around the bridge.
- Future architecture reviews should NOT re-suggest dropping the healthcare-solution mock tasks
  as "scope creep" — they ARE the adoption thesis.
- All such mocks remain fictional and IP-safe (no real vendor/product names).

---
name: synthetic-baa-author
description: "Activate during synthetic data generation slices. Teaches how to author plausible, materially-differing BAA terms across 6 provider customers."
---

# Synthetic BAA Authoring

## Purpose

Generate six sets of plausible, materially-different Business Associate Agreement terms so that Reversal 3 (six legal answers to one subpoena) is credible.

## When to Activate

- Generating synthetic BAA data for provider customers
- Building Slice 006 (synthetic data)
- Testing the BAA Boundary Reasoner agent

## Provider Archetypes and BAA Variation

| Provider | Archetype | BAA Notification | Breach Threshold | Subcontractor Flow-Down |
|---|---|---|---|---|
| Northstar | 7-hospital regional, SE US | 72 hours | >500 records | Full flow-down required |
| Alpha | Urban academic, Mid-Atlantic | 24 hours | Any confirmed access | Strict flow-down + audit rights |
| Beta | Rural community, Midwest | Reasonable time (~30 days) | >1000 records | Basic flow-down |
| Gamma | Multi-state for-profit chain | 48 hours | Any unauthorized use | Full flow-down + indemnification cap |
| Delta | Specialty surgical network | 72 hours | >100 records | Standard flow-down |
| Epsilon | Children's hospital system | 24 hours | Any access to minor data | Enhanced flow-down + state AG notification |

## Variation Dimensions

Each BAA must differ on at least 3 of these 6 dimensions:
1. Notification timeline
2. Breach definition threshold
3. Disclosure scope (what counts as PHI)
4. Regulatory cooperation obligations
5. Subcontractor/vendor provisions
6. Indemnification and liability terms

## Output Format

Each synthetic BAA should produce a JSON structure with:
- provider_id, provider_name, archetype
- notification_hours, breach_threshold
- disclosure_scope (enum: clinical_only, clinical_plus_metadata, all_phi)
- regulatory_cooperation (enum: active, passive, conditional)
- subcontractor_flowdown (enum: basic, full, enhanced)
- indemnification_cap (dollar amount or "unlimited")
- special_provisions (array of strings)

## Anti-patterns

- Do not make all BAAs identical — the entire point is material difference
- Do not use real BAA text from any actual healthcare organization
- Do not include real dollar amounts from actual settlements
- Ensure the children's hospital (Epsilon) has the strictest terms — pediatric data carries enhanced protections

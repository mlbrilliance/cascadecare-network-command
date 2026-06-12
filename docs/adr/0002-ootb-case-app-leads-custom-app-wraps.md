# ADR-0002: OOTB Case App leads demo beats; custom App wraps

- **Status:** accepted
- **Date:** 2026-06-03

## Context
The UiPath Academy "Maestro Case" course trains viewers (and therefore judges) to recognize a
specific set of out-of-the-box surfaces: the OOTB **Case App** (activity timeline with actor
type + "Reworked" badge, SLA KPI tiles), the **Case Instances** heatmap/bottleneck view, and the
Case Instance Management lifecycle controls. We separately built a bespoke UiPath App,
`apps/clearflow-network-command`, as a "network command center" dashboard. Leading the demo with
only the bespoke App risks skipping the exact surfaces a judge is primed to look for.

## Decision
Lead all judge-facing demo beats with the **OOTB Case App + Case Instances heatmap** (configured
for all three case types), and use the bespoke `clearflow-network-command` App as the cinematic
executive **wrapper** around them. Both ship; neither is dropped (Slice S025).

## Rationale
Maximizes judge recognition (Platform Usage 20%, Presentation 10%) via canonical surfaces, while
keeping the differentiated visual that makes the entry memorable.

## Alternatives considered
- OOTB only — fully canonical but forfeits the bespoke "network command center" wow.
- Custom only — strongest unique visual but skips the surfaces judges are trained to recognize.

## Consequences
- S025 configures `caseApp` blocks in all three caseplans AND keeps the custom App bound to live
  Data Fabric + Maestro reads — more surfaces to wire and re-verify live.
- Future reviews should NOT propose deleting `apps/clearflow-network-command` as redundant; it is
  the wrapper by design.

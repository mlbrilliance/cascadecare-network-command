# Integration Service API Workflows (Slice 006)

One UiPath Integration Service **API Workflow** per external system. Each workflow
shapes the event payload its **Maestro Trigger** consumes, then returns it from a
`Response` activity in the single-expression object form (per the `uipath-api-workflow`
skill, critical rule 15).

Each file is `api_workflows/<slug>/main.json` — a valid CNCF Serverless Workflow
DSL `1.0.0` JSON (`document.dsl: "1.0.0"`, `evaluate.mode: "strict"`,
`evaluate.language: "javascript"`). `WorkflowStart` is always the first activity in
the root `Sequence_1`; user activities (a `JsInvoke` payload-builder + a `Response`)
follow it.

## Slug → event-type mapping

| # | Slug (`source_system`) | Event type emitted | Schema (`specs/003-uipath-native/event-contracts/`) | Reversal / beat |
|---|------------------------|--------------------|-----------------------------------------------------|-----------------|
| 1 | `provider-northstar`        | `provider-claim-anomaly` | `provider-claim-anomaly.json-schema.json` | R1 setup (~t+20s) |
| 2 | `provider-alpha`            | `provider-claim-anomaly` | `provider-claim-anomaly.json-schema.json` | R1 setup |
| 3 | `provider-beta`             | `provider-claim-anomaly` | `provider-claim-anomaly.json-schema.json` | R1 setup |
| 4 | `provider-gamma`            | `provider-claim-anomaly` | `provider-claim-anomaly.json-schema.json` | R1 setup |
| 5 | `provider-delta`            | `provider-claim-anomaly` | `provider-claim-anomaly.json-schema.json` | R1 setup |
| 6 | `provider-epsilon`          | `provider-claim-anomaly` | `provider-claim-anomaly.json-schema.json` | R1 setup |
| 7 | `payer-apex`                | `payer-demand`           | `payer-demand.json-schema.json`           | R4 driver (t+200s) |
| 8 | `payer-summitblue`          | `payer-demand`           | `payer-demand.json-schema.json`           | R4 secondary |
| 9 | `payer-union-prairie`       | `payer-demand`           | `payer-demand.json-schema.json`           | R4 secondary |
| 10 | `payer-lakeshore`          | `payer-demand`           | `payer-demand.json-schema.json`           | R4 secondary |
| 11 | `vendor-nimbus`            | `vendor-attribution`     | `vendor-attribution.json-schema.json`     | R2 (t+70s) |
| 12 | `regulator-tn-doi`         | `regulatory-subpoena` **or** `litigation-event` (parameterized) | `regulatory-subpoena.json-schema.json` / `litigation-event.json-schema.json` | R3 HERO (t+150s) / R5 (t+260s) |
| 13 | `insurer-aurora-specialty` | `insurer-directive`      | `insurer-directive.json-schema.json`      | R4 HITL gate (t+200s) |
| 14 | `counsel-hawthorne`        | **none** (utility)       | — (no schema)                             | Privilege-determination utility (not a Maestro event) |

### Note on `multi-customer-correlation`

The seventh event contract — `multi-customer-correlation` — is **NOT** an API Workflow.
It is emitted directly by the **Multi-Customer Pattern Detector Coded Agent**
(`source_system: multi-customer-pattern-detector`), which fires Reversal 1 by
correlating the six `provider-claim-anomaly` events. That is why there are 14 API
Workflow slugs (`source_systems` in `case-vocabulary.yaml`) but 7 event contracts:
6 providers + 4 payers + vendor + regulator (×2 events) + insurer all map to schemas;
counsel is a utility; and the correlation event has no workflow because the Coded
Agent owns it.

### Parameterized regulator workflow

`regulator-tn-doi/main.json` branches on its `event_type` input via the
`If_1#Wrapper` / `If_1#Then` / `If_1#Else` two-way pattern:

- `event_type = "litigation-event"` (`#Then`) → builds the **R5** `litigation-event`
  payload (`event_subtype: co_defendant_named`, `named_parties` drawn only from the
  approved cast: `ClearFlow Health Network`, `Nimbus Patient Engagement Platform`).
- otherwise (`#Else`, default `event_type = "regulatory-subpoena"`) → builds the
  **R3 HERO** `regulatory-subpoena` payload (`scope: all_providers`,
  `template_id: tn-doi-subpoena-2026`, `response_deadline_days: 14`).

Each branch ends with its own `Response` (`then: "end"`).

## Enum / const values chosen

| Workflow | Field | Value |
|----------|-------|-------|
| providers (×6) | `provider_id` | `northstar` / `alpha` / `beta` / `gamma` / `delta` / `epsilon` |
| `payer-apex` | `demand_type` | `data_access` (drives the R4 tri-party HITL gate) |
| `payer-summitblue` | `demand_type` | `coverage_challenge` |
| `payer-union-prairie` | `demand_type` | `idr_pause` |
| `payer-lakeshore` | `demand_type` | `settlement_pressure` |
| `vendor-nimbus` | `evidence_signal_strength` | `strong` (Day-5 attribution) |
| `regulator-tn-doi` (subpoena) | `scope` | `all_providers` |
| `regulator-tn-doi` (litigation) | `event_subtype` | `co_defendant_named` |
| `insurer-aurora-specialty` | `directive_type` | `reservation_of_rights` |

## What is shaped here vs. deferred to DEPLOY

**Shaped here (build-time, offline):** each workflow declares an `input.schema`
carrying the fields that would come from Data Fabric (e.g. `simulated_day`,
`claim_drop_pct`, `anomaly_score`, `target_provider_ids`, …) with sensible
**defaults**, then a `JsInvoke` activity assembles the event payload (constants like
`provider_id` / `source_system` / `event_type` are fixed per workflow), and a
`Response` returns it. No Integration Service connector activity
(`UiPath.IntSvc` / `UiPath.Http`) is hand-authored — the `uip` CLI is offline in
this environment and the skill forbids hand-authoring `metadata.configuration` /
`uiPathActivityTypeId`.

**Deferred to DEPLOY-TIME (against a live tenant):**

1. **Data Fabric connector read.** Replace the input-default payload-builder with a
   real connector activity that reads the source entity (ClaimTelemetry, Payer, Vendor,
   RegulatorTemplate, Insurer, …):
   `uip api-workflow registry resolve "<entity read op>" --output json` →
   `uip is connections ping <uuid>` →
   `uip api-workflow registry stub <activity-type-id> --connection-id <uuid> --output json`,
   then bind the stub's `ResponseFields` into the payload-builder.
2. **Maestro Trigger emission.** Wire each event payload to its Maestro Trigger
   (FilterTree shown in each schema's `maestro_trigger_filter_hint`). Same
   `registry resolve` + `stub` flow against the live Maestro endpoint.
3. **Packaging.** Add a `project.json` (`Type: "Api"`) per workflow folder, register
   them in the solution `.uipx`, and build with `uip solution pack <solutionDir>
   <outputDir>` then `uip solution publish`. `uip solution pack` auto-generates
   `operate.json` / `package-descriptor.json` — do NOT commit those.
4. **Validation.** Run `uip api-workflow validate <slug>/main.json` (offline static
   check) per file, then `uip api-workflow run --no-auth` once a tenant is available.

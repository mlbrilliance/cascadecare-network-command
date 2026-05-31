# clearflow-demo-driver — API Workflow Binding Manifest (DEPLOY-TIME)

Slice 012 Maestro Flow "Demo Driver". `uip` is OFFLINE in the build environment and
none of the `api_workflows/` slugs are published yet, so the registry UUID keys
(`uipath.core.api-workflow.<UUID>`), `resourceKey` values (`<FolderPath>.<ApiName>`),
and `bindings[]` pairs cannot be resolved here. Per the `uipath-maestro-flow` skill's
no-live-tenant rule, registry keys are NOT fabricated.

## What is built offline (this slice)

Each demo beat is a `core.action.script` payload-builder ("fire*" node) that returns
the exact event payload its target API Workflow emits (same `event_type` /
`source_system` / field constants as `api_workflows/<slug>/main.json`). Timing is
realized by `core.logic.delay` ("wait*") nodes. The chain is strictly sequential:

```
start → waitNorthstar → fireNorthstar → waitAlpha → fireAlpha → … → fireLitigationR5 → end
```

The `display.label` on every fire node names: `Fire <slug> → <event_type> [<reversal>]`.

## What is deferred to DEPLOY-TIME

At deploy, against a live tenant with the `api_workflows/` published, replace each
`fire*` script node with a real API Workflow node:

```bash
uip login
uip maestro flow registry pull --force
uip maestro flow registry search "uipath.core.api-workflow" --output json   # find the UUID + resourceKey per slug
uip maestro flow registry get "uipath.core.api-workflow.<UUID>" --output json
```

Then, per the skill's "Replace a mock with a real resource node" recipe
(editing-operations-json.md): swap `type` to `uipath.core.api-workflow.<UUID>`, move
the payload fields into `inputs` (the API Workflow's input schema), copy the definition
into `definitions[]`, and add two top-level `bindings[]` entries (`name` + `folderPath`)
per workflow with `resourceKey` matching the definition's `model.bindings.resourceKey`.

| fire node | target API Workflow slug | event_type | input schema source | reversal / beat |
|---|---|---|---|---|
| `fireNorthstar` | `provider-northstar` | `provider-claim-anomaly` | `api_workflows/provider-northstar/main.json` | R1 setup |
| `fireAlpha` | `provider-alpha` | `provider-claim-anomaly` | `api_workflows/provider-alpha/main.json` | R1 setup |
| `fireBeta` | `provider-beta` | `provider-claim-anomaly` | `api_workflows/provider-beta/main.json` | R1 setup |
| `fireGamma` | `provider-gamma` | `provider-claim-anomaly` | `api_workflows/provider-gamma/main.json` | R1 setup |
| `fireDelta` | `provider-delta` | `provider-claim-anomaly` | `api_workflows/provider-delta/main.json` | R1 setup |
| `fireEpsilon` | `provider-epsilon` | `provider-claim-anomaly` | `api_workflows/provider-epsilon/main.json` | R1 setup |
| `fireCorrelationR1` | `multi-customer-pattern-detector` (Coded Agent emits — NOT an API Workflow) | `multi-customer-correlation` | emitted by the Multi-Customer Pattern Detector Coded Agent | R1 DRIVER |
| `fireChildPhi` | `provider-northstar` | `provider-claim-anomaly` (`event_subtype: phi_exfiltration_signal`) | `api_workflows/provider-northstar/main.json` | Child: BA Exposure (Day 3) |
| `fireVendorR2` | `vendor-nimbus` | `vendor-attribution` | `api_workflows/vendor-nimbus/main.json` | R2 DRIVER |
| `fireChildLiquidity` | `provider-northstar` | `provider-claim-anomaly` (`event_subtype: liquidity_stress`) | `api_workflows/provider-northstar/main.json` | Child: Payment Continuity (Day 14) |
| `fireSubpoenaR3` | `regulator-tn-doi` (`event_type: regulatory-subpoena`) | `regulatory-subpoena` | `api_workflows/regulator-tn-doi/main.json` (#Else branch) | R3 HERO |
| `firePayerR4` | `payer-apex` | `payer-demand` | `api_workflows/payer-apex/main.json` | R4 DRIVER |
| `fireInsurerR4` | `insurer-aurora-specialty` | `insurer-directive` | `api_workflows/insurer-aurora-specialty/main.json` | R4 HITL gate |
| `fireLitigationR5` | `regulator-tn-doi` (`event_type: litigation-event`) | `litigation-event` | `api_workflows/regulator-tn-doi/main.json` (#Then branch) | R5 DRIVER |

> `fireCorrelationR1` has no API Workflow: the `multi-customer-correlation` event is
> emitted directly by the Multi-Customer Pattern Detector Coded Agent (see
> `api_workflows/README.md`). At deploy this beat is driven by the agent, not a flow
> node; the script here is a timeline marker for dry-runs.

## Two definitions to reconcile at deploy

These definitions were hand-authored from the skill's documented `model` fields because
no `uip maestro flow registry get` was available offline (the `core.action.script`,
`core.trigger.manual`, and `core.control.end` definitions are verbatim from validated
skill fixtures and need no reconciliation):

- `core.logic.delay` — verify `model.eventDefinition: "bpmn:TimerEventDefinition"` and
  `version` by re-copying from `uip maestro flow registry get core.logic.delay --output json`.

## Verify at deploy

```bash
uip maestro flow validate flow.json --output json
uip maestro flow format flow.json            # regenerates layout.nodes + variables.nodes
# dry-run sequence only after explicit consent (debug has real side effects):
# uip maestro flow debug flow.json
```

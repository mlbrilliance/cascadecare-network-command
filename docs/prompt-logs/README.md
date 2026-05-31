# Prompt logs — index

**Channel 3** of the coding-agent evidence set. The richest, already-committed prompt evidence
is the set of **authoritative agent prompt templates** Claude Code authored — these are real
build artifacts, not reconstructions:

| Committed prompt template | Drives |
|---|---|
| [`agents/prompts/vector_hypothesis_agent.md`](../../agents/prompts/vector_hypothesis_agent.md) | Vector Hypothesis Agent (R2) |
| [`agents/prompts/baa_boundary_reasoner.md`](../../agents/prompts/baa_boundary_reasoner.md) | BAA Boundary Reasoner (R3) |
| [`agents/prompts/fiduciary_conflict_detector.md`](../../agents/prompts/fiduciary_conflict_detector.md) | Fiduciary Conflict Detector (R4) |
| [`agents/prompts/negligent_monitoring_risk_agent.md`](../../agents/prompts/negligent_monitoring_risk_agent.md) | Negligent Monitoring Risk Agent (R5) |
| [`agents/prompts/claim_flow_anomaly_detector.md`](../../agents/prompts/claim_flow_anomaly_detector.md) | Claim Flow Anomaly Detector (coded) |
| [`agents/prompts/multi_customer_pattern_detector.md`](../../agents/prompts/multi_customer_pattern_detector.md) | Multi-Customer Pattern Detector (coded) |
| [`agents/prompts/forensic_self_exam_agent.md`](../../agents/prompts/forensic_self_exam_agent.md) | Forensic Self-Exam Agent (coded) |

These are the prompts that run **inside the deployed UiPath agents** (byte-identical to each
`agent.json` system prompt / coded-agent prompt).

## Build-session transcripts

Sanitized Claude Code build-session transcripts (the prompts that *authored* the artifacts) are
captured during the submission session and dropped here as `slice-0NN-*.md`. The durable
build narrative is already in [`../changelog.md`](../changelog.md).

**Status: build-session transcript capture PENDING (Slice 017).** Committed prompt-template
evidence above is complete.

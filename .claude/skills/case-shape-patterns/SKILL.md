---
name: case-shape-patterns
description: "Activate when designing any new case stage, child case, or grandchild case. Defines the six case-shape patterns Maestro Case must demonstrate."
---

# Case-Shape Patterns

## Purpose

Define and enforce the six case-shape patterns that distinguish this Maestro Case demonstration from a BPMN workflow.

## When to Activate

- Designing a new case stage or stage transition
- Creating or modifying child cases or grandchild cases
- Implementing case goal changes or participant role changes
- Building the three-level nesting structure

## The Six Patterns

### Pattern 1: Evolving Case Goals

The master case goal changes at each reversal. This is not a state machine with predefined transitions — goals emerge from new information.

| Reversal | Goal Before | Goal After |
|---|---|---|
| 1 | Assist isolated customers | Determine if ClearFlow is the vector |
| 2 | Am I the cause? | Strategic bystander posture |
| 3 | (unchanged) | + Per-customer BAA compliance |
| 4 | Strategic posture | Fiduciary conflict resolution |
| 5 | Fiduciary resolution | Co-defendant defense posture |

### Pattern 2: Evolving Participant Roles

Participants' roles change as the case evolves. ClearFlow starts as recovery coordinator, becomes conflict-governed intermediary, becomes co-defendant.

### Pattern 3: Multi-Level Case Nesting

Three levels: master → parent → grandchild. The third level emerges only when needed (Reversal 3).

### Pattern 4: Cross-Case Evidence Sharing with Privilege-Aware Access

Evidence is shared across cases but access depends on participant role and privilege status. When litigation arrives (Reversal 5), privilege reshuffles and some evidence becomes restricted.

### Pattern 5: Non-Sequential Human Approval Gates

HITL decisions don't follow a fixed sequence. They appear when the case demands them, sometimes reopening previously resolved decisions.

### Pattern 6: Case Reopening and Stage Re-Entry

Closed child cases can reopen. Completed stages can re-enter. The IDR Posture child case opens on Day 0, resolves, then reopens on Day 60 with a different posture question.

## Implementation Notes

- Every case goal change must be recorded in goalHistory
- Every participant role change must be recorded in roleHistory
- Evidence access scopes must be recalculated when privilege status changes
- Reopened cases/stages must preserve their previous history

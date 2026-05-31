---
description: "Dry-run the 3-minute demo end-to-end. Compares actual vs expected state per reversal."
user-invocable: true
---

# Rehearse Demo

Run a full demo rehearsal against the local stack.

## Steps

1. Reset demo state: `uv run python -m cascadecare.demo.reset`
2. Start the demo stack (mocks + agents + state store)
3. Execute each demo event in sequence:
   - Day 0: Northstar anomaly
   - Day 0: Alpha anomaly
   - Day 1: Beta anomaly -> Reversal 1 (correlation)
   - Day 3: PHI exfiltration signal (child event)
   - Day 5: Reversal 2 (ClearFlow cleared, Nimbus identified)
   - Day 14: Liquidity stress (child event)
   - Day 30: Reversal 3 (subpoena -> 6 BAA analyses -> grandchild cases)
   - Day 45: Reversal 4 (payer conflict -> fiduciary HITL)
   - Day 90: Reversal 5 (litigation -> co-defendant -> privilege reshuffle)
4. After each event, capture the case state snapshot
5. Compare actual state against expected state per reversal:
   - Master goal matches expected?
   - Correct child cases open?
   - Evidence count matches?
   - HITL decisions appeared?
   - Risk score updated?
6. Produce a Markdown report:

```markdown
# Demo Rehearsal Report — {timestamp}

## Summary
- Reversals passed: X/5
- Child events passed: X/2
- Total checks: X/Y

## Per-Reversal Results
### Reversal 1: Multi-Customer Correlation
- [PASS/FAIL] Master goal changed to "Determine if ClearFlow is the vector"
- [PASS/FAIL] Pattern Detector fired with 91% correlation
- [PASS/FAIL] 3+ child cases open
...
```

7. Save report to docs/rehearsal-reports/{timestamp}.md

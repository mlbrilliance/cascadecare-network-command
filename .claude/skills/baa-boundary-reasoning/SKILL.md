---
name: baa-boundary-reasoning
description: "Activate when the BAA Boundary Reasoner Agent runs or when a regulatory inquiry hits multiple affected provider customers. Teaches how to reason about a single regulatory inquiry against multiple differing BAA terms."
---

# BAA Boundary Reasoning

## Purpose

Guide reasoning about how a single regulatory inquiry (e.g., state DOI subpoena) produces materially different disclosure obligations across multiple provider customers, each with different Business Associate Agreement (BAA) terms.

## When to Activate

- BAA Boundary Reasoner Agent is running or being implemented
- A regulatory inquiry touches multiple provider customers with differing BAA terms
- Reversal 3 (state DOI subpoena collision) is being built or tested
- Grandchild BAA sub-cases are being created

## Key Concepts

### BAA Term Dimensions That Produce Different Outcomes

1. **Notification timeline**: Some BAAs require 24-hour notification, others 72 hours, others "reasonable time"
2. **Disclosure scope**: What constitutes "PHI potentially affected" differs — some BAAs include metadata, others only clinical data
3. **Regulatory cooperation clause**: Some BAAs require active cooperation with regulators, others allow passive compliance
4. **Indemnification terms**: Who bears the cost of regulatory response varies
5. **Breach definition threshold**: What counts as a "breach" vs. an "incident" varies by BAA
6. **Subcontractor flow-down**: Whether the SaaS vendor (Nimbus) is covered by the BAA's subcontractor provisions

### Analysis Structure

For each provider customer, the BAA Boundary Reasoner must produce:

1. **BAA Terms Summary**: Key provisions relevant to the specific inquiry
2. **Disclosure Obligation**: What ClearFlow must disclose, to whom, by when
3. **Legal Risk Assessment**: Exposure if ClearFlow over-discloses vs. under-discloses
4. **Recommended Action**: Specific recommended response with rationale
5. **Confidence Level**: High / Medium / Low with explanation
6. **Conflicts**: Where this customer's recommended action conflicts with another customer's BAA terms

### The Six-Answer Problem

The signature moment of Reversal 3: one subpoena from TN DOI produces six different legal positions because six provider customers have materially different BAA terms. ClearFlow cannot give one answer — it must give six, each defensible under that customer's specific BAA.

This is what spawns six grandchild BAA sub-cases, making three-level nesting a necessity rather than an architectural choice.

## Regulatory References

- HIPAA Privacy Rule: 45 CFR 164.502-514 (use and disclosure)
- HIPAA Breach Notification Rule: 45 CFR 164.400-414
- Business Associate provisions: 45 CFR 164.502(e), 164.504(e)
- State law variation: State DOI authority under state insurance codes

## Anti-patterns

- Do not produce identical analyses for different provider customers — the point is that they differ
- Do not cite real case numbers, settlement amounts, or enforcement actions
- Do not provide legal advice — label all outputs as "decision-support draft for counsel review"
- Do not use real company names in any BAA term examples

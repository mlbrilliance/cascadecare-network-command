---
name: regulatory-citer
description: "Activate whenever regulatory text appears in code, prompts, or docs. Guides precise citation of US healthcare regulatory sources."
---

# Regulatory Citation Guide

## Purpose

Ensure all regulatory citations in code, agent prompts, documentation, and UI text are precise and verifiable. Never fabricate case numbers, settlement amounts, or enforcement actions.

## When to Activate

- Writing agent prompts that reference regulations
- Creating synthetic regulatory communications
- Building mock regulator responses
- Writing documentation that mentions compliance frameworks

## Citable Regulatory Sources

### HIPAA (Health Insurance Portability and Accountability Act)

- Privacy Rule: 45 CFR Part 160 and Subparts A, E of Part 164
- Security Rule: 45 CFR Part 160 and Subparts A, C of Part 164
- Breach Notification Rule: 45 CFR Part 164 Subpart D (sections 164.400-414)
- Business Associate provisions: 45 CFR 164.502(e), 164.504(e)
- Enforcement: 45 CFR Part 160 Subparts C, D, E

### No Surprises Act / IDR

- NSA IDR process: 45 CFR Part 149 (specifically 149.510-149.520)
- Federal IDR portal and process rules
- State IDR variations where applicable

### SEC Disclosure

- SEC Item 1.05 (Form 8-K): Material cybersecurity incidents
- SEC Regulation S-K Item 106: Cybersecurity risk management

### False Claims Act

- FCA Civil Cyber-Fraud Initiative (DOJ)
- 31 U.S.C. sections 3729-3733

### State Insurance Codes

- State DOI authority: cite as "[State] Insurance Code section [X]" — use fictional state code sections
- NAIC Model Laws: cite by model number, not state-specific adoption

## Anti-patterns

- NEVER fabricate case numbers (e.g., "In re ClearFlow Health, Case No. 24-cv-1234")
- NEVER cite specific settlement amounts as if they are real ("$XX million settlement")
- NEVER cite real enforcement actions against real companies
- NEVER present regulatory analysis as legal advice — always label as "decision-support draft"
- When uncertain about a citation, use the general statute reference (e.g., "45 CFR 164.400-414") rather than inventing a specific subsection

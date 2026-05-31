# Security Hooks — Two-Layer Design

This harness wires the [Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills)
(754 skills, 26 domains) into your git workflow. But it does so in a way that
respects what skills actually are and what git hooks can actually do.

## The key distinction

**Skills are AI context, not executables.** A skill is a practitioner playbook an
AI agent loads and reasons with. A git hook is a shell script that runs
synchronously and must finish fast. A hook cannot "run a skill" directly — only
an AI agent can. So the security coverage is split into two layers triggered at
two different points:

| Layer | Trigger | Speed | Uses skills? | Blocks? |
|---|---|---|---|---|
| **Deterministic scan** | every commit (pre-commit) | milliseconds | No | Yes |
| **AI skill review** | before push (pre-push) | seconds–minutes | Yes (754 skills) | Advisory by default |

This split exists because running an AI review on *every commit* would make
committing painfully slow and expensive, and you'd disable it within a day.
Pre-push is the right cadence for the heavy review — it runs once before code
leaves your machine.

## Layer 1 — Deterministic scan (every commit)

`.agent-os/hooks/security_scan.py` runs on every commit and blocks if it finds:

- **Secrets** — OpenAI/AWS/GitHub/Slack/Google keys, private key blocks, JWTs,
  generic `password=`/`token=` assignments.
- **Dangerous patterns** — `eval`/`exec` on dynamic input, `pickle.loads`,
  `yaml.load` without SafeLoader, `shell=True`, disabled TLS verification,
  `os.system`, hardcoded `0.0.0.0` binds.

No AI, no network, no tokens. Pure pattern matching, milliseconds. This catches
the high-frequency mistakes before they ever reach the repo. Tuned for
high-confidence patterns to avoid false-positive fatigue.

## Layer 2 — AI skill-based review (before push)

`.agent-os/security/security_review.py` runs on pre-push. It:

1. Collects the diff of all commits being pushed.
2. Runs `skill_router.py` to identify *which* of the 754 skills are relevant
   (API code → API-security skills, IaC → DevSecOps/cloud skills, auth code →
   IAM skills, etc.). You never load all 754 — only the handful that apply.
3. Writes a **review brief** (diff + routed skill domains) to a temp file.
4. Prints instructions for your AI agent to perform the review using those skills.

By default this is **advisory** — it prepares the review and prints it but does
not block the push. To make it blocking, set `REVIEW_BLOCKING=1` and the push
fails until a signoff file exists (created after the agent reviews and you accept).

### Why routing matters

The 754 skills cost ~22K tokens just to scan frontmatter. Loading all of them on
every review is wasteful and pollutes the agent's context. The router inspects
what changed and emits only the relevant domains — typically 2–4 — so the agent
loads maybe 6–12 skills instead of 754.

## Setup

```bash
# 1. Clone the cybersecurity skills next to your project
git clone https://github.com/mukul975/Anthropic-Cybersecurity-Skills.git \
  ../Anthropic-Cybersecurity-Skills

# 2. Confirm the path in .agent-os/security/config.txt points to the clone
#    (default: ../Anthropic-Cybersecurity-Skills/skills)

# 3. Install the hooks
bash .agent-os/security/install_hooks.sh
```

That's it. Layer 1 now runs on every commit; Layer 2 on every push.

## Using the AI review

When you push, the pre-push hook prints a brief path and instructions. Hand it to
your agent:

```
Read /tmp/security-review-brief-<timestamp>.md and perform the security review
it describes. Load the routed cybersecurity skills from the
Anthropic-Cybersecurity-Skills repo, reason about each changed hunk, and report
findings as: SEVERITY | file:line | issue | applicable skill | fix.
```

The agent loads the routed skills, reviews the diff, and reports. You decide
whether to fix-and-re-push or accept.

### On-demand review (without pushing)

You can run the review any time on your staged changes:

```bash
python3 .agent-os/security/skill_router.py     # see which skills apply
python3 .agent-os/security/security_review.py  # generate a review brief
```

## Making it blocking

For a repo where security review is mandatory before push:

```bash
export REVIEW_BLOCKING=1
```

Now a push fails unless a signoff file exists next to the brief. The agent (or
you) creates it after an accepted review:

```bash
touch /tmp/security-review-brief-<timestamp>.md.signoff
```

## Customizing the router

`.agent-os/security/skill_router.py` has a `ROUTES` table mapping file signals to
skill domains. Add entries for your stack — e.g. if you have a `/payments/`
directory, route it to `compliance-governance` and `cryptography`. The more
precise the routing, the more relevant the review.

## What this is NOT

- It is **not** a replacement for a real SAST/DAST pipeline in CI. It's a
  developer-machine fast feedback loop. Run heavier scanners (Semgrep, CodeQL,
  Trivy) in CI as well.
- The AI review is **assistive**, not authoritative. It surfaces likely issues
  using expert playbooks; a human still owns the security decision.
- The deterministic scan is **high-confidence, not exhaustive**. It won't catch
  novel or obfuscated secrets. Pair it with `detect-secrets` (already in the
  pre-commit config) for entropy-based detection.

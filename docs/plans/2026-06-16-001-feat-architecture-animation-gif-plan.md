---
title: "feat: Animated architecture-diagram GIF for the README hero"
date: 2026-06-16
type: feat
depth: lightweight
status: ready
---

# feat: Animated architecture-diagram GIF for the README hero

## Summary

Produce a ~6-second, cleanly-looping **schematic animation GIF** of the existing CascadeCare
architecture diagram — the full diagram animating in place (master pipeline lights up → agents
plug in → the Reversal-3 6-way fan-out draws out → 3-level cascade lands → brief hold → loop).
Embed it at the marked GIF spot in `README.md`, **supplementing** (not replacing) the static
`docs/images/architecture.png`. It is an honest illustrative animation, not live-tenant footage —
labeled as such — and the existing "real live-run GIF is still ideal" human-capture note stays.

The whole asset is generated from the same parametric SVG the static diagram already uses, via
`cairosvg` (frame render) + `Pillow` (GIF assembly), both installed in the `uv` venv.

## Problem Frame

README research flagged a short live-run GIF as the single biggest remaining visual win, but a
true screen-capture needs the live UiPath tenant (unavailable from this environment). A schematic
animation of the hero moment is the achievable, honest substitute: it adds motion to the README
hero and reinforces the three-level fan-out story without claiming to be live footage.

## Requirements

- R1 — A single looping GIF at `docs/images/architecture.gif`, **< ~2 MB** (README-embeddable).
- R2 — Animates the **full architecture diagram** in place (per user choice), ending on the
  complete, static-equivalent frame so the loop seam is clean.
- R3 — On-brand: charcoal/orange Energy-Flow palette matching `docs/images/architecture.svg`.
- R4 — Embedded at the existing `<!-- TODO(human) … GIF … -->` spot in `README.md`, with a caption
  that explicitly says **schematic animation (illustrative, not live-tenant footage)**.
- R5 — Static `architecture.png`/`.svg` remain the primary diagram; the live-run-GIF human-capture
  TODO note remains (slimmed, not deleted).
- R6 — IP-safe (zero forbidden tokens); README completeness gate stays green; committed + pushed.

## Key Technical Decisions

- **KTD1 — Frame-driven reveal from the existing generator.** Adapt the proven static generator
  (`/tmp/gen_arch.py`) into a frame-capable variant that takes a frame index and gates each visual
  *band* (title → reversal/pipeline → agents → fan-out → Trust Layer → platform → footer) by a
  per-band reveal window, plus a draw-in animation for the six fan-out strands and a pulse on the
  "13 live case instances" callout. Reuses a known-good diagram; full control over choreography.
- **KTD2 — Size budget via width/frame/palette levers.** A detailed full-diagram GIF is inherently
  heavy. Hold to < 2 MB with: render width ~1000–1100 px (not 1680), ~24–30 frames, final frame
  *held by per-frame duration* (not duplicated frames), `Pillow` `save(..., loop=0, optimize=True)`
  with an adaptive ≤256-colour palette. If still over budget, step down (width 900 → frames 20 →
  palette 128) and re-measure. Record the final knobs in the commit.
- **KTD3 — Honesty framing.** Caption states "schematic animation … not live-tenant footage."
  Keeps the static diagram primary and the live-run-GIF TODO note. Protects submission integrity.
- **KTD4 — Generators stay in `/tmp` (uncommitted), only the GIF ships.** Consistent with the
  static `gen_arch.py` workflow; the committed deliverable is `docs/images/architecture.gif`. (Can
  be promoted to `scripts/` later if reproducibility is wanted — out of scope here.)

## Implementation Units

### U1. Frame-capable animation generator

- **Goal:** Emit the full architecture SVG for a given animation frame, with progressive band
  reveal + fan-out draw-in + final hold state.
- **Dependencies:** none (adapts existing `/tmp/gen_arch.py`).
- **Files:** `/tmp/gen_arch_anim.py` *(uncommitted build tool)*.
- **Approach:** Refactor the linear static builder into band-emitting functions; add a
  `frame(i, N)` driver that (a) ramps each band's opacity over its reveal window so bands appear in
  narrative order, (b) animates the six `Regulatory Response → parent` strands drawing in during the
  fan-out window, (c) pulses the "13 instances" callout as the cascade lands, and (d) renders the
  complete diagram for the final ~20% of frames. Final frame must equal a clean complete state for a
  seamless loop. Keep the exact stage/agent labels from the static diagram (already caseplan-accurate).
- **Test scenarios:** none — asset tooling; correctness verified by U2 render + visual inspection.

### U2. Render frames and assemble the looping GIF under budget

- **Goal:** Render every frame and assemble one looping `docs/images/architecture.gif` < ~2 MB.
- **Dependencies:** U1.
- **Files:** `docs/images/architecture.gif` *(output)*; `/tmp/build_gif.py` *(uncommitted assembler)*.
- **Approach:** Render each frame to PNG via `cairosvg` at the chosen width; assemble with `Pillow`
  (`loop=0`, per-frame `duration` ~180–220 ms with a longer hold on the final frame, `optimize=True`,
  adaptive palette). Measure file size; apply the KTD2 step-downs until < 2 MB. Visually verify the
  first / fan-out / final frames and the assembled GIF via render-and-Read.
- **Verification:** GIF exists, loops, < 2 MB, correct dimensions, and visibly shows build-up →
  fan-out → hold without a visible loop seam.
- **Test scenarios:** none — asset generation; verified by size + visual inspection.

### U3. Embed in README and ship

- **Goal:** Embed the GIF at the marked spot with an honest caption; keep the static PNG primary and
  the live-run TODO; pass gates; commit + push.
- **Dependencies:** U2.
- **Files:** `README.md`, `docs/images/architecture.gif`.
- **Approach:** Replace the `<!-- TODO(human) … GIF … -->` region with a centered
  `<p align="center"><img src="docs/images/architecture.gif" width="900" alt="…" /></p>` plus a
  caption: *"Schematic animation of the Reversal-3 cascade — illustrative, not live-tenant footage."*
  Retain a slim TODO note that a real live-run capture is still the ideal. `architecture.gif` is a
  `.gif`, so the `*.png` gitignore carve-out does not cover it — confirm GIFs aren't ignored (or add a
  carve-out) so it actually commits. Run the README completeness gate + forbidden-token scan; commit
  (guard the OneDrive `index.lock`) and push.
- **Test scenarios:** none behavioral — the existing `tests/unit/docs/test_readme_completeness.py`
  gate must remain green (every slug/LICENSE/coding-agents pointer preserved).

## Risks & Mitigations

- **Over budget (> 2 MB).** Detailed full-diagram animation is heavy. Mitigate via KTD2 levers; last
  resort is narrowing the animated region to the cascade band while keeping the full diagram as the
  held final frame. `log` whatever knob was used.
- **GIF colour banding.** SVG gradients → 256-colour GIF can band. Acceptable for a schematic;
  adaptive palette + `optimize` mitigate.
- **`.gif` accidentally gitignored.** The repo ignores `*.png` with a carve-out for the diagram; verify
  `.gif` is not similarly ignored before assuming the commit succeeded (mirror the PNG carve-out fix if
  needed).
- **OneDrive/WSL `index.lock`.** Guard commits with `[ -f .git/index.lock ] && rm -f .git/index.lock`.

## Verification

The GIF renders in the README at the marked spot; loops cleanly; < 2 MB; static diagram still
primary; honesty caption + live-run TODO present; README completeness gate green; zero forbidden
tokens; committed and pushed.

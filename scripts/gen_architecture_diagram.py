#!/usr/bin/env python3
"""Generate docs/images/architecture.svg — the CascadeCare architecture diagram.

Glassmorphism restyle: dark frosted-glass nodes with glowing colored borders,
soft outer glows, a faint circuit texture, a starfield background, and glowing
rails/connectors — while preserving the proven information architecture
(orchestration spine, 11 agents under their stages, 3-level case nesting, Trust
Layer, data/integration surfaces, vertical bridge, Claude Code footer + legend).

Render to PNG with headless Chrome (see scripts/render_architecture_png.sh).
Build-time tooling only — no runtime dependency.
"""
from __future__ import annotations

import random
from pathlib import Path

W, H = 1680, 1150

# --- palette -----------------------------------------------------------------
ACCENT = {
    "orange": "#FF9A5C",   # Maestro Case / orchestration
    "violet": "#9D8CF0",   # Agent Builder (Claude Sonnet 4.6)
    "cyan": "#4FD0F5",     # Coded Agent (Python SDK)
    "green": "#43D49A",    # Platform service
    "gold": "#F6C04A",     # Human gate
    "amber": "#F6B73C",    # Trust Layer
    "neutral": "#5C76A6",
}
TEXT = "#EAF2FF"      # primary light text on glass
MUTED = "#9FB2CC"     # secondary muted text
FONT = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"

_OUT = Path(__file__).resolve().parent.parent / "docs" / "images" / "architecture.svg"


# --- primitives --------------------------------------------------------------
def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size, fill=TEXT, weight=400, anchor="start", ls=0, op=1.0):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
        f'text-anchor="{anchor}" letter-spacing="{ls}" opacity="{op}">{esc(s)}</text>'
    )


def glass(x, y, w, h, rx, key, glow=0.42, sheen=True, circuit=False, bw=1.6, gf="glow"):
    """A frosted-glass rounded box: outer glow + glass fill + colored edge + sheen."""
    a = ACCENT[key]
    p = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{a}" '
        f'opacity="{glow}" filter="url(#{gf})"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#glass_{key})" '
        f'stroke="{a}" stroke-width="{bw}"/>',
    ]
    if circuit:
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                 f'fill="url(#circuit)" opacity="0.5"/>')
    if sheen:
        sh = min(h - 2.4, h * 0.5)
        p.append(f'<rect x="{x+1.2}" y="{y+1.2}" width="{w-2.4}" height="{sh}" rx="{rx}" '
                 f'fill="url(#sheen)"/>')
        p.append(f'<rect x="{x+rx}" y="{y+1.5}" width="{w-2*rx}" height="1.2" rx="0.6" '
                 f'fill="#ffffff" opacity="0.20"/>')
    return "".join(p)


def panel(x, y, w, h, rx, accent_key):
    a = ACCENT[accent_key]
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{a}" '
        f'opacity="0.10" filter="url(#glowL)"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#glass_panel)" '
        f'stroke="#2C3C5A" stroke-width="1.2"/>'
        f'<rect x="{x}" y="{y+rx}" width="3.5" height="{h-2*rx}" rx="1.75" fill="{a}" '
        f'opacity="0.5" filter="url(#glowS)"/>'
        f'<rect x="{x}" y="{y+rx}" width="3.5" height="{h-2*rx}" rx="1.75" fill="{a}"/>'
    )


def pill(x, y, w, h, s, key, size=11.5):
    a = ACCENT[key]
    cx = x + w / 2
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="#0C1322" '
        f'opacity="0.85"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="none" '
        f'stroke="{a}" stroke-width="1.2"/>'
        + text(cx, y + h / 2 + size * 0.36, s, size, a, 700, "middle")
    )


def rail(x1, x2, y, key, op=0.45):
    a = ACCENT[key]
    return (
        f'<rect x="{x1}" y="{y-1.6}" width="{x2-x1}" height="3.2" rx="1.6" fill="{a}" '
        f'opacity="{op*0.55}" filter="url(#glow)"/>'
        f'<rect x="{x1}" y="{y-0.8}" width="{x2-x1}" height="1.6" rx="0.8" fill="{a}" '
        f'opacity="{op}"/>'
    )


def dropper(cx, y1, y2, key, op=0.75):
    a = ACCENT[key]
    return (f'<line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2}" stroke="{a}" stroke-width="1.6" '
            f'opacity="{op}" marker-end="url(#ar_{key})"/>')


def arrow(x1, y1, x2, y2, key, w=2.2, op=0.85):
    a = ACCENT[key]
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{a}" stroke-width="{w}" '
            f'opacity="{op}" marker-end="url(#ar_{key})"/>')


def conn(d, key, w=1.6, op=0.55, dash=None, arrow_end=False):
    a = ACCENT[key]
    da = f' stroke-dasharray="{dash}"' if dash else ""
    me = f' marker-end="url(#ar_{key})"' if arrow_end else ""
    return f'<path d="{d}" fill="none" stroke="{a}" stroke-width="{w}" opacity="{op}"{da}{me}/>'


# --- defs --------------------------------------------------------------------
def build_defs() -> str:
    d = ['<defs>']
    # background gradient
    d.append('<linearGradient id="bg" x1="0" y1="0" x2="0.25" y2="1">'
             '<stop offset="0" stop-color="#0C1424"/>'
             '<stop offset="0.55" stop-color="#0A0E1A"/>'
             '<stop offset="1" stop-color="#070A12"/></linearGradient>')
    # nebula glow (top-right)
    d.append('<radialGradient id="neb" cx="0.78" cy="0.12" r="0.55">'
             '<stop offset="0" stop-color="#2A4A7A" stop-opacity="0.34"/>'
             '<stop offset="1" stop-color="#2A4A7A" stop-opacity="0"/></radialGradient>')
    d.append('<radialGradient id="neb2" cx="0.12" cy="0.92" r="0.5">'
             '<stop offset="0" stop-color="#7C4AB0" stop-opacity="0.16"/>'
             '<stop offset="1" stop-color="#7C4AB0" stop-opacity="0"/></radialGradient>')
    # glass fills per accent
    for key, a in ACCENT.items():
        d.append(f'<linearGradient id="glass_{key}" x1="0" y1="0" x2="0" y2="1">'
                 f'<stop offset="0" stop-color="{a}" stop-opacity="0.22"/>'
                 f'<stop offset="0.5" stop-color="#101A2C" stop-opacity="0.55"/>'
                 f'<stop offset="1" stop-color="#090E18" stop-opacity="0.66"/></linearGradient>')
    # neutral panel glass
    d.append('<linearGradient id="glass_panel" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#1B2740" stop-opacity="0.58"/>'
             '<stop offset="1" stop-color="#0A101C" stop-opacity="0.64"/></linearGradient>')
    # trust bar glass (horizontal)
    d.append('<linearGradient id="glass_trust" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#241B0E" stop-opacity="0.6"/>'
             '<stop offset="0.5" stop-color="#2C2112" stop-opacity="0.72"/>'
             '<stop offset="1" stop-color="#241B0E" stop-opacity="0.6"/></linearGradient>')
    # sheen
    d.append('<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.15"/>'
             '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>')
    # circuit texture
    d.append('<pattern id="circuit" width="28" height="28" patternUnits="userSpaceOnUse">'
             '<path d="M0 14 H28 M14 0 V28" stroke="#6F93C8" stroke-width="0.5" opacity="0.16"/>'
             '<path d="M14 14 L24 4" stroke="#6F93C8" stroke-width="0.5" opacity="0.12"/>'
             '<circle cx="14" cy="14" r="1.1" fill="#8FB4EC" opacity="0.22"/>'
             '<circle cx="0" cy="0" r="0.9" fill="#8FB4EC" opacity="0.16"/>'
             '<circle cx="28" cy="28" r="0.9" fill="#8FB4EC" opacity="0.16"/></pattern>')
    # glow filters
    d.append('<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
             '<feGaussianBlur stdDeviation="6"/></filter>')
    d.append('<filter id="glowS" x="-80%" y="-80%" width="260%" height="260%">'
             '<feGaussianBlur stdDeviation="3"/></filter>')
    d.append('<filter id="glowL" x="-30%" y="-30%" width="160%" height="160%">'
             '<feGaussianBlur stdDeviation="14"/></filter>')
    # arrowheads per accent
    for key, a in ACCENT.items():
        d.append(f'<marker id="ar_{key}" markerWidth="9" markerHeight="9" refX="6.5" refY="3" '
                 f'orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="{a}"/></marker>')
    d.append('</defs>')
    return "".join(d)


def build_starfield() -> str:
    rng = random.Random(7)
    s = []
    for _ in range(170):
        x = round(rng.uniform(24, W - 24), 1)
        y = round(rng.uniform(24, H - 24), 1)
        r = round(rng.uniform(0.4, 1.5), 2)
        op = round(rng.uniform(0.08, 0.6), 2)
        s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#CFE0FF" opacity="{op}"/>')
    return "".join(s)


# --- content -----------------------------------------------------------------
def build_body() -> str:
    b = []
    # background
    b.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg)"/>')
    b.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#neb)"/>')
    b.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#neb2)"/>')
    b.append(build_starfield())
    b.append(f'<rect x="16" y="16" width="{W-32}" height="{H-32}" rx="20" fill="none" '
             f'stroke="#26344E" stroke-width="1.2" opacity="0.6"/>')

    # ---- header ----
    b.append(text(46, 60, "CascadeCare Network Command", 33, TEXT, 700))
    b.append(rail(48, 478, 72, "orange", 0.9))
    b.append(text(46, 96, "The living case layer for healthcare financial shockwaves — a "
                          "UiPath Maestro Case, live on Automation Cloud", 14.5, MUTED, 400))
    b.append(glass(1430, 36, 204, 34, 17, "orange", glow=0.4, sheen=False, bw=1.4))
    b.append(text(1532, 58, "AgentHack 2026 · Track 1", 13.5, ACCENT["orange"], 700, "middle"))

    # ============ SECTION 1 — ORCHESTRATION ============
    b.append(panel(40, 116, 1600, 560, 16, "orange"))
    b.append(glass(60, 128, 22, 22, 6, "orange", glow=0.5, sheen=False, bw=1.2))
    b.append(text(71, 146, "1", 16, ACCENT["orange"], 800, "middle"))
    b.append(text(94, 146, "ORCHESTRATION — the Maestro Case canvas IS the orchestrator",
                  16.5, TEXT, 700, "start", 0.3))
    b.append(text(1620, 146, "3 nested case levels · 7+4+3 stages · native case-management task",
                  12.5, MUTED, 500, "end"))
    b.append(rail(94, 1610, 160, "orange", 0.32))

    # master pipeline stages
    stages = [
        ("Initial Response", None, "orange"),
        ("Multi-Customer\nInvestigation", "R1 · Day 1", "orange"),
        ("Vector Isolation", "R2 · Day 5", "orange"),
        ("Regulatory Response", "R3 · Day 30", "orange"),
        ("Fiduciary Review", "R4 · Day 45", "orange"),
        ("Litigation Defense", "R5 · Day 90", "orange"),
        ("Closed", None, "green"),
    ]
    sx, sw, sy, sh, gap = 70, 196, 266, 60, 28
    centers = []
    for i, (label, rev, key) in enumerate(stages):
        x = sx + i * (sw + gap)
        cx = x + sw / 2
        centers.append(cx)
        if i > 0:
            ax1 = x - gap
            b.append(arrow(ax1, sy + sh / 2, x, sy + sh / 2, "orange", 2.2, 0.85))
        b.append(glass(x, sy, sw, sh, 11, key, glow=0.4, circuit=True, bw=1.7))
        if rev:
            b.append(pill(cx - 48, 236, 96, 22, rev, "orange", 11.5))
        lines = label.split("\n")
        if len(lines) == 1:
            b.append(text(cx, sy + sh / 2 + 5, lines[0], 14.5, TEXT, 700, "middle"))
        else:
            b.append(text(cx, sy + sh / 2 - 4, lines[0], 13.5, TEXT, 700, "middle"))
            b.append(text(cx, sy + sh / 2 + 13, lines[1], 13.5, TEXT, 700, "middle"))

    # reversal-5 return-to-origin arc
    b.append(conn(f"M {centers[5]},234 C {centers[5]},202 {centers[1]},202 {centers[1]},234",
                  "gold", 2, 0.85, dash="6 4", arrow_end=True))
    b.append(text(centers[3], 196, "Reversal 5 · return-to-origin → re-open the investigation",
                  12, ACCENT["gold"], 600, "middle"))

    # agent chips under stages
    b.append(text(70, 338, 'agents run as type:"agent" tasks inside stages', 11, MUTED, 500))
    chips = [
        (centers[0], 342, "Claim Flow Anomaly Detector", "cyan", False),
        (centers[1], 342, "Multi-Customer Pattern Detector", "cyan", False),
        (centers[2], 342, "Forensic Self-Exam · LangGraph", "cyan", True),
        (centers[2], 372, "Vector Hypothesis Agent", "violet", False),
        (centers[3], 342, "BAA Boundary Reasoner", "violet", False),
        (centers[4], 342, "Fiduciary Conflict Detector", "violet", False),
        (centers[5], 342, "Negligent Monitoring Risk", "violet", False),
    ]
    cw = 196
    droppers_at = {0: "cyan", 1: "cyan", 2: "cyan", 3: "violet", 4: "violet", 5: "violet"}
    for idx, key in droppers_at.items():
        b.append(dropper(centers[idx], sy + sh + 1, 341, key, 0.55))
    for cx, cy, label, key, spark in chips:
        x = cx - cw / 2
        b.append(glass(x, cy, cw, 26, 13, key, glow=0.5, sheen=False, bw=1.4))
        tx = cx - 6 if spark else cx
        b.append(text(tx, cy + 17, label, 11.5, TEXT, 600, "middle"))
        if spark:
            b.append(text(cx + 86, cy + 18, "⚡", 13, ACCENT["gold"], 700, "middle"))
    # HITL gate marker under Fiduciary Conflict Detector
    b.append(pill(centers[4] - 54, 372, 108, 22, "🔒 HITL gate", "gold", 11.5))
    # closed -> completed text
    b.append(text(centers[6], 359, "✓ all instances Completed", 11.5, ACCENT["green"], 700, "middle"))

    # ---- nested case cards ----
    # stakeholder-parent (stacked ×6)
    for off in (12, 6, 0):
        bw = 1.7 if off == 0 else 1.0
        gl = 0.4 if off == 0 else 0.12
        b.append(glass(110 + off, 446 + off, 360, 150, 12, "orange", glow=gl, sheen=(off == 0),
                       circuit=(off == 0), bw=bw))
    b.append(text(126, 470, "clearflow-stakeholder-parent", 12.5, TEXT, 700))
    b.append(pill(418, 456, 42, 19, "× 6", "orange", 12))
    for px, lab in [(126, "Onboard"), (210, "Impact\nAssess"), (294, "Obligation\nDeterm."),
                    (378, "Resolved")]:
        b.append(glass(px, 482, 76, 36, 7, "orange", glow=0.28, sheen=False, bw=1.1))
        ls = lab.split("\n")
        ccx = px + 38
        if len(ls) == 1:
            b.append(text(ccx, 504, ls[0], 9.5, TEXT, 700, "middle"))
        else:
            b.append(text(ccx, 499, ls[0], 9, TEXT, 700, "middle"))
            b.append(text(ccx, 510, ls[1], 9, TEXT, 700, "middle"))
    b.append(glass(118, 542, 168, 26, 13, "violet", glow=0.45, sheen=False, bw=1.3))
    b.append(text(202, 559, "Assess Claim Disruption", 11.5, TEXT, 600, "middle"))
    b.append(glass(294, 542, 168, 26, 13, "violet", glow=0.45, sheen=False, bw=1.3))
    b.append(text(378, 559, "BAA Boundary Reasoner", 11.5, TEXT, 600, "middle"))
    b.append(text(290, 585, "per-provider liquidity + lawful BAA disclosure (Context Grounding)",
                  10.5, MUTED, 500, "middle"))

    # obligation-grandchild (stacked ×6)
    for off in (12, 6, 0):
        bw = 1.7 if off == 0 else 1.0
        gl = 0.4 if off == 0 else 0.12
        b.append(glass(590 + off, 464 + off, 300, 132, 12, "orange", glow=gl, sheen=(off == 0),
                       circuit=(off == 0), bw=bw))
    b.append(text(606, 488, "clearflow-obligation-grandchild", 12, TEXT, 700))
    b.append(pill(838, 474, 42, 19, "× 6", "orange", 12))
    for px, lab in [(606, "Intake"), (698, "Response"), (790, "Discharged")]:
        b.append(glass(px, 500, 84, 34, 7, "orange", glow=0.28, sheen=False, bw=1.1))
        b.append(text(px + 42, 521, lab, 10, TEXT, 700, "middle"))
    b.append(glass(606, 556, 128, 26, 13, "violet", glow=0.45, sheen=False, bw=1.3))
    b.append(text(670, 573, "Classify Obligation", 11.5, TEXT, 600, "middle"))
    b.append(pill(758, 556, 120, 26, "🔒 file / withdraw", "gold", 11))

    # reversal-3 fan-out connectors (master -> 6 parents)
    for tx in (140, 200, 260, 320, 380, 440):
        b.append(conn(f"M 840,402 C 840,432 {tx},418 {tx},444", "orange", 1.5, 0.5))
    b.append(text(290, 434, "Reversal 3 · Day 30 — master spawns 6 parents", 12,
                  ACCENT["orange"], 700, "middle"))
    b.append(arrow(482, 530, 588, 530, "orange", 2, 0.85))
    b.append(text(530, 522, "each spawns", 10, MUTED, 500, "middle"))
    b.append(text(530, 546, "1 grandchild", 10, MUTED, 500, "middle"))

    # 13 instances callout
    b.append(glass(920, 494, 188, 76, 12, "orange", glow=0.5, circuit=True, bw=1.6))
    b.append(text(1014, 522, "13 live case instances", 13, ACCENT["orange"], 800, "middle"))
    b.append(text(1014, 544, "3 levels of native", 11.5, TEXT, 500, "middle"))
    b.append(text(1014, 560, "Maestro Case nesting", 11.5, TEXT, 500, "middle"))

    # ---- Trust Layer bar ----
    b.append(f'<rect x="64" y="630" width="1552" height="32" rx="10" fill="{ACCENT["amber"]}" '
             f'opacity="0.22" filter="url(#glow)"/>')
    b.append('<rect x="64" y="630" width="1552" height="32" rx="10" fill="url(#glass_trust)" '
             f'stroke="{ACCENT["amber"]}" stroke-width="1.5"/>')
    b.append('<rect x="65.2" y="631.2" width="1549.6" height="15" rx="9" fill="url(#sheen)"/>')
    b.append(text(840, 651, "🛡  UiPath LLM Gateway + Trust Layer  —  PHI / PII guardrails on "
                            "every LLM call  ·  BYO Claude Sonnet 4.6  +  advisory OpenAI",
                  13, ACCENT["amber"], 700, "middle"))

    # ============ SECTION 2 — DATA, INTEGRATION & SURFACES ============
    b.append(panel(40, 692, 1600, 286, 16, "green"))
    b.append(glass(60, 704, 22, 22, 6, "green", glow=0.5, sheen=False, bw=1.2))
    b.append(text(71, 722, "2", 16, ACCENT["green"], 800, "middle"))
    b.append(text(94, 722, "DATA, INTEGRATION & SURFACES", 16.5, TEXT, 700, "start", 0.3))
    b.append(text(1620, 722, "13 UiPath product surfaces · 37 runtime artifacts",
                  12.5, MUTED, 500, "end"))
    b.append(rail(94, 1610, 736, "green", 0.3))

    rowa = [
        (70, "Data Fabric", ["9 entities · 4,320 telemetry rows", "structured source-of-truth seed"], "green"),
        (590, "Context Grounding", ["2 indexes · BAA-corpus (live)", "→ grounds BAA Boundary Reasoner"], "cyan"),
        (1110, "Integration Service", ["19 API Workflows (CNCF)", "external-party mocks + 3 ViVE bridges"], "violet"),
    ]
    for x, title, subs, key in rowa:
        b.append(glass(x, 744, 500, 92, 11, key, glow=0.32, circuit=True, bw=1.4))
        b.append(text(x + 22, 772, title, 13.5, TEXT, 700))
        for j, sub in enumerate(subs):
            b.append(text(x + 22, 792 + j * 16, sub, 11, MUTED, 500))

    rowb = [
        (70, "Maestro BPMN × 2", "ideal-response + closure", "orange"),
        (459, "Maestro Flow", "demo driver", "orange"),
        (848, "Action Center", "2 HITL gate apps", "gold"),
        (1237, "Coded Web App", "React + Vite dashboard", "cyan"),
    ]
    for x, title, sub, key in rowb:
        b.append(glass(x, 848, 373, 66, 11, key, glow=0.3, bw=1.3))
        b.append(text(x + 22, 874, title, 13.5, TEXT, 700))
        b.append(text(x + 22, 894, sub, 11, MUTED, 500))

    # ---- vertical bridge ----
    b.append(f'<rect x="40" y="992" width="1600" height="40" rx="12" fill="{ACCENT["cyan"]}" '
             f'opacity="0.16" filter="url(#glow)"/>')
    b.append('<rect x="40" y="992" width="1600" height="40" rx="12" fill="url(#glass_cyan)" '
             f'stroke="{ACCENT["cyan"]}" stroke-width="1.4"/>')
    b.append('<rect x="41.4" y="993.4" width="1597.2" height="19" rx="11" fill="url(#sheen)"/>')
    b.append(text(64, 1017, "↑ Vertical bridge", 13.5, ACCENT["cyan"], 800))
    b.append(text(890, 1017, "each stakeholder parent case invokes UiPath ViVE-2026 Healthcare "
                             "solutions:  Medical Records Summarization · Claim Denial Prevention "
                             "· Prior Authorization", 12.5, TEXT, 500, "middle"))

    # ---- footer: Claude Code + legend ----
    b.append(glass(40, 1046, 560, 64, 12, "violet", glow=0.34, circuit=True, bw=1.4))
    b.append(text(62, 1073, "Built end-to-end with Claude Code", 14, "#D9CCFF", 800))
    b.append(text(62, 1094, "37 UiPath artifacts · 683 offline tests (TDD) · IP-safe fictional cast",
                  11.5, MUTED, 500))

    b.append(glass(628, 1046, 1012, 64, 12, "neutral", glow=0.18, bw=1.2))
    legend = [
        (648, "orange", "Maestro Case stage"),
        (792.8, "violet", "Agent Builder · Claude Sonnet 4.6"),
        (1036.6, "cyan", "Coded Agent · Python SDK"),
        (1221, "green", "Platform service"),
        (1352.6, "gold", "Human gate"),
    ]
    for x, key, lab in legend:
        a = ACCENT[key]
        b.append(f'<rect x="{x}" y="1064" width="16" height="16" rx="4" fill="{a}" '
                 f'opacity="0.4" filter="url(#glowS)"/>')
        b.append(f'<rect x="{x}" y="1064" width="16" height="16" rx="4" fill="url(#glass_{key})" '
                 f'stroke="{a}" stroke-width="1.3"/>')
        b.append(text(x + 22, 1077, lab, 11, TEXT, 600))
    b.append(text(648, 1098, "Maestro Case V20 · case-management task · LangGraph "
                             "(uipath-langchain) · LLM Gateway + Trust Layer · Context Grounding "
                             "· Data Fabric", 10.5, MUTED, 500))
    return "".join(b)


def build_svg() -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">'
        + build_defs() + build_body() + "</svg>"
    )


def main() -> None:
    _OUT.write_text(build_svg(), encoding="utf-8")
    print(f"wrote {_OUT} ({_OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

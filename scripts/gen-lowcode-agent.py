#!/usr/bin/env python3
"""Generate the full UiPath low-code Agent Builder file set for the 2 grandchild-walk
agents (assess-claim-disruption, classify-obligation), mirroring the existing
vector-hypothesis-agent structure. Prompts are loaded from agents/prompts/*.md
(never inlined). Run from repo root: python3 scripts/gen-lowcode-agent.py
"""
import json, os, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS = os.path.join(REPO, "agents")
PROMPTS = os.path.join(AGENTS, "prompts")

SETTINGS = {"model": "anthropic.claude-sonnet-4-6", "maxTokens": 16384, "temperature": 0,
            "engine": "basic-v2", "maxIterations": 25, "mode": "standard"}
METADATA = {"storageVersion": "50.0.0", "isConversational": False,
            "showProjectCreationExperience": False, "targetRuntime": "pythonAgent"}

SPECS = [
    {
        "dir": "assess-claim-disruption", "name": "AssessClaimDisruptionAgent",
        "agent_id": "c0ffee01-1111-4a11-8a11-000000000a11",
        "entry_uid": "c0ffee01-2222-4a22-8a22-000000000a22",
        "prompt": "assess_claim_disruption_agent.md",
        "inputs": [
            ("stakeholder_id", "string", "Affected provider slug or id (northstar | alpha | beta | gamma | delta | epsilon).", "northstar"),
            ("claim_telemetry_summary", "string", "Summary of the provider's claim telemetry: baseline vs observed claim volume and the disruption pattern.",
             "Observed claim volume for this provider dropped from a 30-day baseline of ~1,000 daily claims to ~200 daily claims over a sustained 6-day window, an ~80% drop with no recovery trend, concentrated in electronic remittance and eligibility flows."),
            ("business_continuity_runway_days", "integer", "Days the provider can sustain the disruption before liquidity stress.", 12),
        ],
        "outputs": [
            ("disruption_score", {"type": "number", "description": "Severity of the claim-flow disruption, 0.0 to 1.0.", "minimum": 0, "maximum": 1}),
            ("impact_tier", {"type": "string", "description": "Disruption tier.", "enum": ["none", "moderate", "elevated", "critical"]}),
            ("liquidity_assessment", {"type": "string", "description": "Liquidity / payment-continuity pressure given the runway."}),
            ("rationale", {"type": "string", "description": "Decision-support explanation of the assessment."}),
        ],
    },
    {
        "dir": "classify-obligation", "name": "ClassifyObligationAgent",
        "agent_id": "c0ffee02-1111-4b11-8b11-000000000b11",
        "entry_uid": "c0ffee02-2222-4b22-8b22-000000000b22",
        "prompt": "classify_obligation_agent.md",
        "inputs": [
            ("obligation_type", "string", "The raised obligation, e.g. subpoena-response | breach-notification | baa-disclosure | audit-cooperation.", "subpoena-response"),
            ("jurisdiction", "string", "The obligation's jurisdiction, e.g. TN-DOI | federal | contractual.", "TN-DOI"),
            ("baa_reference", "string", "The originating Business Associate Agreement reference.", "BAA-NORTHSTAR"),
        ],
        "outputs": [
            ("obligation_class", {"type": "string", "description": "The classified obligation kind."}),
            ("severity", {"type": "string", "description": "Obligation severity.", "enum": ["low", "medium", "high"]}),
            ("required_response", {"type": "string", "description": "Response posture the reviewer should prepare."}),
            ("rationale", {"type": "string", "description": "Decision-support explanation of the classification."}),
        ],
    },
]


def input_schema(inputs):
    props = {}
    for name, typ, desc, default in inputs:
        props[name] = {"type": typ, "description": desc, "default": default}
    return {"type": "object", "properties": props, "required": []}


def output_schema(outputs):
    return {"type": "object", "properties": {n: s for n, s in outputs}}


def entry_input(inputs):
    props = {}
    for name, typ, desc, _ in inputs:
        props[name] = {"type": typ, "description": desc}
    return {"type": "object", "properties": props, "required": []}


def user_message(inputs):
    parts, tokens = [], []
    for i, (name, _t, _d, _df) in enumerate(inputs):
        label = name.replace("_", " ").title()
        prefix = ("" if i == 0 else "\n\n") + f"{label}:\n"
        parts.append(prefix + "{{input." + name + "}}")
        tokens.append({"type": "simpleText", "rawString": prefix})
        tokens.append({"type": "variable", "rawString": "input." + name})
    return "".join(parts), tokens


def build(spec):
    d = os.path.join(AGENTS, spec["dir"])
    system_prompt = open(os.path.join(PROMPTS, spec["prompt"]), encoding="utf-8").read().strip()
    in_schema = input_schema(spec["inputs"])
    out_schema = output_schema(spec["outputs"])
    umsg, utokens = user_message(spec["inputs"])
    messages = [
        {"role": "system", "content": system_prompt,
         "contentTokens": [{"type": "simpleText", "rawString": system_prompt}]},
        {"role": "user", "content": umsg, "contentTokens": utokens},
    ]
    # remove any prior coded-agent files
    for f in ("agent.py", "uipath.json", "pyproject.toml", "uv.lock", "AGENTS.md", "CLAUDE.md", "main.mermaid"):
        p = os.path.join(d, f)
        if os.path.exists(p):
            os.remove(p)
    for sub in (".uipath", ".agent", "evaluations", "__pycache__", ".venv"):
        p = os.path.join(d, sub)
        if os.path.isdir(p):
            shutil.rmtree(p)

    agent_json = {"version": "1.1.0", "settings": SETTINGS, "inputSchema": in_schema,
                  "outputSchema": out_schema, "metadata": METADATA, "type": "lowCode", "messages": messages}
    _w(os.path.join(d, "agent.json"), agent_json)

    entry = {"$schema": "https://cloud.uipath.com/draft/2024-12/entry-point", "$id": "entry-points.json",
             "entryPoints": [{"filePath": "/content/agent.json", "uniqueId": spec["entry_uid"], "type": "agent",
                              "input": entry_input(spec["inputs"]), "output": out_schema}]}
    _w(os.path.join(d, "entry-points.json"), entry)
    _w(os.path.join(d, "flow-layout.json"), {})
    _w(os.path.join(d, "project.uiproj"), {"ProjectType": "Agent", "Name": spec["name"], "Description": None, "MainFile": None})

    ab = os.path.join(d, ".agent-builder")
    os.makedirs(ab, exist_ok=True)
    ab_agent = {"id": spec["agent_id"], "version": "1.1.0", "name": spec["name"], "metadata": METADATA,
                "messages": messages, "settings": SETTINGS, "inputSchema": in_schema, "outputSchema": out_schema, "type": "lowCode"}
    _w(os.path.join(ab, "agent.json"), ab_agent)
    _w(os.path.join(ab, "bindings.json"), {"version": "2.0", "resources": []})
    _w(os.path.join(ab, "entry-points.json"), entry)
    print(f"built low-code agent: {spec['dir']} ({spec['name']})")


def _w(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    for spec in SPECS:
        build(spec)
    print("done")

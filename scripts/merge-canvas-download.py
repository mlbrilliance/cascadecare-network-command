#!/usr/bin/env python3
"""Re-apply CascadeCare master-case fixes onto a fresh Studio Web canvas download.

Canvas regeneration of clearflow-master-crisis reliably drops/changes 5 things that
this script restores deterministically, so a canvas round-trip (e.g. to add/modify a
task) doesn't regress the working deploy:

  1. mainline start event  -> case never auto-walks (commit 400caf6)
  2. HITL action->app binding (tvlKcFYnW name/folderPath + 2 app bindings) -> 170015
  3. entry-points.json (canvas emits empty) -> restored from canonical
  4. canvas auto-adds dup 'error' outputs on the 6 spawn tasks -> V20 dup-var error
  5. provider-identity spawn inputs (StakeholderId/MasterCaseId on the 6 spawns) ->
     children spawn without provider identity (lost in the v1.0.14 canvas regen).
     StakeholderId is the LITERAL provider slug: the `=datafabric.qem:Provider[...]`
     expression fails runtime evaluation (incident 400300 "Syntax error at index 4",
     proven live 2026-06-10 on 1.0.21) — qem: refs are not valid in JobArguments.

It writes the merged master case into BOTH the canonical standalone dir and the
canonical solution copy, and copies the Slack Connection resource into the solution.

Usage:
  python3 scripts/merge-canvas-download.py <extracted-download-dir>
    e.g. /tmp/dl/<solutionId>  (output of `uip solution download <id> --extract`)
"""
import json, re, sys, os, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(REPO, "maestro_case/clearflow-master-crisis")
SOL = os.path.join(REPO, "maestro_case/clearflow-solution")
SOL_MC = os.path.join(SOL, "clearflow-master-crisis")

APP_BINDINGS = [
    {"id": "bCCAppNm1", "name": "name", "type": "string", "resource": "app",
     "resourceKey": "Shared/CascadeCare-v110.CascadeCare", "default": "CascadeCare",
     "propertyAttribute": "name"},
    {"id": "bCCAppFp2", "name": "folderPath", "type": "string", "resource": "app",
     "resourceKey": "Shared/CascadeCare-v110.CascadeCare", "default": "Shared/CascadeCare-v110",
     "propertyAttribute": "folderPath"},
]
APP_BINDING_XML = (
    '        <uipath:binding id="bCCAppNm1" name="name" type="string" default="CascadeCare" resource="app" resourceKey="Shared/CascadeCare-v110.CascadeCare" propertyAttribute="name" />\n'
    '        <uipath:binding id="bCCAppFp2" name="folderPath" type="string" default="Shared/CascadeCare-v110" resource="app" resourceKey="Shared/CascadeCare-v110.CascadeCare" propertyAttribute="folderPath" />\n'
    '      </uipath:bindings>')
START_EVENT_XML = (
    '<bpmn:startEvent id="33a46298-878c-4076-ace9-7dcd36c4635d">\n'
    '      <bpmn:extensionElements>\n'
    '        <uipath:entryPointId value="490e6462-8455-4b32-89e9-48117a504326" />\n'
    '        <uipath:activity version="v1" caseManagement="[object Object]">\n'
    '          <uipath:type value="uipath:EntryPointId" version="v1" />\n'
    '        </uipath:activity>\n'
    '      </bpmn:extensionElements>\n'
    '      <bpmn:outgoing>edge_33a46298-878c-4076-ace9-7dcd36c4635d-CaseInitialVariablesSetupNode</bpmn:outgoing>\n'
    '      <bpmn:messageEventDefinition />\n'
    '    </bpmn:startEvent>\n'
    '    <bpmn:sequenceFlow id="edge_33a46298-878c-4076-ace9-7dcd36c4635d-CaseInitialVariablesSetupNode" sourceRef="33a46298-878c-4076-ace9-7dcd36c4635d" targetRef="CaseInitialVariablesSetupNode" />\n'
    '    <bpmn:task id="CaseInitialVariablesSetupNode"')
SPAWN_ERROR_ELEM = '<uipath:output name="Error" type="jsonSchema" source="=Error" var="error" />'
# Reversal-3 fan: spawn task id -> Provider entity slug (drives the qem: input restore)
SPAWN_SLUGS = {
    "tFONj34ck": "northstar", "tP26wJSn9": "alpha", "tP1qlCyT5": "beta",
    "tXX9Tu80x": "gamma", "tf3qEuV5z": "delta", "tz8z6TUHT": "epsilon",
}
SPAWN_IDS = set(SPAWN_SLUGS)
SPAWN_INPUT_SCHEMA_XML = (
    '<uipath:inputSchema type="jsonSchema"><![CDATA[{"$schema":"http://json-schema.org/draft-07/schema#",'
    '"type":"object","properties":{"StakeholderId":{"type":"string"},"MasterCaseId":{"type":"string"}},'
    '"required":[]}]]></uipath:inputSchema>')
# S025 (ADR-0002): OOTB Case App surface. caseAppEnabled:true requires a caseAppConfig
# (V20 / skills PR #216: absent config breaks the Case App UI). Restored if the canvas
# strips it; a canvas-authored config wins (setdefault).
CASE_APP_CONFIG = {
    "caseSummary": ('=string.Format("Day {0} - Reversal {1}: {2}", vars.var_simulated_day, '
                    'vars.var_reversal_number, vars.var_case_goal)'),
    "sections": [
        {"id": "section-d3b08386-8e82-4bf8-8cb9-e8c05c6f1d06", "title": "Crisis posture",
         "details": '{"Current goal":"=vars.var_case_goal",'
                    '"Vector status":"=vars.var_clearflow_vector_status"}'},
        {"id": "section-0d16dc48-ab71-49bb-8aa2-297651845e86", "title": "Cascade state",
         "details": '{"Reversal":"=vars.var_reversal_number",'
                    '"Simulated day":"=vars.var_simulated_day",'
                    '"Grandchild cases":"=vars.var_grandchild_case_count"}'},
    ],
}


def ensure_case_app_config(d):
    if d["metadata"].get("caseAppEnabled"):
        d["metadata"].setdefault("caseAppConfig", CASE_APP_CONFIG)


def spawn_inputs(slug):
    return [
        {"id": f"inp_sid_{slug}", "name": "StakeholderId", "type": "string",
         "value": slug},
        {"id": f"inp_mid_{slug}", "name": "MasterCaseId", "type": "string",
         "value": "=metadata.caseId"},
    ]


def spawn_job_arguments_xml(slug):
    return ('<uipath:input name="JobArguments" type="json" target="bodyField"><![CDATA[{'
            f'"StakeholderId":"{slug}",'
            '"MasterCaseId":"=metadata.caseId"}]]></uipath:input>')


def patch_caseplan(path):
    d = json.load(open(path))
    ensure_case_app_config(d)
    ids = {b["id"] for b in d["bindings"]}
    for b in APP_BINDINGS:
        if b["id"] not in ids:
            d["bindings"].append(b)
    hit = False
    for n in d["nodes"]:
        if n.get("id") == "Stage_LKuLeU":
            for lane in n["data"]["tasks"]:
                for t in lane:
                    if t["id"] == "tvlKcFYnW":
                        t["data"]["name"] = "=bindings.bCCAppNm1"
                        t["data"]["folderPath"] = "=bindings.bCCAppFp2"
                        hit = True
        if n.get("id") == "Stage_JM1SVs":
            for lane in n["data"]["tasks"]:
                for t in lane:
                    if t["id"] in SPAWN_IDS:
                        if t["data"].get("outputs"):
                            t["data"]["outputs"] = []
                        t["data"]["inputs"] = spawn_inputs(SPAWN_SLUGS[t["id"]])
    assert hit, "tvlKcFYnW not found in caseplan"
    json.dump(d, open(path, "w"), separators=(",", ":"))


def patch_bpmn(path):
    s = open(path).read()
    assert s.count("</uipath:bindings>") == 1
    if "bCCAppNm1" not in s:
        s = s.replace("      </uipath:bindings>", APP_BINDING_XML, 1)
    s = s.replace('<uipath:input name="name" type="string" value="=bindings." />',
                  '<uipath:input name="name" type="string" value="=bindings.bCCAppNm1" />', 1)
    s = s.replace('<uipath:input name="folderPath" type="string" value="=bindings." />',
                  '<uipath:input name="folderPath" type="string" value="=bindings.bCCAppFp2" />', 1)
    if '<bpmn:startEvent id="33a46298-878c-4076-ace9-7dcd36c4635d"' not in s:
        assert s.count('<bpmn:task id="CaseInitialVariablesSetupNode"') == 1
        s = s.replace('<bpmn:task id="CaseInitialVariablesSetupNode"', START_EVENT_XML, 1)
        anchor = ('</bpmn:extensionElements>\n      <bpmn:outgoing>'
                  'edge_CaseInitialVariablesSetupNode-CaseGlobalsVariablesSetupNode</bpmn:outgoing>')
        assert s.count(anchor) == 1
        s = s.replace(anchor,
                      '</bpmn:extensionElements>\n      <bpmn:incoming>edge_33a46298-878c-4076-ace9-7dcd36c4635d-CaseInitialVariablesSetupNode</bpmn:incoming>\n      <bpmn:outgoing>edge_CaseInitialVariablesSetupNode-CaseGlobalsVariablesSetupNode</bpmn:outgoing>', 1)
    s = re.sub(r'[ \t]*' + re.escape(SPAWN_ERROR_ELEM) + r'\n', '', s)
    s = s.replace(SPAWN_ERROR_ELEM, '')
    s = patch_spawn_inputs(s)
    open(path, "w").write(s)


def patch_spawn_inputs(s):
    """Restore qem: StakeholderId/MasterCaseId inputs on the 6 spawn callActivities
    (executable nodes only — the embedded CDATA caseplan copy is runtime-inert)."""
    for tid, slug in SPAWN_SLUGS.items():
        start = s.find(f'<bpmn:callActivity id="{tid}"')
        assert start != -1, f"callActivity {tid} not found in bpmn"
        end = s.find("</bpmn:callActivity>", start)
        block = s[start:end]
        if "JobArguments" in block:
            continue
        assert block.count("</uipath:context>") == 1, f"unexpected context shape in {tid}"
        block = block.replace(
            "            </uipath:context>",
            f"              {SPAWN_INPUT_SCHEMA_XML}\n"
            "            </uipath:context>\n"
            f"            {spawn_job_arguments_xml(slug)}", 1)
        s = s[:start] + block + s[end:]
    return s


def main():
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    dl = sys.argv[1]
    dl_mc = os.path.join(dl, "clearflow-master-crisis")
    assert os.path.isdir(dl_mc), f"no clearflow-master-crisis in {dl}"
    # restore entry-points from canonical onto the download, then patch
    shutil.copy(os.path.join(CANON, "entry-points.json"), os.path.join(dl_mc, "entry-points.json"))
    patch_caseplan(os.path.join(dl_mc, "caseplan.json"))
    patch_bpmn(os.path.join(dl_mc, "caseplan.json.bpmn"))
    # propagate merged master case into canonical standalone + solution copy
    for dst in (CANON, SOL_MC):
        for f in ("caseplan.json", "caseplan.json.bpmn", "entry-points.json"):
            shutil.copy(os.path.join(dl_mc, f), os.path.join(dst, f))
    # copy Slack connection resource into the solution (download has it; canonical may not)
    src_conn = os.path.join(dl, "resources/solution_folder/connection")
    if os.path.isdir(src_conn):
        dst_conn = os.path.join(SOL, "resources/solution_folder/connection")
        os.makedirs(dst_conn, exist_ok=True)
        for root, _, files in os.walk(src_conn):
            rel = os.path.relpath(root, src_conn)
            os.makedirs(os.path.join(dst_conn, rel), exist_ok=True)
            for fn in files:
                shutil.copy(os.path.join(root, fn), os.path.join(dst_conn, rel, fn))
    print("merge complete -> canonical + solution updated; entry-points/start-event/HITL/dup-error fixed; connection copied")


if __name__ == "__main__":
    main()

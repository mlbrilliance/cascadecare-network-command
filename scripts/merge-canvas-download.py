#!/usr/bin/env python3
"""Re-apply CascadeCare master-case fixes onto a fresh Studio Web canvas download.

Canvas regeneration of clearflow-master-crisis reliably drops/changes 4 things that
this script restores deterministically, so a canvas round-trip (e.g. to add/modify a
task) doesn't regress the working deploy:

  1. mainline start event  -> case never auto-walks (commit 400caf6)
  2. HITL action->app binding (tvlKcFYnW name/folderPath + 2 app bindings) -> 170015
  3. entry-points.json (canvas emits empty) -> restored from canonical
  4. canvas auto-adds dup 'error' outputs on the 6 spawn tasks -> V20 dup-var error

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
SPAWN_IDS = {"tFONj34ck", "tP26wJSn9", "tP1qlCyT5", "tXX9Tu80x", "tf3qEuV5z", "tz8z6TUHT"}


def patch_caseplan(path):
    d = json.load(open(path))
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
                    if t["id"] in SPAWN_IDS and t["data"].get("outputs"):
                        t["data"]["outputs"] = []
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
    open(path, "w").write(s)


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

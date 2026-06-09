#!/usr/bin/env python3
"""Apply the child + grandchild case fixes onto a fresh Studio Web canvas download,
preserving the canvas-authored task bindings (assess/classify/register/audit/ViVE)
and writing the merged cases into the canonical standalone dirs (pack-solution.sh
then copies them into the solution).

Two deterministic fixes the canvas does NOT produce:

  CHILD (clearflow-stakeholder-parent)
    - mainline start event is MISSING (CaseInitialVariablesSetupNode orphaned, empty
      entry-points.json) -> child spawns but sits Running forever. Inject the
      message start event for trigger 468d60f1 (mirrors master commit 400caf6) +
      populate entry-points.json. entryPointId == entry-points uniqueId (master
      pattern; the master spawns the child BY NAME, so the uuid is free to choose).

  GRANDCHILD (clearflow-obligation-grandchild)
    - the "Prepare & File Obligation Response" Human-action (t9BUmAX8k) could NOT be
      bound to its Action Center app in the canvas ("Adding resource to solution
      failed #100"), so it ships with empty value="=bindings." -> would fault 170015.
      Hand-wire it to app "Regulatory/Contractual Obligation Response" in
      Shared/CascadeCare-v110, identical to the master gate tvlKcFYnW -> CascadeCare.
    - the mainline start event is already intact (canvas-generated) -> no patch.

Usage:
  python3 scripts/merge-child-grandchild.py <extracted-download-dir>
    e.g. /tmp/dl/<solutionId>
"""
import json, re, sys, os, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHILD_CANON = os.path.join(REPO, "maestro_case/clearflow-stakeholder-parent")
GC_CANON = os.path.join(REPO, "maestro_case/clearflow-obligation-grandchild")

# --- child mainline start event -------------------------------------------------
CHILD_TRIGGER_ID = "468d60f1-0562-4be9-ae1e-2e05e0ac3ac3"
CHILD_ENTRY_UID = "916f0a1c-df8b-4c8a-b6d2-e3e48bb4b2ee"
CHILD_START_XML = (
    f'<bpmn:startEvent id="{CHILD_TRIGGER_ID}">\n'
    '      <bpmn:extensionElements>\n'
    f'        <uipath:entryPointId value="{CHILD_ENTRY_UID}" />\n'
    '        <uipath:activity version="v1" caseManagement="[object Object]">\n'
    '          <uipath:type value="uipath:EntryPointId" version="v1" />\n'
    '        </uipath:activity>\n'
    '      </bpmn:extensionElements>\n'
    f'      <bpmn:outgoing>edge_{CHILD_TRIGGER_ID}-CaseInitialVariablesSetupNode</bpmn:outgoing>\n'
    '      <bpmn:messageEventDefinition />\n'
    '    </bpmn:startEvent>\n'
    f'    <bpmn:sequenceFlow id="edge_{CHILD_TRIGGER_ID}-CaseInitialVariablesSetupNode" '
    f'sourceRef="{CHILD_TRIGGER_ID}" targetRef="CaseInitialVariablesSetupNode" />\n'
    '    <bpmn:task id="CaseInitialVariablesSetupNode"')
CHILD_INCOMING_ANCHOR = (
    '</bpmn:extensionElements>\n      '
    '<bpmn:outgoing>edge_CaseInitialVariablesSetupNode-CaseGlobalsVariablesSetupNode</bpmn:outgoing>')
CHILD_INCOMING_REPL = (
    '</bpmn:extensionElements>\n      '
    f'<bpmn:incoming>edge_{CHILD_TRIGGER_ID}-CaseInitialVariablesSetupNode</bpmn:incoming>\n      '
    '<bpmn:outgoing>edge_CaseInitialVariablesSetupNode-CaseGlobalsVariablesSetupNode</bpmn:outgoing>')
# tasks the canvas left isRequired=false that MUST fire before their stage exits
# (stage exit = required-tasks-completed). Without this the grandchild never spawns
# and the ViVE vertical-bridge tasks are skipped. Mirrors the master 6-spawn fix
# (canvas toggle wrote isRequired:true into the embedded case-definition JSON, which
# the CaseRulesEvaluator reads — there is no executable required-set gateway).
CHILD_REQUIRED_TASKS = ["tfmtATbvb", "tMRS001", "tCDP001", "tPAC001"]
# The grandchild-spawn (tfmtATbvb) entry was "after BAA boundary analysis"
# (selected-tasks-completed[ta1Ou8jah]). Live-proven that this races with the stage's
# required-tasks-completed exit (BAA completes -> stage exits before the spawn activates,
# even though both are Required -- identical defn to the master's working spawns, yet the
# child's single after-BAA spawn loses the race). Re-point it to current-stage-entered so it
# activates in parallel with BAA (no data dependency -- the grandchild takes no BAA output).
SPAWN_ENTRY_OLD = '"rule":"selected-tasks-completed","id":"Rule_MWQvdm","selectedTasksIds":["ta1Ou8jah"]'
SPAWN_ENTRY_NEW = '"rule":"current-stage-entered","id":"Rule_MWQvdm"'
CHILD_ENTRY_POINTS = {
    "$schema": "https://cloud.uipath.com/draft/2024-12/entry-point",
    "$id": "entry-points.json",
    "entryPoints": [{
        "filePath": f"/content/caseplan.json.bpmn#{CHILD_TRIGGER_ID}",
        "uniqueId": CHILD_ENTRY_UID,
        "type": "CaseManagement",
        "input": {"type": "object", "properties": {}},
        "output": {"type": "object", "properties": {}},
        "displayName": "Trigger 1",
    }],
}

# --- grandchild Human-action app wiring -----------------------------------------
GC_TASK_ID = "t9BUmAX8k"
GC_APP_NAME = "Regulatory/Contractual Obligation Response"
GC_APP_FOLDER = "Shared/CascadeCare-v110"
GC_APP_KEY = f"{GC_APP_FOLDER}.{GC_APP_NAME}"
GC_APP_BINDINGS = [
    {"id": "bGCAppNm1", "name": "name", "type": "string", "resource": "app",
     "resourceKey": GC_APP_KEY, "default": GC_APP_NAME, "propertyAttribute": "name"},
    {"id": "bGCAppFp2", "name": "folderPath", "type": "string", "resource": "app",
     "resourceKey": GC_APP_KEY, "default": GC_APP_FOLDER, "propertyAttribute": "folderPath"},
]
GC_APP_BINDING_XML = (
    f'        <uipath:binding id="bGCAppNm1" name="name" type="string" default="{GC_APP_NAME}" resource="app" resourceKey="{GC_APP_KEY}" propertyAttribute="name" />\n'
    f'        <uipath:binding id="bGCAppFp2" name="folderPath" type="string" default="{GC_APP_FOLDER}" resource="app" resourceKey="{GC_APP_KEY}" propertyAttribute="folderPath" />\n'
    '      </uipath:bindings>')
# action-task outputs (mirror master tvlKcFYnW; describe-verified app output schema)
GC_OUTPUTS = [
    ("ReviewerId", "reviewerId"),
    ("ResponseDisposition", "responseDisposition"),
    ("ResponseNarrative", "responseNarrative"),
    ("FiledTimestamp", "filedTimestamp"),
]
GC_OUTPUT_XML = "".join(
    f'            <uipath:output name="{n}" type="string" source="={n}" var="{v}" target="={v}" />\n'
    for n, v in GC_OUTPUTS)


def _flip_required(s, tid):
    """Ensure the embedded-JSON isRequired of leaf task <tid> is true (idempotent).
    No-op if the canvas already saved it as true."""
    i = s.find('{"id":"' + tid + '"')
    assert i >= 0, f"{tid} not in embedded JSON"
    j_false = s.find('"isRequired":false', i)
    j_true = s.find('"isRequired":true', i)
    already = j_true >= 0 and (j_false < 0 or j_true < j_false) and (j_true - i) < 2000
    if already:
        return s  # canvas already saved Required=true
    assert j_false >= 0 and (j_false - i) < 2000, f"{tid} isRequired not found near task"
    return s[:j_false] + '"isRequired":true' + s[j_false + len('"isRequired":false'):]


def patch_child_bpmn(path):
    s = open(path).read()
    if f'<bpmn:startEvent id="{CHILD_TRIGGER_ID}"' not in s:
        assert s.count('<bpmn:task id="CaseInitialVariablesSetupNode"') == 1
        s = s.replace('<bpmn:task id="CaseInitialVariablesSetupNode"', CHILD_START_XML, 1)
        assert s.count(CHILD_INCOMING_ANCHOR) == 1
        s = s.replace(CHILD_INCOMING_ANCHOR, CHILD_INCOMING_REPL, 1)
    for tid in CHILD_REQUIRED_TASKS:
        s = _flip_required(s, tid)
    s = s.replace(SPAWN_ENTRY_OLD, SPAWN_ENTRY_NEW)
    s = s.replace('"displayName":"After BAA boundary analysis"', '"displayName":"Stage entered"')
    open(path, "w").write(s)


def patch_child_caseplan(path):
    d = json.load(open(path))
    flipped = set()
    for n in d["nodes"]:
        for lane in (n.get("data", {}).get("tasks") or []):
            for t in lane:
                if t.get("id") in CHILD_REQUIRED_TASKS:
                    t["isRequired"] = True
                    flipped.add(t["id"])
                if t.get("id") == "tfmtATbvb":
                    for ec in t.get("entryConditions", []):
                        for rules in ec.get("rules", []):
                            for r in rules:
                                if r.get("rule") == "selected-tasks-completed":
                                    r.clear()
                                    r["rule"] = "current-stage-entered"
                                    r["id"] = "Rule_MWQvdm"
                        if ec.get("displayName") == "After BAA boundary analysis":
                            ec["displayName"] = "Stage entered"
    assert flipped == set(CHILD_REQUIRED_TASKS), f"missing tasks: {set(CHILD_REQUIRED_TASKS)-flipped}"
    json.dump(d, open(path, "w"), separators=(",", ":"))


def patch_gc_caseplan(path):
    d = json.load(open(path))
    ids = {b["id"] for b in d["bindings"]}
    for b in GC_APP_BINDINGS:
        if b["id"] not in ids:
            d["bindings"].append(b)
    hit = False
    for n in d["nodes"]:
        for lane in (n.get("data", {}).get("tasks") or []):
            for t in lane:
                if t.get("id") == GC_TASK_ID:
                    t["data"]["name"] = "=bindings.bGCAppNm1"
                    t["data"]["folderPath"] = "=bindings.bGCAppFp2"
                    t["data"].setdefault("inputs", [])
                    t["data"]["outputs"] = [
                        {"name": n2, "id": v, "var": v, "value": v,
                         "source": f"={n2}", "target": f"={v}", "type": "string",
                         "elementId": t.get("elementId", "")}
                        for n2, v in GC_OUTPUTS]
                    hit = True
    assert hit, f"{GC_TASK_ID} not found in grandchild caseplan"
    json.dump(d, open(path, "w"), separators=(",", ":"))


def patch_gc_bpmn(path):
    s = open(path).read()
    assert s.count("</uipath:bindings>") == 1
    if "bGCAppNm1" not in s:
        s = s.replace("      </uipath:bindings>", GC_APP_BINDING_XML, 1)
    # fill the two empty refs (they belong to the t9BUmAX8k userTask context)
    s = s.replace('<uipath:input name="name" type="string" value="=bindings." />',
                  '<uipath:input name="name" type="string" value="=bindings.bGCAppNm1" />', 1)
    s = s.replace('<uipath:input name="folderPath" type="string" value="=bindings." />',
                  '<uipath:input name="folderPath" type="string" value="=bindings.bGCAppFp2" />', 1)
    # inject outputs into the t9BUmAX8k userTask (after its </uipath:context>)
    if GC_OUTPUTS[0][0] not in s:
        m = re.search(r'(<bpmn:userTask id="' + GC_TASK_ID + r'".*?</uipath:context>\n)', s, re.S)
        assert m, "grandchild userTask context not found"
        s = s[:m.end()] + GC_OUTPUT_XML + s[m.end():]
    open(path, "w").write(s)


def main():
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    dl = sys.argv[1]
    dl_child = os.path.join(dl, "clearflow-stakeholder-parent")
    dl_gc = os.path.join(dl, "clearflow-obligation-grandchild")
    assert os.path.isdir(dl_child) and os.path.isdir(dl_gc), f"cases missing in {dl}"

    # CHILD: copy download (with canvas bindings) -> patch start event + entry-points
    for f in ("caseplan.json", "caseplan.json.bpmn"):
        shutil.copy(os.path.join(dl_child, f), os.path.join(CHILD_CANON, f))
    patch_child_bpmn(os.path.join(CHILD_CANON, "caseplan.json.bpmn"))
    patch_child_caseplan(os.path.join(CHILD_CANON, "caseplan.json"))
    json.dump(CHILD_ENTRY_POINTS, open(os.path.join(CHILD_CANON, "entry-points.json"), "w"), indent=2)

    # GRANDCHILD: copy download (with canvas bindings) -> wire Human-action; start ok
    for f in ("caseplan.json", "caseplan.json.bpmn", "entry-points.json"):
        shutil.copy(os.path.join(dl_gc, f), os.path.join(GC_CANON, f))
    patch_gc_caseplan(os.path.join(GC_CANON, "caseplan.json"))
    patch_gc_bpmn(os.path.join(GC_CANON, "caseplan.json.bpmn"))

    print("merge complete -> child start-event + entry-points patched; "
          "grandchild Human-action wired to app; canvas bindings preserved")


if __name__ == "__main__":
    main()

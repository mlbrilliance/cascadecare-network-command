#!/usr/bin/env python3
"""Apply the child + grandchild case fixes onto a fresh Studio Web canvas download,
preserving the canvas-authored task bindings (assess/classify/register/audit/ViVE)
and writing the merged cases into the canonical standalone dirs (pack-solution.sh
then copies them into the solution).

Three deterministic fixes the canvas does NOT produce:

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

  BOTH (1.0.23 closing-stage fix)
    - the closing stages ("Stakeholder Resolved" Stage_SUCBZw / "Obligation
      Discharged" Stage_otF4rP) are isRequired:true with a required-tasks-completed
      exit. Empty, that exit can NEVER fire -> required-stages-completed never
      satisfied -> every instance sits Running forever (38 stuck instances
      cancelled 2026-06-11). The canvas session adds a generate-audit-record
      closing task to each; this merge asserts the task exists in the download
      and forces isRequired:true on every task in those stages (caseplan +
      embedded definition JSON) because the canvas historically leaves new
      tasks Required=false -- the exact defect that once skipped the grandchild
      spawn and the ViVE tasks.

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


# S025 (ADR-0002): OOTB Case App surface. caseAppEnabled:true requires a caseAppConfig
# (V20 / skills PR #216: absent config breaks the Case App UI). Restored if the canvas
# strips it; a canvas-authored config wins (setdefault).
CASE_APP_CONFIGS = {
    "clearflow-stakeholder-parent": {
        "caseSummary": ('=string.Format("Stakeholder {0} - BAA position: {1}", '
                        'vars.var_stakeholder_id, vars.var_baa_disclosure_position)'),
        "sections": [
            {"id": "section-ba3b1c76-bab8-4ad1-acf6-76da3166ccaf", "title": "Stakeholder",
             "details": '{"Stakeholder":"=vars.var_stakeholder_id",'
                        '"Master case":"=vars.var_master_case_id"}'},
            {"id": "section-b93648bd-cece-4de5-be3e-d3cb1f8fd6c7", "title": "Obligation posture",
             "details": '{"BAA disclosure position":"=vars.var_baa_disclosure_position",'
                        '"Privilege flag":"=vars.var_privilege_flag"}'},
        ],
    },
    "clearflow-obligation-grandchild": {
        "caseSummary": ('=string.Format("{0} obligation - ref {1}", '
                        'vars.var_obligation_type, vars.var_subpoena_reference_id)'),
        "sections": [
            {"id": "section-da977890-3420-4c94-8c1d-9f91f1185bb7", "title": "Obligation",
             "details": '{"Type":"=vars.var_obligation_type",'
                        '"Subpoena reference":"=vars.var_subpoena_reference_id"}'},
            {"id": "section-4f3e9d54-c65e-4d46-9846-890de5e48f50", "title": "Case lineage",
             "details": '{"Parent case":"=vars.var_parent_case_id",'
                        '"Master case":"=vars.var_master_case_id"}'},
        ],
    },
}


def ensure_case_app_config(d, case_name):
    if d["metadata"].get("caseAppEnabled"):
        d["metadata"].setdefault("caseAppConfig", CASE_APP_CONFIGS[case_name])


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


def _flip_or_inject_required(s, tid):
    """Like _flip_required, but injects the key when the canvas omitted it
    entirely (new canvas-authored tasks sometimes ship without isRequired)."""
    i = s.find('{"id":"' + tid + '"')
    assert i >= 0, f"{tid} not in embedded JSON"
    if s.find('"isRequired"', i, i + 2000) < 0:
        anchor = '{"id":"' + tid + '",'
        assert anchor in s, f"{tid} embedded JSON not in expected key order"
        return s.replace(anchor, anchor + '"isRequired":true,', 1)
    return _flip_required(s, tid)


# --- closing-stage fix (1.0.23): the canvas-added closing task MUST be Required --
CLOSING_STAGES = {
    "clearflow-stakeholder-parent": "Stage_SUCBZw",
    "clearflow-obligation-grandchild": "Stage_otF4rP",
}


def require_closing_tasks(caseplan_path, bpmn_path, stage_id):
    """Assert the closing stage holds >=1 task in the download (the canvas edit
    happened) and force isRequired:true on every task in it, in both layers."""
    d = json.load(open(caseplan_path))
    ids = []
    for n in d["nodes"]:
        if n.get("id") != stage_id:
            continue
        for lane in (n.get("data", {}).get("tasks") or []):
            for t in lane:
                t["isRequired"] = True
                ids.append(t["id"])
    assert ids, (
        f"{stage_id} has no tasks in the download — the closing-task canvas "
        "edit is missing. Add the generate-audit-record task in Studio Web "
        "before merging (empty required stage = case never completes)."
    )
    json.dump(d, open(caseplan_path, "w"), separators=(",", ":"))
    s = open(bpmn_path).read()
    for tid in ids:
        s = _flip_or_inject_required(s, tid)
    open(bpmn_path, "w").write(s)
    return ids


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
    ensure_case_app_config(d, "clearflow-stakeholder-parent")
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
    ensure_case_app_config(d, "clearflow-obligation-grandchild")
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
    child_closers = require_closing_tasks(
        os.path.join(CHILD_CANON, "caseplan.json"),
        os.path.join(CHILD_CANON, "caseplan.json.bpmn"),
        CLOSING_STAGES["clearflow-stakeholder-parent"])

    # GRANDCHILD: copy download (with canvas bindings) -> wire Human-action; start ok
    for f in ("caseplan.json", "caseplan.json.bpmn", "entry-points.json"):
        shutil.copy(os.path.join(dl_gc, f), os.path.join(GC_CANON, f))
    patch_gc_caseplan(os.path.join(GC_CANON, "caseplan.json"))
    patch_gc_bpmn(os.path.join(GC_CANON, "caseplan.json.bpmn"))
    gc_closers = require_closing_tasks(
        os.path.join(GC_CANON, "caseplan.json"),
        os.path.join(GC_CANON, "caseplan.json.bpmn"),
        CLOSING_STAGES["clearflow-obligation-grandchild"])

    print("merge complete -> child start-event + entry-points patched; "
          "grandchild Human-action wired to app; canvas bindings preserved; "
          f"closing tasks Required (child={child_closers}, gc={gc_closers})")


if __name__ == "__main__":
    main()

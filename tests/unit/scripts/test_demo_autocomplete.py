"""Tests for scripts/demo_autocomplete.py — demo pacing helper (uip CLI driven)."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import scripts.demo_autocomplete as da


def _task(task_id: int, title: str, folder_id: int = 3059530, status: str = "Pending", type_: str = "AppTask") -> dict:
    return {"Id": task_id, "Title": title, "Status": status, "Type": type_, "FolderId": folder_id}


FIDUCIARY_TASKS = [
    _task(1001, "Tri-Party Fiduciary Conflict: Apex vs ClearFlow vs Provider BAAs"),
    _task(1002, "Tri-Party Fiduciary Conflict: Apex vs ClearFlow vs Provider BAAs"),
    _task(1003, "Tri-Party Fiduciary Conflict: Apex vs ClearFlow vs Provider BAAs"),
]

OBLIGATION_TASKS = [
    _task(2001, "Prepare & File Obligation Response"),
    _task(2002, "Prepare & File Obligation Response"),
    _task(2003, "Prepare & File Obligation Response"),
    _task(2004, "Prepare & File Obligation Response"),
    _task(2005, "Prepare & File Obligation Response"),
    _task(2006, "Prepare & File Obligation Response"),
]


class TestClassifyTasks:
    def test_fiduciary_classified(self):
        tasks = FIDUCIARY_TASKS + OBLIGATION_TASKS
        fid, obl = da.classify_tasks(tasks)
        assert fid == FIDUCIARY_TASKS
        assert obl == OBLIGATION_TASKS

    def test_empty_input(self):
        fid, obl = da.classify_tasks([])
        assert fid == []
        assert obl == []

    def test_unknown_title_ignored(self):
        tasks = [_task(9999, "Some Other Task")]
        fid, obl = da.classify_tasks(tasks)
        assert fid == []
        assert obl == []


class TestPartitionTasks:
    def test_keep_two_fiduciary(self):
        auto, keep = da.partition_tasks(FIDUCIARY_TASKS, keep=2)
        assert len(keep) == 2
        assert len(auto) == 1
        assert keep == FIDUCIARY_TASKS[-2:]
        assert auto == FIDUCIARY_TASKS[:-2]

    def test_keep_two_obligation(self):
        auto, keep = da.partition_tasks(OBLIGATION_TASKS, keep=2)
        assert len(keep) == 2
        assert len(auto) == 4

    def test_fewer_than_keep_returns_all_as_keep(self):
        tasks = FIDUCIARY_TASKS[:1]
        auto, keep = da.partition_tasks(tasks, keep=2)
        assert auto == []
        assert keep == tasks

    def test_exactly_keep_count(self):
        tasks = FIDUCIARY_TASKS[:2]
        auto, keep = da.partition_tasks(tasks, keep=2)
        assert auto == []
        assert keep == tasks


class TestBuildPayload:
    def test_fiduciary_approve_payload(self):
        payload = da.build_fiduciary_payload(decision="Approve", index=0)
        assert payload["ReviewerDecision"] == "Approve"
        assert payload["ReviewerId"] == "AutoDemo"
        assert "ReviewerContext" in payload
        assert "ReviewTimestamp" in payload

    def test_fiduciary_deny_payload(self):
        payload = da.build_fiduciary_payload(decision="Deny", index=1)
        assert payload["ReviewerDecision"] == "Deny"

    def test_obligation_filed_payload(self):
        payload = da.build_obligation_payload(disposition="filed", index=0)
        assert payload["ResponseDisposition"] == "filed"
        assert payload["ReviewerId"] == "AutoDemo"
        assert "ResponseNarrative" in payload
        assert "FiledTimestamp" in payload

    def test_obligation_withdrawn_payload(self):
        payload = da.build_obligation_payload(disposition="withdrawn", index=1)
        assert payload["ResponseDisposition"] == "withdrawn"

    def test_timestamp_is_iso8601(self):
        payload = da.build_fiduciary_payload(decision="Approve", index=0)
        ts = payload["ReviewTimestamp"]
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        assert parsed.tzinfo is not None


class TestAutoDecision:
    def test_fiduciary_alternates_approve_deny(self):
        decisions = [da.auto_fiduciary_decision(i) for i in range(4)]
        assert decisions == ["Approve", "Deny", "Approve", "Deny"]

    def test_obligation_alternates_filed_withdrawn(self):
        dispositions = [da.auto_obligation_disposition(i) for i in range(4)]
        assert dispositions == ["filed", "withdrawn", "filed", "withdrawn"]


class TestActionMapping:
    def test_fiduciary_action_is_decision(self):
        assert da.fiduciary_action("Approve") == "Approve"
        assert da.fiduciary_action("Deny") == "Deny"

    def test_obligation_action_maps_disposition(self):
        # Defaults are best-guess outcome names (env-overridable).
        assert da.obligation_action("filed") == "File"
        assert da.obligation_action("withdrawn") == "Withdraw"

    def test_obligation_action_unknown_passthrough(self):
        assert da.obligation_action("escalated") == "escalated"


class TestParseTaskList:
    def test_data_key(self):
        raw = {"Result": "Success", "Data": FIDUCIARY_TASKS}
        assert da.parse_task_list(raw) == FIDUCIARY_TASKS

    def test_value_key_fallback(self):
        raw = {"value": OBLIGATION_TASKS}
        assert da.parse_task_list(raw) == OBLIGATION_TASKS

    def test_empty(self):
        assert da.parse_task_list({"Data": []}) == []
        assert da.parse_task_list({}) == []


class TestFilterActionable:
    def test_keeps_pending_apptasks(self):
        tasks = FIDUCIARY_TASKS + OBLIGATION_TASKS
        assert da.filter_actionable(tasks) == tasks

    def test_drops_completed(self):
        tasks = [_task(1, "Tri-Party Fiduciary Conflict", status="Completed")]
        assert da.filter_actionable(tasks) == []

    def test_drops_non_apptask_type(self):
        tasks = [_task(1, "Tri-Party Fiduciary Conflict", type_="FormTask")]
        assert da.filter_actionable(tasks) == []

    def test_folder_scope(self):
        a = _task(1, "Tri-Party Fiduciary Conflict", folder_id=3059530)
        b = _task(2, "Prepare & File Obligation Response", folder_id=999)
        assert da.filter_actionable([a, b], folder_id=3059530) == [a]


class TestBuildCompleteArgv:
    def test_includes_id_type_folder_action_data(self):
        argv = da.build_complete_argv(
            FIDUCIARY_TASKS[0], action="Approve", data={"ReviewerDecision": "Approve"}
        )
        assert argv[:2] == ["tasks", "complete"]
        assert "1001" in argv
        assert "--type" in argv and "AppTask" in argv
        assert "--folder-id" in argv and "3059530" in argv
        assert "--action" in argv and "Approve" in argv
        # --data is a JSON-encoded string
        data_idx = argv.index("--data") + 1
        assert '"ReviewerDecision": "Approve"' in argv[data_idx]


class TestBuildAssignArgv:
    def test_assigns_to_user(self):
        argv = da.build_assign_argv(FIDUCIARY_TASKS[0], assignee="me@org.com")
        assert argv[:2] == ["tasks", "assign"]
        assert "1001" in argv
        assert "--user" in argv and "me@org.com" in argv


class TestAssignTask:
    def test_success_true(self):
        with patch.object(da, "_run_uip", return_value={"Result": "Success"}) as m:
            assert da.assign_task(FIDUCIARY_TASKS[0], "me@org.com") is True
        argv = m.call_args[0][0]
        assert argv[:2] == ["tasks", "assign"]

    def test_failure_false(self):
        with patch.object(da, "_run_uip", return_value={"Result": "Failure"}):
            assert da.assign_task(FIDUCIARY_TASKS[0], "me@org.com") is False


class TestClassifyResult:
    def test_success_is_completed(self):
        assert da.classify_result({"Result": "Success"}) == da.COMPLETED

    def test_already_deleted_is_orphaned(self):
        result = {"Result": "Failure", "Instructions": "This action has been already deleted"}
        assert da.classify_result(result) == da.ORPHANED

    def test_other_failure_is_failed(self):
        result = {"Result": "Failure", "Message": "Invalid action 'Approve'"}
        assert da.classify_result(result) == da.FAILED


class TestCompleteTask:
    def test_completes_via_run_uip(self):
        with patch.object(da, "_run_uip", return_value={"Result": "Success"}) as m:
            status, _ = da.complete_task(
                FIDUCIARY_TASKS[0], action="Approve", data={"ReviewerDecision": "Approve"}
            )
        assert status == da.COMPLETED
        m.assert_called_once()
        argv = m.call_args[0][0]
        assert argv[:2] == ["tasks", "complete"]

    def test_orphan_classified(self):
        orphan = {"Result": "Failure", "Instructions": "This action has been already deleted"}
        with patch.object(da, "_run_uip", return_value=orphan):
            status, _ = da.complete_task(OBLIGATION_TASKS[0], action="File", data={})
        assert status == da.ORPHANED


class TestRunUip:
    def test_parses_json_stdout(self):
        completed = type("P", (), {"stdout": '{"Result":"Success"}', "stderr": "", "returncode": 0})()
        with patch.object(da.subprocess, "run", return_value=completed):
            assert da._run_uip(["tasks", "list"]) == {"Result": "Success"}

    def test_non_json_raises(self):
        completed = type("P", (), {"stdout": "<html>nope</html>", "stderr": "", "returncode": 1})()
        with patch.object(da.subprocess, "run", return_value=completed):
            try:
                da._run_uip(["tasks", "list"])
            except RuntimeError as exc:
                assert "did not return JSON" in str(exc)
            else:
                raise AssertionError("expected RuntimeError")

    def test_non_dict_json_wrapped_in_data(self):
        completed = type("P", (), {"stdout": "[1, 2, 3]", "stderr": "", "returncode": 0})()
        with patch.object(da.subprocess, "run", return_value=completed):
            assert da._run_uip(["x"]) == {"Data": [1, 2, 3]}

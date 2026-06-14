"""Tests for scripts/demo_autocomplete.py — demo pacing helper."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, call, patch

import pytest

import scripts.demo_autocomplete as da


FOLDER_KEY = "de7b7c18-d743-4c8c-b555-9bd3b96fe524"


def _task(task_id: int, title: str) -> dict:
    return {"Id": task_id, "Title": title, "Status": "Pending"}


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


class TestCompleteTask:
    def test_complete_calls_post(self):
        client = MagicMock()
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        client.post.return_value = resp

        da.complete_task(client, FOLDER_KEY, task_id=1001, action_data={"ReviewerDecision": "Approve"})

        client.post.assert_called_once()
        url = client.post.call_args[0][0]
        assert "1001" in url
        assert "Complete" in url

    def test_complete_includes_folder_key_header(self):
        client = MagicMock()
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        client.post.return_value = resp

        da.complete_task(client, FOLDER_KEY, task_id=1001, action_data={})

        _, kwargs = client.post.call_args
        headers = kwargs.get("headers", {})
        assert headers.get("X-UIPATH-OrganizationUnitId") == FOLDER_KEY


class TestListPendingTasks:
    def test_returns_value_list(self):
        client = MagicMock()
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {"value": FIDUCIARY_TASKS + OBLIGATION_TASKS}
        client.get.return_value = resp

        result = da.list_pending_tasks(client, FOLDER_KEY)
        assert len(result) == len(FIDUCIARY_TASKS) + len(OBLIGATION_TASKS)

    def test_empty_tenant_returns_empty_list(self):
        client = MagicMock()
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = {"value": []}
        client.get.return_value = resp

        result = da.list_pending_tasks(client, FOLDER_KEY)
        assert result == []

"""Unit tests for the UiPath Maestro Case CLI client.

All tests use mocked subprocess calls — no real UiPath tenant required.
"""

from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from cascadecare.uipath.maestro_client import (
    CaseInstance,
    CaseProcess,
    MaestroCaseClient,
    MaestroCaseError,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

UIP_BIN = "/fake/uip"

_PROCESS_LIST_RESPONSE = {
    "Result": "Success",
    "Code": "CaseProcessList",
    "Data": [
        {
            "key": "clearflow-crisis",
            "name": "clearflow-crisis",
            "displayName": "ClearFlow Crisis Case",
            "description": "Master crisis case for ClearFlow Network Command",
            "processType": "CaseManagement",
            "version": "1.0.0",
            "folderKey": "folder-abc-123",
        }
    ],
}

_PROCESS_RUN_RESPONSE = {
    "Result": "Success",
    "Code": "CaseProcessRun",
    "Data": {
        "instanceId": "inst-abc-123",
        "jobKey": "job-xyz-456",
        "runId": "run-def-789",
        "processKey": "clearflow-crisis",
        "folderKey": "folder-abc-123",
        "status": "Running",
    },
}

_INSTANCE_GET_RESPONSE = {
    "Result": "Success",
    "Code": "CaseInstanceGet",
    "Data": {
        "id": "inst-abc-123",
        "processKey": "clearflow-crisis",
        "folderKey": "folder-abc-123",
        "status": "Running",
        "currentStageId": "Stage_ugoiTN",
        "currentStageName": "Initial Response",
        "reversalNumber": 1,
        "goal": "Determine if ClearFlow is the breach vector",
        "simulatedDay": 1,
    },
}

_INSTANCE_LIST_RESPONSE = {
    "Result": "Success",
    "Code": "CaseInstanceList",
    "Data": [
        {
            "id": "inst-abc-123",
            "processKey": "clearflow-crisis",
            "status": "Running",
            "currentStageName": "Initial Response",
        }
    ],
}


def _make_ok_result(payload: dict) -> MagicMock:
    result = MagicMock()
    result.returncode = 0
    result.stdout = json.dumps(payload)
    result.stderr = ""
    return result


def _make_fail_result(message: str, code: int = 1) -> MagicMock:
    result = MagicMock()
    result.returncode = code
    result.stdout = json.dumps({"Result": "Failure", "Message": message})
    result.stderr = ""
    return result


@pytest.fixture
def client() -> MaestroCaseClient:
    return MaestroCaseClient(uip_bin=UIP_BIN, folder_key="folder-abc-123")


# ---------------------------------------------------------------------------
# Tests — process list
# ---------------------------------------------------------------------------


class TestListProcesses:
    def test_returns_typed_process_list(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result(_PROCESS_LIST_RESPONSE)
            processes = client.list_processes()

        assert len(processes) == 1
        proc = processes[0]
        assert isinstance(proc, CaseProcess)
        assert proc.key == "clearflow-crisis"
        assert proc.folder_key == "folder-abc-123"

    def test_includes_folder_key_flag(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result(_PROCESS_LIST_RESPONSE)
            client.list_processes()

        cmd = mock_run.call_args[0][0]
        assert "--folder-key" in cmd
        assert "folder-abc-123" in cmd

    def test_raises_on_cli_error(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_fail_result("Unauthorized (401)")
            with pytest.raises(MaestroCaseError, match="Unauthorized"):
                client.list_processes()


# ---------------------------------------------------------------------------
# Tests — process run
# ---------------------------------------------------------------------------


class TestRunProcess:
    def test_returns_instance_with_id(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result(_PROCESS_RUN_RESPONSE)
            instance = client.run_process("clearflow-crisis")

        assert isinstance(instance, CaseInstance)
        assert instance.instance_id == "inst-abc-123"
        assert instance.job_key == "job-xyz-456"
        assert instance.process_key == "clearflow-crisis"

    def test_passes_process_key_to_cli(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result(_PROCESS_RUN_RESPONSE)
            client.run_process("clearflow-crisis")

        cmd = mock_run.call_args[0][0]
        assert "clearflow-crisis" in cmd

    def test_passes_input_variables_as_json(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result(_PROCESS_RUN_RESPONSE)
            client.run_process(
                "clearflow-crisis",
                input_variables={"CaseGoal": "Determine breach vector", "SimulatedDay": 1},
            )

        cmd = mock_run.call_args[0][0]
        # Input variables should appear as JSON somewhere in the command
        full_cmd = " ".join(cmd)
        assert "CaseGoal" in full_cmd or any("CaseGoal" in str(arg) for arg in cmd)


# ---------------------------------------------------------------------------
# Tests — instance get
# ---------------------------------------------------------------------------


class TestGetInstance:
    def test_returns_typed_instance(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result(_INSTANCE_GET_RESPONSE)
            instance = client.get_instance("inst-abc-123")

        assert isinstance(instance, CaseInstance)
        assert instance.instance_id == "inst-abc-123"
        assert instance.status == "Running"
        assert instance.current_stage_name == "Initial Response"

    def test_raises_when_instance_not_found(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_fail_result("Instance not found")
            with pytest.raises(MaestroCaseError, match="Instance not found"):
                client.get_instance("nonexistent-id")


# ---------------------------------------------------------------------------
# Tests — instance list
# ---------------------------------------------------------------------------


class TestListInstances:
    def test_returns_list_of_instances(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result(_INSTANCE_LIST_RESPONSE)
            instances = client.list_instances("clearflow-crisis")

        assert len(instances) == 1
        assert instances[0].instance_id == "inst-abc-123"

    def test_filters_by_status(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result(_INSTANCE_LIST_RESPONSE)
            client.list_instances("clearflow-crisis", status="Running")

        cmd = mock_run.call_args[0][0]
        full_cmd = " ".join(cmd)
        assert "Running" in full_cmd


# ---------------------------------------------------------------------------
# Tests — pause / resume
# ---------------------------------------------------------------------------


class TestPauseResume:
    def test_pause_calls_correct_subcommand(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result({"Result": "Success", "Data": {}})
            client.pause_instance("inst-abc-123")

        cmd = mock_run.call_args[0][0]
        assert "pause" in cmd

    def test_resume_calls_correct_subcommand(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result({"Result": "Success", "Data": {}})
            client.resume_instance("inst-abc-123")

        cmd = mock_run.call_args[0][0]
        assert "resume" in cmd


# ---------------------------------------------------------------------------
# Tests — cancel
# ---------------------------------------------------------------------------


class TestCancelInstance:
    def test_cancel_calls_correct_subcommand(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result({"Result": "Success", "Data": {}})
            client.cancel_instance("inst-abc-123")

        cmd = mock_run.call_args[0][0]
        assert "cancel" in cmd
        assert "inst-abc-123" in cmd
        assert "--folder-key" in cmd
        assert "folder-abc-123" in cmd

    def test_cancel_raises_on_cli_error(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_fail_result("Instance already cancelled")
            with pytest.raises(MaestroCaseError, match="already cancelled"):
                client.cancel_instance("inst-abc-123")


# ---------------------------------------------------------------------------
# Tests — global variables
# ---------------------------------------------------------------------------


class TestGetGlobalVariables:
    def test_returns_variable_dict(self, client: MaestroCaseClient) -> None:
        payload = {
            "Result": "Success",
            "Code": "CaseInstanceGlobalVariables",
            "Data": {
                "goal": "Determine if ClearFlow is the breach vector",
                "reversalNumber": 1,
                "simulatedDay": 1,
            },
        }
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result(payload)
            variables = client.get_global_variables("inst-abc-123")

        assert isinstance(variables, dict)
        assert variables["goal"] == "Determine if ClearFlow is the breach vector"
        assert variables["reversalNumber"] == 1

    def test_uses_global_variables_subcommand(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result({"Result": "Success", "Data": {}})
            client.get_global_variables("inst-abc-123")

        cmd = mock_run.call_args[0][0]
        assert "global-variables" in cmd
        assert "inst-abc-123" in cmd
        assert "--folder-key" in cmd

    def test_returns_empty_dict_when_no_data(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_ok_result({"Result": "Success", "Data": {}})
            variables = client.get_global_variables("inst-abc-123")

        assert variables == {}


# ---------------------------------------------------------------------------
# Tests — _run error paths
# ---------------------------------------------------------------------------


class TestRunErrors:
    def test_nonzero_exit_raises_maestro_error(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_fail_result("Bad request", code=2)
            with pytest.raises(MaestroCaseError, match="Bad request"):
                client.list_processes()

    def test_timeout_raises_maestro_error(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="uip", timeout=60)
            with pytest.raises(MaestroCaseError, match="timed out"):
                client.list_processes()

    def test_missing_binary_raises_maestro_error(self, client: MaestroCaseClient) -> None:
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("no such file")
            with pytest.raises(MaestroCaseError, match="not found"):
                client.list_processes()

    def test_non_json_output_raises_maestro_error(self, client: MaestroCaseClient) -> None:
        bad = MagicMock()
        bad.returncode = 0
        bad.stdout = "this is not json"
        bad.stderr = ""
        with patch("cascadecare.uipath.maestro_client.subprocess.run") as mock_run:
            mock_run.return_value = bad
            with pytest.raises(MaestroCaseError, match="non-JSON"):
                client.list_processes()

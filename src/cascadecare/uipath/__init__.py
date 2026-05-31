"""UiPath Platform integration package for CascadeCare.

Build-time only — these wrappers exist so AI coding agents can inspect the
UiPath tenant during the build. None of this code runs at demo time; the
demo runs entirely as UiPath assets (Maestro Case + Flow + BPMN + Agents).

Modules
-------
auth            OAuth2 client credentials authentication
maestro_client  CLI wrapper for `uip maestro case` (typed)
"""

from cascadecare.uipath.maestro_client import (
    CaseInstance,
    CaseProcess,
    MaestroCaseClient,
    MaestroCaseError,
    from_active_session,
)

__all__ = [
    "CaseInstance",
    "CaseProcess",
    "MaestroCaseClient",
    "MaestroCaseError",
    "from_active_session",
]

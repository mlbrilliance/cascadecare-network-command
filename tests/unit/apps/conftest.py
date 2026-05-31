"""Add the Coded App backend to sys.path once for all apps tests."""
import pathlib
import sys

_BACKEND = pathlib.Path(__file__).parents[3] / "apps" / "clearflow-network-command" / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

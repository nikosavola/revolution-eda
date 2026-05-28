"""Pytest configuration for tests that don't require PySide6."""
import importlib.util
import sys
import types
from pathlib import Path

# Pre-register minimal package stubs to avoid triggering the full
# revedaEditor __init__.py which imports PySide6.
_REPO_ROOT = Path(__file__).resolve().parent.parent

# Only patch if PySide6 is not available
try:
    import PySide6  # noqa: F401
except ImportError:
    # Create stub packages so that sub-module imports work without PySide6
    for key in list(sys.modules.keys()):
        if key.startswith("revedaEditor"):
            del sys.modules[key]

    pkg = types.ModuleType("revedaEditor")
    pkg.__path__ = [str(_REPO_ROOT / "revedaEditor")]
    pkg.__package__ = "revedaEditor"
    sys.modules["revedaEditor"] = pkg

    fileio = types.ModuleType("revedaEditor.fileio")
    fileio.__path__ = [str(_REPO_ROOT / "revedaEditor" / "fileio")]
    fileio.__package__ = "revedaEditor.fileio"
    sys.modules["revedaEditor.fileio"] = fileio

    # Load schemaValidation into the module tree
    spec = importlib.util.spec_from_file_location(
        "revedaEditor.fileio.schemaValidation",
        str(_REPO_ROOT / "revedaEditor" / "fileio" / "schemaValidation.py"),
    )
    sv_mod = importlib.util.module_from_spec(spec)
    sys.modules["revedaEditor.fileio.schemaValidation"] = sv_mod
    spec.loader.exec_module(sv_mod)

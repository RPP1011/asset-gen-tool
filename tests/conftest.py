import os
import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path when tests are launched from subprocesses
ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)


@pytest.fixture(scope="session", autouse=True)
def _set_default_firestore_project():
    """
    Ensure a default Firestore project id is available when using the emulator.
    """
    os.environ.setdefault(
        "FIRESTORE_PROJECT", os.environ.get("GCLOUD_PROJECT", "asset-gen-local")
    )
    yield

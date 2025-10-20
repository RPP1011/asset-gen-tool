#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".vercel-python-env"
REQUESTED_PYTHON="${PYTHON:-python3.12}"

cleanup() {
  if [[ -d "$VENV_DIR" ]]; then
    rm -rf "$VENV_DIR"
  fi
}
trap cleanup EXIT

rm -rf "$VENV_DIR"

if command -v uv >/dev/null 2>&1; then
  uv venv --python 3.12 "$VENV_DIR"
  VENV_PYTHON="$VENV_DIR/bin/python"
  INSTALL_CMD=(uv pip install --python "$VENV_PYTHON")
else
  PYTHON_BIN="$REQUESTED_PYTHON"
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    if command -v python3.12 >/dev/null 2>&1; then
      PYTHON_BIN="$(command -v python3.12)"
    elif command -v python3 >/dev/null 2>&1; then
      PYTHON_BIN="$(command -v python3)"
      echo "Falling back to detected interpreter: $PYTHON_BIN" >&2
    else
      echo "Unable to find interpreter: $PYTHON_BIN" >&2
      exit 1
    fi
  fi
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  VENV_PYTHON="$VENV_DIR/bin/python"
  "$VENV_PYTHON" -m pip install --upgrade pip
  INSTALL_CMD=("$VENV_PYTHON" -m pip install)
fi

"${INSTALL_CMD[@]}" .

# Import every module inside the api package so missing dependencies fail fast.
"$VENV_PYTHON" - <<'PY'
import importlib
import pkgutil
import sys

package_name = "api"

try:
    package = importlib.import_module(package_name)
except Exception as exc:  # pragma: no cover
    msg = f"Failed to import {package_name!r}: {exc}"
    raise SystemExit(msg) from exc

failures = []
for module in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
    try:
        importlib.import_module(module.name)
    except Exception as exc:
        failures.append((module.name, exc))

if failures:
    for name, exc in failures:
        print(f"Failed to import {name}: {exc}", file=sys.stderr)
    raise SystemExit("Python dependency check failed")

print(f"Successfully imported all modules under '{package_name}'")
PY

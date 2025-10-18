# Makefile for asset-gen-tool
# Purpose:
# - Provide convenient developer targets for local setup, formatting, linting, testing and safe dev run.
# - Include a target to emit a small README for Python setup that is Vercel-friendly.
#
# IMPORTANT: This Makefile is intended for local development. Do NOT run long-lived servers
# in CI or in Vercel build steps. The `run` target is only for local development.
#
# Usage:
#   make help            # show available targets
#   make init            # create virtualenv and install runtime deps
#   make install-dev     # install development tools
#   make format          # run code formatters (black, isort)
#   make lint            # run linters (ruff, mypy)
#   make test            # run pytest
#   make readme          # emit a short README (python-setup guidance) to stdout or to README-PY.md
#
# Note about Vercel:
# - Vercel builds should only install runtime dependencies. Do not call `make init` from a Vercel build
#   step that also installs dev dependencies. Vercel will detect Python projects using requirements.txt
#   or pyproject configuration. Keep dev-only steps out of the build pipeline.
# - This Makefile provides guidance but does not modify Vercel behavior.

PYTHON ?= python3
VENV ?= .venv
PIP = $(PYTHON) -m pip
ACTIVATE = . $(VENV)/bin/activate

REQ = requirements.txt
REQ_DEV = requirements-dev.txt

.DEFAULT_GOAL := help

.PHONY: help init install install-dev format lint test freeze readme ci clean firebase-emulator test-firestore fire

help:
	@printf "Makefile targets for asset-gen-tool\n\n"
	@printf "  init         Create virtualenv and install runtime dependencies (safe local use)\n"
	@printf "  install-dev  Install development dependencies (dev machine only)\n"
	@printf "  format       Run code formatters (black, isort)\n"
	@printf "  lint         Run linters and static checks (ruff, mypy)\n"
	@printf "  test         Run test suite (pytest)\n"
	@printf "  firebase-emulator  Start the local Firestore emulator (requires firebase-tools)\n"
	@printf "  fire              Run pytest inside the Firestore emulator context (firestore emulator)\n"
	@printf "  freeze       Produce a pinned requirements file (pip freeze > pinned-requirements.txt)\n"
	@printf "  readme       Emit a short README with Python setup guidance (Vercel-friendly)\n"
	@printf "  ci           Run CI checks (format check, lint, test)\n"
	@printf "  clean        Remove virtualenv and temporary files\n\n"
	@printf "Notes:\n  - Firestore tests run inside the emulator; use 'make test-firestore' for a one-liner.\n"

# Create virtualenv and install runtime requirements (local only)
init:
	@echo "Creating virtual environment at $(VENV) (if missing) and installing runtime dependencies..."
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(VENV)/bin/python -m pip install --upgrade pip wheel
	@$(VENV)/bin/pip install -r $(REQ)
	@echo "Done. Activate with: source $(VENV)/bin/activate"

# Install runtime deps into the current environment (alternative to init)
install:
	@echo "Installing runtime requirements into current environment..."
	@$(PIP) install -r $(REQ)

# Install dev dependencies (local dev machines only)
install-dev:
	@echo "Installing development dependencies into the active environment (or virtualenv if activated)..."
	@$(PIP) install -r $(REQ_DEV)
	@echo "Dev dependencies installed."

# Format code
format:
	@echo "Running code formatters (black, isort)..."
	@$(VENV)/bin/black . || $(PIP) install black && $(VENV)/bin/black .
	@$(VENV)/bin/isort . || $(PIP) install isort && $(VENV)/bin/isort .
	@echo "Formatting complete."

# Lint and static analysis
lint:
	@echo "Running ruff and mypy (if available)..."
	@$(VENV)/bin/ruff check . || $(PIP) install ruff && $(VENV)/bin/ruff check .
	@if [ -f pyproject.toml ]; then \
		if $(VENV)/bin/python -c "import mypy" 2>/dev/null; then \
			$(VENV)/bin/mypy . || true; \
		else \
			echo "mypy not installed; install with 'make install-dev' to run static typing checks"; \
		fi \
	fi
	@echo "Lint complete."

# Test suite
test:
	@echo "Running tests (pytest)..."
	@$(VENV)/bin/pytest -q

firebase-emulator:
	@echo "Starting Firestore emulator (Ctrl+C to stop)..."
	@echo "Requires firebase-tools; install with 'npm install -g firebase-tools' or use npx."
	@npx --yes firebase-tools emulators:start --only firestore --project asset-gen-local

test-firestore:
	@echo "Running pytest against Firestore emulator via firebase emulators:exec..."
	@if [ -x "$(VENV)/bin/python" ]; then \
		npx --yes firebase-tools emulators:exec --only firestore --project asset-gen-local "$(VENV)/bin/python -m pytest -q"; \
	else \
		npx --yes firebase-tools emulators:exec --only firestore --project asset-gen-local "python3 -m pytest -q"; \
	fi

# Freeze installed packages to a pinned file (developer convenience)
freeze:
	@echo "Freezing installed packages to pinned-requirements.txt"
	@$(VENV)/bin/pip freeze > pinned-requirements.txt
	@echo "Wrote pinned-requirements.txt"

# Emit a README snippet with Python setup guidance, careful about Vercel
readme:
	@printf "%s\n" "----- asset-gen-tool: Python Setup Guidance (Vercel-friendly) -----"
	@cat <<-'EOF'
	Quick local setup (recommended)
	1. Create a virtual environment:
	   python3 -m venv .venv
	2. Activate the virtual environment:
	   source .venv/bin/activate
	3. Install runtime dependencies:
	   pip install -r requirements.txt
	4. (Optional) Install dev tools:
	   pip install -r requirements-dev.txt
	5. Run formatters / linters:
	   make format
	   make lint
	6. Run Firestore-backed tests:
	   make test-firestore

	Notes for Vercel deployment
	- Vercel (and similar serverless hosts) will run a build step and install runtime dependencies.
	  Keep these points in mind to avoid breaking Vercel:
	  * Vercel's Python runtime expects a requirements.txt (or pyproject with proper build backend).
	  * Do not rely on local virtualenv activation in the Vercel build; only runtime requirements listed
	    in requirements.txt should be installed by the platform.
	  * Keep dev dependencies out of requirements.txt. Use requirements-dev.txt locally for tools.
	  * If you have a pinned requirements file for reproducible builds, include it as pinned-requirements.txt
	    and point your CI to use that instead.

	Security & Credentials
	- For Firestore and GCP access, use GOOGLE_APPLICATION_CREDENTIALS or platform-provided credentials.
	- Never commit service account keys into the repository.

	EOF
	@printf "%s\n" "----- end guidance -----"

# CI target: run checks (non-destructive)
ci: format lint test
	@echo "CI checks finished."

# Clean up
clean:
	@echo "Cleaning virtualenv and generated files..."
	@rm -rf $(VENV)
	@rm -f pinned-requirements.txt
	@echo "Clean complete."

# Data Engineer Doctor — single authoritative verification pipeline.
# CI and local development must run the same command: `make verify`.

VENV ?= .venv
PYTHON := $(VENV)/bin/python
UV := $(shell command -v uv 2>/dev/null || echo $(HOME)/.local/bin/uv)

.DEFAULT_GOAL := help

.PHONY: help setup format format-check lint typecheck test validate audit build verify clean

help:
	@echo "Targets:"
	@echo "  setup        Create the virtualenv and install dev dependencies"
	@echo "  format       Auto-format with ruff"
	@echo "  format-check Check formatting (ruff)"
	@echo "  lint         Lint (ruff)"
	@echo "  typecheck    Type check (mypy, strict)"
	@echo "  test         Unit, integration, regression, fixture tests (pytest)"
	@echo "  validate     Validate all diagnosis YAML definitions"
	@echo "  audit        Dependency security audit (pip-audit)"
	@echo "  build        Build sdist + wheel"
	@echo "  verify       Run the full verification pipeline (authoritative)"

setup:
	@if command -v uv >/dev/null 2>&1 || [ -x "$(HOME)/.local/bin/uv" ]; then \
		"$(UV)" sync; \
	else \
		python3 -m venv "$(VENV)" && "$(VENV)/bin/pip" install -e ".[dev]"; \
	fi

format:
	"$(PYTHON)" -m ruff format .
	"$(PYTHON)" -m ruff check --fix .

format-check:
	"$(PYTHON)" -m ruff format --check .

lint:
	"$(PYTHON)" -m ruff check .

typecheck:
	"$(PYTHON)" -m mypy

test:
	"$(PYTHON)" -m pytest

validate:
	"$(PYTHON)" -m dedoc.diagnosis.validate

audit:
	"$(PYTHON)" -m pip_audit

build:
	"$(PYTHON)" -m build

verify: format-check lint typecheck test validate audit build
	@echo "verify: PASSED"

clean:
	rm -rf dist build .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

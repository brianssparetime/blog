#!/usr/bin/env bash
set -e

# Install uv if not cached from a previous build
command -v uv || curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv if not cached from a previous build
test -d .venv || uv venv .venv

uv pip install -r requirements.txt
.venv/bin/python build.py

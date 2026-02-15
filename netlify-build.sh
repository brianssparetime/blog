#!/usr/bin/env bash
set -e

# Install uv if not cached from a previous build
if command -v uv > /dev/null; then
  echo "uv already installed (cached)"
else
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create venv if not cached from a previous build
if [ -d .venv ]; then
  echo "venv already exists (cached)"
else
  echo "Creating venv..."
  uv venv .venv
fi

echo "Installing dependencies..."
uv pip install -r requirements.txt

echo "Running build..."
.venv/bin/python build.py

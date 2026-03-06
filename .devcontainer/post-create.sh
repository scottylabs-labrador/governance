#!/usr/bin/env bash
set -e

# Install Python dependencies
uv sync

# Create uvlint alias
uvlint_alias="alias uvlint='uv run ruff check && uv run mypy . && uv run ty check'"
if ! grep -q "$uvlint_alias" ~/.zshrc; then
  echo "$uvlint_alias" >>~/.zshrc
fi

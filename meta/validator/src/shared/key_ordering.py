"""Schema-based TOML key ordering validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from meta.validator.src.reporter import Reporter


class KeyOrdering:
    """Validate TOML key ordering against a JSON schema ordering."""

    def __init__(self, schema_path: str, reporter: Reporter) -> None:
        """Create a validator using the schema's properties key ordering."""
        text = Path(schema_path).read_text(encoding="utf-8")
        data = json.loads(text)
        properties = data.get("properties", {})
        self.expected_order = list(properties.keys())
        self.reporter = reporter

    def validate(self, file_path: str, data: Mapping[str, object]) -> None:
        """Validate key order for a single TOML mapping."""
        it = iter(self.expected_order)
        key_order = list(data.keys())
        if all(key in it for key in key_order):
            return

        self.reporter.insert_error(
            file_path,
            (
                f"Invalid key order for {file_path}.\n"
                f"    - expected (schema): {self.expected_order}\n"
                f"    - found (file): {key_order}"
            ),
        )

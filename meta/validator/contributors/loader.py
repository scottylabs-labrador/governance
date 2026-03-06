"""Load contributor TOML files from disk."""

from pathlib import Path
from typing import TYPE_CHECKING, Any

import tomli

from meta.models import Contributor
from meta.validator.shared.key_ordering import KeyOrdering

if TYPE_CHECKING:
    from meta.validator.shared.reporter import Reporter

CONTRIBUTORS_GLOB = "contributors/*.toml"
CONTRIBUTOR_SCHEMA_PATH = "__meta/schemas/contributor.schema.json"


def load_contributors(reporter: Reporter) -> dict[str, Contributor]:
    """Load all contributor TOML files."""
    contributors: dict[str, Contributor] = {}
    key_ordering = KeyOrdering(CONTRIBUTOR_SCHEMA_PATH, reporter)
    for path in sorted(Path().glob(CONTRIBUTORS_GLOB)):
        if not path.is_file():
            continue

        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = tomli.loads(content)
        file_path = f"contributors/{path.name}"
        key_ordering.validate(file_path, data)
        contributor = Contributor.model_validate(data)
        contributors[file_path] = contributor

    return contributors

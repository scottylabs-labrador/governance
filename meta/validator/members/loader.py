"""Load contributor TOML files from disk."""

import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from meta.models import Member
from meta.validator.shared import KeyOrdering

if TYPE_CHECKING:
    from meta.validator.shared import Reporter

MEMBERS_GLOB = "members/*.toml"
MEMBER_SCHEMA_PATH = "meta/schemas/member.schema.json"


def load_members(
    reporter: Reporter,
    members_glob: str = MEMBERS_GLOB,
) -> dict[str, Member]:
    """Load all member TOML files."""
    members: dict[str, Member] = {}
    key_ordering = KeyOrdering(MEMBER_SCHEMA_PATH, reporter)
    for path in Path().glob(members_glob):
        if not path.is_file():
            reporter.insert_error(path.name, "Not a file")

        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = tomllib.loads(content)
        file_path = f"members/{path.name}"
        key_ordering.validate(file_path, data)
        data["file_path"] = file_path
        members[path.stem] = Member.model_validate(data)

    return members

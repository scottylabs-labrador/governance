"""Load contributor TOML files from disk."""

from pathlib import Path
from typing import TYPE_CHECKING, Any

import tomli

from meta.models import Member
from meta.validator.shared.key_ordering import KeyOrdering

if TYPE_CHECKING:
    from meta.validator.shared.reporter import Reporter

MEMBERS_GLOB = "members/*.toml"
MEMBER_SCHEMA_PATH = "__meta/schemas/member.schema.json"


def load_members(reporter: Reporter) -> dict[str, Member]:
    """Load all member TOML files."""
    members: dict[str, Member] = {}
    key_ordering = KeyOrdering(MEMBER_SCHEMA_PATH, reporter)
    for path in sorted(Path().glob(MEMBERS_GLOB)):
        if not path.is_file():
            continue

        content = path.read_text(encoding="utf-8")
        data: dict[str, Any] = tomli.loads(content)
        file_path = f"members/{path.name}"
        key_ordering.validate(file_path, data)
        member = Member.model_validate(data)
        members[file_path] = member

    return members

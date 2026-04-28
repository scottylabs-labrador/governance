"""Validator package smoke tests."""

from meta.validator.members.loader import load_members
from meta.validator.shared import Reporter

MEMBER_SCHEMA_PATH = "meta/schemas/member.schema.json"


def test_member_key_ordering() -> None:
    """Members key ordering must be validated."""
    reporter = Reporter()
    load_members(reporter, "meta/validator/tests/members/wrong-key-ordering.toml")
    assert len(reporter._errors) > 0  # noqa: SLF001

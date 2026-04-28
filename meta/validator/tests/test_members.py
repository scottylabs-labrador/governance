"""Validator package smoke tests."""

from meta.validator.src.members.loader import load_members
from meta.validator.src.members.validator import MemberValidator
from meta.validator.src.reporter import ErrorCode, Reporter
from meta.validator.tests.helper import has_error, no_errors


def test_member_valid() -> None:
    """Members must be valid."""
    reporter = Reporter()
    members = load_members(reporter, "meta/validator/tests/members/valid.toml")
    assert no_errors(reporter)
    MemberValidator(members, reporter).validate()
    assert no_errors(reporter)


def test_member_key_ordering() -> None:
    """Members key ordering must be validated."""
    reporter = Reporter()
    load_members(reporter, "meta/validator/tests/members/wrong-key-ordering.toml")
    assert has_error(reporter, ErrorCode.MEMBER_KEY_ORDERING)


def test_member_not_file() -> None:
    """Members must be a file."""
    reporter = Reporter()
    load_members(reporter, "meta/validator/tests/members/*")
    assert has_error(reporter, ErrorCode.MEMBER_NOT_FILE)

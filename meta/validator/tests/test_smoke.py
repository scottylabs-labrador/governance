"""Validator package smoke tests."""

from meta.validator import main


def test_main_is_cli_entrypoint() -> None:
    """Console script ``validate`` must keep targeting ``main``."""
    assert main.__name__ == "main"

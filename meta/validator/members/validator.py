"""Member validation runner."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from meta.models import Member
    from meta.validator.shared.reporter import Reporter


class MemberValidator:
    """Run contributor validation and record results."""

    def __init__(
        self,
        members: dict[str, Member],
        reporter: Reporter,
    ) -> None:
        """Create a contributor validator."""
        self.members = members
        self.reporter = reporter

    def validate(self) -> None:
        """Validate all contributors.

        This includes:
        - Validating that the GitHub username is valid
        - Validating that the Andrew ID maps to a user in Keycloak
        - Validating that the email from Andrew ID is in Slack
        """

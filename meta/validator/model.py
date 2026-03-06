"""Data models for governance validation."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Contributor:
    """A contributor with key order for schema validation."""

    full_name: str
    github_username: str
    slack_member_id: Optional[str] = None
    key_order: list[str] = field(default_factory=list)

    def get_key_order(self) -> list[str]:
        return self.key_order

    def set_key_order(self, order: list[str]) -> None:
        self.key_order = order


@dataclass
class Team:
    """A team with key order for schema validation."""

    name: str
    slug: str
    maintainers: list[str]
    contributors: list[str]
    applicants: Optional[list[str]] = None
    repos: list[str] = field(default_factory=list)
    slack_channel_ids: list[str] = field(default_factory=list)
    key_order: list[str] = field(default_factory=list)

    def get_key_order(self) -> list[str]:
        return self.key_order

    def set_key_order(self, order: list[str]) -> None:
        self.key_order = order


@dataclass(frozen=True)
class EntityKey:
    """Key for looking up an entity (contributor or team) by kind and name."""

    kind: str  # "team" | "contributor"
    name: str  # file_stem

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EntityKey):
            return NotImplemented
        return self.name == other.name

    def __str__(self) -> str:
        return self.name

    def scoped_id(self) -> str:
        return f"{self.kind}:{self.name}"


@dataclass
class ValidationError:
    file: str
    message: str


@dataclass
class ValidationWarning:
    file: str
    message: str


@dataclass
class FileValidationMessages:
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationWarning] = field(default_factory=list)


@dataclass
class ValidationStatistics:
    contributors_count: int
    teams_count: int
    valid_files_count: int
    invalid_files_count: int
    total_errors: int
    total_warnings: int


@dataclass
class ValidationReport:
    valid: bool
    stats: ValidationStatistics
    files: dict[str, FileValidationMessages]

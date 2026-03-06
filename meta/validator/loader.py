"""Load contributors, teams, and schema key orderings from disk."""

import json
from pathlib import Path

import tomli

from .model import Contributor, EntityKey, Team

CONTRIBUTORS_GLOB = "contributors/*.toml"
TEAMS_GLOB = "teams/*.toml"


def _toml_key_order(content: str) -> list[str]:
    """Parse TOML and return top-level keys in order (using tomli's behavior)."""
    data = tomli.loads(content)
    return list(data.keys())


def _parse_contributor(content: str, key_order: list[str]) -> Contributor:
    data = tomli.loads(content)
    return Contributor(
        full_name=data["full-name"],
        github_username=data["github-username"],
        slack_member_id=data.get("slack-member-id"),
        key_order=key_order,
    )


def _parse_team(content: str, key_order: list[str]) -> Team:
    data = tomli.loads(content)
    return Team(
        name=data["name"],
        slug=data["slug"],
        maintainers=data["maintainers"],
        contributors=data["contributors"],
        applicants=data.get("applicants"),
        repos=data.get("repos", []),
        slack_channel_ids=data.get("slack-channel-ids", []),
        key_order=key_order,
    )


def load_contributors() -> dict[EntityKey, Contributor]:
    """Load all contributor TOML files."""
    out: dict[EntityKey, Contributor] = {}
    for path in sorted(Path(".").glob(CONTRIBUTORS_GLOB)):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        key_order = _toml_key_order(content)
        c = _parse_contributor(content, key_order)
        key = EntityKey(kind="contributor", name=path.stem)
        out[key] = c
    return out


def load_teams() -> dict[EntityKey, Team]:
    """Load all team TOML files."""
    out: dict[EntityKey, Team] = {}
    for path in sorted(Path(".").glob(TEAMS_GLOB)):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        key_order = _toml_key_order(content)
        t = _parse_team(content, key_order)
        key = EntityKey(kind="team", name=path.stem)
        out[key] = t
    return out


def load_schema_key_ordering(schema_path: str) -> list[str]:
    """Load JSON schema and return the order of keys in the properties object."""
    text = Path(schema_path).read_text(encoding="utf-8")
    data = json.loads(text)
    # In JSON, "properties" order is preserved in Python 3.7+ when loading with json.
    properties = data.get("properties", {})
    return list(properties.keys())

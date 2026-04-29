# 5. define member schema

Date: 2026-04-28

## Status

Accepted

## Context

The member schema is very short and straightforward, but we would like to explain
the reasoning behind the design in this ADR.

## Decision

First, we use the GitHub username as the filename. We could use the Andrew ID as
the filename, and since the Andrew ID is linked to a GitHub account through Keycloak,
in theory we could remove the entire `members/` directory. However, when a Labrador
member graduates from CMU, we would still like to keep their record, hence we
use the GitHub username as the filename and make Andrew ID optional.

The only other field is the `full-name` field, which we could obtain from Keycloak,
but we would like this information to be publicly visible so anyone can also easily
identify the members in the Labrador organization and each team.

## Consequences

The reasoning behind the design of the member schema is now documented in this ADR.

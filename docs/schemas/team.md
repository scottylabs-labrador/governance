# Adding a team

> [!NOTE]
> This is for team maintainers seeking to register their team.

Create a new TOML file in `teams/` with the team slug as the filename:

```toml
# The team slug is used to identify the team internally (e.g. Slack channel name).
# It should be a short, lowercase, and hyphen-separated string.
slug = "your-team-slug"

# The name is used to identify the team publicly (e.g. GitHub org team name).
name = "Your Team Name"

# The website is not required.
website = "your-team-website.com"

description = """
A brief description of the team.
"""

# Set the `create-oidc-clients` field to `false` if the team does not need OIDC clients.
# OIDC clients are necessary if you want to use ScottyLabs' auth system!
#
# It defaults to true if not specified, so please remove this section if the team
# do need OIDC clients.
create-oidc-clients = false

# List of repositories owned by the team.
# Note that the owners of the repositories must be ScottyLabs-Labrador.
[[repos]]
name = "repo-name-1" # As it appears at the end of the GitHub repository URL
description = "A brief description of repo 1."

[[repos]]
name = "repo-name-2" # As it appears at the end of the GitHub repository URL
description = "A brief description of repo 2."

# List of membership records by timeframe.
# Note that only the first record will be used for synchronization.
[[membership]]

# The timeframe can be any string, but we suggest using either the year or semester.
# E.g. "2026-2027" or "Spring 2026".
timeframe = "timeframe-1"

# List of the GitHub usernames of the maintainers for this timeframe.
maintainers = ["maintainer-1", "maintainer-2"]

# List of contributors for this timeframe.
[[membership.contributors]]
github-username = "contributor-1"
title = "Contributor 1's title" # The title is optional.

[[membership.contributors]]
github-username = "contributor-2"
title = "Contributor 2's title"
```

Visit the [team schema](../../meta/schemas/team.schema.json) to learn more about
each field.

#!/bin/bash
set -e

PR_AUTHOR=$1
TEAM_FILE=$2

if ! python3 - <<'PY' "$TEAM_FILE" "$PR_AUTHOR"
import sys
import tomllib

team_file = sys.argv[1]
pr_author = sys.argv[2]

with open(team_file, "rb") as f:
    data = tomllib.load(f)

leads = data.get("leads", [])
if pr_author not in leads:
    sys.exit(1)
PY
then
    echo "::error::Team creator must be listed as a lead in $TEAM_FILE"
    exit 1
fi

echo "Team creator membership validated"

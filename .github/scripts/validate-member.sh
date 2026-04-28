#!/bin/bash
set -e

PR_AUTHOR=$1
GITHUB_FILE=$2

# Extract GitHub username from TOML file name
GITHUB_USERNAME=$(basename "$GITHUB_FILE" .toml)

# Check if PR author matches GitHub username
if [[ "$GITHUB_USERNAME" != "$PR_AUTHOR" ]]; then
    echo "::error::Member file $GITHUB_FILE must be submitted by $GITHUB_USERNAME themselves, not by $PR_AUTHOR"
    exit 1
fi

echo "Self-nomination validated for $GITHUB_USERNAME"

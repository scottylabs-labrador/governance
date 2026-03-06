# 2. adopt hybrid synchronization strategy

Date: 2026-03-05

## Status

Accepted

## Context

The goal of the project is to automate the permission synchronizations.

## Decision

We adopt a hybrid synchronization strategy using both OpenTofu and Python scripts.

### OpenTofu

OpenTofu allows us to define the resources and their relationships in a declarative way.
This is the default synchronization strategy we are using.

### Python

Python is the second best tool for every job, including this one. The following
scenarios are when we will be using Python scripts instead of OpenTofu:

- When Labrador does not entirely own the resource (e.g. Slack, Google Drive, etc).

- When using Python scripts is more efficient and OpenTofu adds little value.
  For example, the `CODEOWNERS` file is generated and overwritten each time,
  so it is not worth the effort to use OpenTofu to manage it.

## Consequences

The hybrid synchronization strategy allows us to leverage the benefits of
both OpenTofu and Python scripts, utilizing the best tool for each job.

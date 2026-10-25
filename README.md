# DataDep Guard

A lightweight dataset dependency checker for machine-learning projects.

## Planned features
- Discover supported Hugging Face dataset references.
- Record immutable dataset revisions.
- Snapshot metadata and file manifests.
- Report upstream changes.
- Enforce configurable policies in CI.

## Status
Early development — Day 1. Dataset discovery, snapshot comparison, and CI checks are not implemented yet.

## Development
Requires Python 3.11 or later.

Install development dependencies:

    python -m pip install -e ".[dev]"

Run tests:

    python -m pytest

Check the CLI version:

    datadep-guard --version

## Limitations
This experimental project does not guarantee dataset immutability, data quality, licence compliance, or reproducibility.

## Research
See docs/SCOPE.md and docs/EXISTING_TOOLS.md.

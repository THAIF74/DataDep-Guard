# DataDep Guard — Project Scope

## Problem
Machine-learning projects may depend on datasets hosted outside their
repositories. When those datasets change, projects may consume different
files, metadata, or structures without the developer noticing.

## Proposed solution
A lightweight CLI that identifies supported dataset references, records
immutable revisions, compares snapshots, and reports changes according
to configurable policies.

## Initial scope
1. Discover supported Hugging Face dataset references.
2. Record repository IDs and immutable revisions.
3. Capture available metadata and file manifests.
4. Compare snapshots and explain detected changes.
5. Support configurable warnings and CI failure rules.

## Non-goals for the MVP
- Downloading entire datasets by default.
- Claiming metadata checks guarantee data quality.
- Automatically retraining models.
- Supporting every dataset hosting platform.
- Claiming uniqueness before comparing existing alternatives.

## Initial success criteria
- An unchanged pinned dataset passes its checks.
- A changed file manifest produces a clear report.
- Missing revision pins are reported.
- Policy violations produce predictable exit codes.
- Automated tests cover normal and failure cases.

## Current status
Day 1: project foundation and scope definition.
Dataset discovery and change detection are not implemented yet.

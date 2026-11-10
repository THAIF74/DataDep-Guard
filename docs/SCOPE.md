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

## Implemented status

All seven planned development milestones are implemented:

1. **Day 1 — Project foundation:** package structure and initial scope.
2. **Day 2 — Dataset dependency scanner:** validate the dataset configuration.
3. **Day 3 — Hugging Face revision checks:** check remote dataset revisions.
4. **Day 4 — Revision pinning:** resolve and save full commit SHA pins.
5. **Day 5 — Snapshot manifests:** record local file paths, sizes, and SHA-256 checksums.
6. **Day 6 — Dataset change detection:** compare manifests and report added, removed, modified, and unchanged files.
7. **Day 7 — Policy configuration and CI exit codes:** enforce configurable scan policies and return predictable exit codes for CI use.

## Verification status

The project owner reported a local test run on **November 4, 2026**:
**25 tests passed in 0.76 seconds** using Python 3.11.9.

A GitHub Actions workflow is being added to run the test suite automatically
on pushes and pull requests. The remote workflow result must be checked in
the GitHub Actions tab; a local passing test run does not prove that remote
CI has passed.

## Current limitations
- The tool checks public Hugging Face dataset revisions; remote checks require network access.
- Private or gated dataset authentication is not currently configured.
- Local manifests do not download datasets or verify their origin.
- SHA-256 checksums detect file-content differences between manifests; they do not establish dataset quality or correctness.
- The project does not guarantee dataset immutability, data quality, licence compliance, or complete reproducibility.
- This is an experimental developer tool, not a production compliance or security certification product.

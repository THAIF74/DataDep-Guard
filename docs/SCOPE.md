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

The first six development milestones are implemented:

1. **Day 1 — Project foundation:** package structure and initial scope.
2. **Day 2 — Dataset dependency scanner:** validate the dataset configuration.
3. **Day 3 — Hugging Face revision checks:** check remote dataset revisions.
4. **Day 4 — Revision pinning:** resolve and save full commit SHA pins.
5. **Day 5 — Snapshot manifests:** record local file paths, sizes, and SHA-256 checksums.
6. **Day 6 — Dataset change detection:** compare manifests and report added, removed, modified, and unchanged files.

The scanner and manifest comparison are implemented. Snapshot manifests describe
local files; they do not independently prove that those files came from the
declared remote revision.

## Remaining planned scope

The initial scope also mentions configurable warning policies and CI failure
rules. These are **not confirmed as implemented in the current six milestones**.

A possible Day 7 is to add policy configuration and predictable CLI exit codes
for policy violations, with tests for normal and failure cases. This should be
treated as the next proposed milestone, not as completed work.

## Current limitations
- The tool checks public Hugging Face dataset revisions; remote checks require network access.
- Private or gated dataset authentication is not currently configured.
- Local manifests do not download datasets or verify their origin.
- SHA-256 checksums detect file-content differences between manifests; they do not establish dataset quality or correctness.
- The project does not guarantee dataset immutability, data quality, licence compliance, or complete reproducibility.
- This is an experimental developer tool, not a production compliance or security certification product.

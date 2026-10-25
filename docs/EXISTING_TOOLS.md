# Existing Tools and Research

This is an initial comparison, not proof of originality.

## Hugging Face Hub
https://huggingface.co/docs/hub

Provides dataset repository revisions, metadata, and commit history.
Overlap: revision discovery and upstream change information.

## Apify
https://apify.com/

A related dataset-monitoring direction has been identified.
Its exact capabilities need further verification.

## DVC
https://dvc.org/doc

Provides data and ML pipeline versioning workflows.
Overlap: versioned data and reproducible ML workflows.

## Working differentiation hypothesis
DataDep Guard may provide a lightweight, project-aware CI gate that
connects declared dataset dependencies, pinned revisions, change reports,
and configurable build policies.

This hypothesis is NOT proven unique.

## Research still required
- Verify competitors' exact capabilities and current maintenance.
- Check whether existing tools already provide the complete workflow.
- Determine which dataset changes can be detected reliably.
- Define limitations for private and custom datasets.
- Revise the idea if existing tools already cover the proposed gap.

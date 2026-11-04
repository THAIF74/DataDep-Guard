# DataDep Guard

A lightweight Python tool for checking Hugging Face dataset dependencies and detecting changes between local dataset snapshots.

## Features

- Validate a `datadep.json` dataset dependency configuration.
- Check public Hugging Face dataset revisions.
- Pin unpinned dataset references to full commit SHAs.
- Generate local file manifests with file sizes and SHA-256 checksums.
- Compare two manifests and report added, removed, modified, and unchanged files.

## Requirements

- Python 3.11 or later
- Internet connection for Hugging Face revision checks and pinning
- `pytest` for running the test suite

## Installation

Clone the repository, create and activate a virtual environment, then install the project:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Configuration

Create a `datadep.json` file in the project directory:

```json
{
  "datasets": [
    {
      "source": "huggingface",
      "id": "ylecun/mnist",
      "revision": null
    }
  ]
}
```

Use a full 40-character commit SHA for a reproducible revision pin.

## CLI commands

Check the installed version:

```powershell
datadep-guard --version
```

Validate the configuration and check the remote dataset revision:

```powershell
datadep-guard scan
```

Pin datasets that do not yet have a revision:

```powershell
datadep-guard pin
```

Compare two previously generated manifest JSON files:

```powershell
datadep-guard compare snapshots\old-manifest.json snapshots\new-manifest.json
```

The comparison report identifies added, removed, modified, and unchanged file paths.

## Python API: create a local manifest

The manifest functions can be used from Python:

```python
from pathlib import Path
from datadep_guard.manifest import create_manifest, save_manifest

manifest = create_manifest(
    dataset_id="ylecun/mnist",
    revision="YOUR_40_CHARACTER_COMMIT_SHA",
    directory=Path("data/mnist"),
)
save_manifest(manifest, Path("snapshots/mnist-manifest.json"))
```

Replace the example revision with the actual commit SHA associated with the local dataset files. Generate a second manifest after updating the local dataset, then compare the two manifest files with the `compare` command.

## Run tests

```powershell
python -m pytest -v
```

## Current scope and limitations

- Snapshot manifests describe files in a local directory; they do not download datasets or independently prove that local files came from the declared Hugging Face revision.
- SHA-256 checksums detect file-content differences between manifests; they do not establish dataset quality or correctness.
- The project does not guarantee dataset immutability, data quality, licence compliance, or complete reproducibility.
- Remote revision checks require network access. Private or gated datasets may require additional authentication, which is not currently configured by this tool.
- This is an experimental developer tool, not a production compliance or security certification product.

## Project status

The initial six development milestones are implemented: configuration scanning, Hugging Face revision checks, revision pinning, local snapshot manifests, and manifest comparison.


# DataDep Guard

A lightweight Python tool for checking Hugging Face dataset dependencies and detecting changes between local dataset snapshots.

## Features

- Validate a `datadep.json` dataset dependency configuration.
- Check public Hugging Face dataset revisions.
- Pin unpinned dataset references to full commit SHAs.
- Generate local file manifests with file sizes and SHA-256 checksums using the Python API or CLI.
- Compare two manifests and report added, removed, modified, and unchanged files.

## Requirements

- Python 3.11 or later
- Internet connection for Hugging Face revision checks and pinning
- `pytest` for running the test suite

## Installation

Clone the repository, create and activate a virtual environment, then install the project.

**Windows PowerShell**

```powershell
git clone https://github.com/THAIF74/DataDep-Guard.git
cd DataDep-Guard
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

**Linux / macOS**

```bash
git clone https://github.com/THAIF74/DataDep-Guard.git
cd DataDep-Guard
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
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
  ],
  "policies": {
    "fail_on_unpinned": true,
    "fail_on_remote_error": true
  }
}
```

Use a full 40-character commit SHA for a reproducible revision pin.

## CLI commands

Check the installed version:

```bash
datadep-guard --version
```

Validate the configuration and check the remote dataset revision:

```bash
datadep-guard scan
```

Pin datasets that do not yet have a revision:

```bash
datadep-guard pin
```

Verify that a Hugging Face revision resolves correctly:

```bash
datadep-guard verify --dataset-id ylecun/mnist --revision YOUR_40_CHARACTER_COMMIT_SHA
```

For a full 40-character commit SHA, the command compares the requested SHA
with the commit SHA returned by Hugging Face. It reports `[VERIFIED]` when
they match and `[MISMATCH]` when they differ. Branches and tags are resolved
to their current commit, but are not immutable pins.

The command exits with:
- `0`: revision verified
- `1`: remote request failed or returned an invalid commit SHA
- `2`: invalid or missing command arguments
- `3`: requested full commit SHA does not match the resolved commit

Create a manifest directly from a local dataset folder:

```powershell
datadep-guard manifest `
  --dataset-id ylecun/mnist `
  --revision YOUR_40_CHARACTER_COMMIT_SHA `
  --directory .\data\mnist `
  --output .\snapshots\mnist-manifest.json
```

The command records each included file's relative path, size, and SHA-256 checksum.
It reads the local folder only; it does not download or upload dataset files.
Keep the output manifest outside the dataset folder.

Compare two previously generated manifest JSON files:

```bash
datadep-guard compare snapshots/old-manifest.json snapshots/new-manifest.json
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

Install the development dependency and run the test suite:

```bash
python -m pip install -e ".[dev]"
python -m pytest -v
```

GitHub Actions runs the test suite automatically on pushes and pull requests
using Python 3.11 and 3.12. Check the repository's **Actions** tab for the
latest remote CI result.

## Current scope and limitations

- Snapshot manifests describe files in a local directory; they do not download datasets or independently prove that local files came from the declared Hugging Face revision.
- SHA-256 checksums detect file-content differences between manifests; they do not establish dataset quality or correctness.
- The project does not guarantee dataset immutability, data quality, licence compliance, or complete reproducibility.
- Remote revision checks require network access. Private or gated datasets may require additional authentication, which is not currently configured by this tool.
- This is an experimental developer tool, not a production compliance or security certification product.

## Project status

The initial seven development milestones are implemented. The project owner
reported that 25 tests passed locally on November 4, 2026. Remote CI status is
shown in the GitHub Actions tab.

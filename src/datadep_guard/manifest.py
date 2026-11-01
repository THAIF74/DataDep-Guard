
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


IGNORED_DIRECTORIES = {
    "__pycache__",
    ".git",
    ".venv",
    ".pytest_cache",
}


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 checksum using chunks."""
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def create_manifest(dataset_id: str, revision: str, directory: Path) -> dict:
    """Create a manifest of dataset files."""
    directory = Path(directory)

    if not directory.is_dir():
        raise ValueError(f"Dataset directory does not exist: {directory}")

    files = []

    for file_path in sorted(directory.rglob("*")):
        relative_path = file_path.relative_to(directory)

        if not file_path.is_file():
            continue

        if any(part in IGNORED_DIRECTORIES for part in relative_path.parts):
            continue

        if file_path.suffix.lower() == ".pyc":
            continue

        files.append({
            "path": relative_path.as_posix(),
            "size": file_path.stat().st_size,
            "sha256": calculate_sha256(file_path),
        })

    return {
        "schema_version": 1,
        "dataset": dataset_id,
        "revision": revision,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "file_count": len(files),
        "files": files,
    }


def save_manifest(manifest: dict, output_path: Path) -> None:
    """Save manifest as formatted JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

import json
from pathlib import Path
def compare_manifests(old_manifest: dict, new_manifest: dict) -> dict:
    """Compare two dataset manifests and detect file changes."""
    old_files = {
        item["path"]: item
        for item in old_manifest.get("files", [])
    }
    new_files = {
        item["path"]: item
        for item in new_manifest.get("files", [])
    }
    old_paths = set(old_files)
    new_paths = set(new_files)
    added = sorted(new_paths - old_paths)
    removed = sorted(old_paths - new_paths)
    common = old_paths & new_paths
    modified = sorted(
        path for path in common
        if (
            old_files[path].get("sha256")
            != new_files[path].get("sha256")
        )
    )
    unchanged = sorted(common - set(modified))
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
        "status": (
            "CHANGES DETECTED"
            if added or removed or modified
            else "NO CHANGES"
        ),
    }
def compare_manifest_files(old_path: Path, new_path: Path) -> dict:
    """Load and compare two JSON manifest files."""
    old_manifest = json.loads(
        Path(old_path).read_text(encoding="utf-8")
    )
    new_manifest = json.loads(
        Path(new_path).read_text(encoding="utf-8")
    )
    return compare_manifests(old_manifest, new_manifest)
def print_comparison_report(result: dict) -> None:
    """Display a readable comparison report."""
    print("\nDataset Comparison Report")
    print("-" * 35)
    print(f"Added:       {len(result['added'])}")
    print(f"Removed:     {len(result['removed'])}")
    print(f"Modified:    {len(result['modified'])}")
    print(f"Unchanged:   {len(result['unchanged'])}")
    print("-" * 35)
    print(f"Status: {result['status']}")

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from datadep_guard import __version__
from datadep_guard.compare import (
    compare_manifest_files,
    print_comparison_report,
)
from datadep_guard.manifest import create_manifest, save_manifest


def fetch_dataset_info(dataset_id: str, revision: str | None = None) -> dict:
    """Fetch public Hugging Face dataset metadata."""
    url = "https://huggingface.co/api/datasets/" + quote(dataset_id, safe="/")
    if revision:
        url += "?" + urlencode({"revision": revision})

    request = Request(url, headers={"User-Agent": "DataDep-Guard/0.1.0"})

    try:
        with urlopen(request, timeout=10) as response:
            info = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(
            f"Hugging Face returned HTTP {exc.code}; check the dataset ID "
            "and revision, and whether access is required."
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"Network error contacting Hugging Face: {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError("Hugging Face request timed out.") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Hugging Face returned invalid JSON.") from exc

    if not isinstance(info, dict) or not isinstance(info.get("sha"), str):
        raise RuntimeError("Dataset response did not contain a commit SHA.")

    return info



def load_config(path: Path):
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: Cannot read configuration: {exc}", file=sys.stderr)
        return None
    if not isinstance(config, dict) or not isinstance(config.get("datasets"), list):
        print("ERROR: Configuration must contain a 'datasets' list.", file=sys.stderr)
        return None
    for index, dataset in enumerate(config["datasets"]):
        if not isinstance(dataset, dict):
            print(f"ERROR: Dataset {index + 1} must be an object.", file=sys.stderr)
            return None
        if dataset.get("source") != "huggingface":
            print(f"ERROR: Dataset {index + 1}: invalid source.", file=sys.stderr)
            return None
        if not isinstance(dataset.get("id"), str) or not dataset["id"].strip():
            print(f"ERROR: Dataset {index + 1}: missing dataset id.", file=sys.stderr)
            return None
        revision = dataset.get("revision")
        if revision is not None and (
            not isinstance(revision, str) or not revision.strip()
        ):
            print(f"ERROR: Dataset {index + 1}: invalid revision.", file=sys.stderr)
            return None
    return config


def scan_config(path: Path) -> int:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: Cannot read configuration: {exc}", file=sys.stderr)
        return 2

    if not isinstance(config, dict) or not isinstance(config.get("datasets"), list):
        print("ERROR: Configuration must contain a 'datasets' list.", file=sys.stderr)
        return 2

    datasets = config["datasets"]
    policies = config.get("policies", {})
    if not isinstance(policies, dict):
        print("ERROR: 'policies' must be an object.", file=sys.stderr)
        return 2
    for key in ("fail_on_unpinned", "fail_on_remote_error"):
        if key in policies and not isinstance(policies[key], bool):
            print(f"ERROR: Policy '{key}' must be true or false.", file=sys.stderr)
            return 2
    fail_on_unpinned = policies.get("fail_on_unpinned", False)
    fail_on_remote_error = policies.get("fail_on_remote_error", True)
    errors = []

    for index, dataset in enumerate(datasets):
        if not isinstance(dataset, dict):
            errors.append(f"Dataset {index + 1} must be an object.")
            continue

        source = dataset.get("source")
        dataset_id = dataset.get("id")
        revision = dataset.get("revision")

        if source != "huggingface":
            errors.append(f"Dataset {index + 1}: source must be 'huggingface'.")
        if not isinstance(dataset_id, str) or not dataset_id.strip():
            errors.append(f"Dataset {index + 1}: missing dataset id.")
        if revision is not None and (
            not isinstance(revision, str) or not revision.strip()
        ):
            errors.append(
                f"Dataset {index + 1}: revision must be a non-empty string or null."
            )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(f"DataDep Guard: checking {len(datasets)} dataset(s) on Hugging Face.")
    failures = 0
    unpinned = 0

    for dataset in datasets:
        dataset_id = dataset["id"]
        revision = dataset.get("revision")

        try:
            info = fetch_dataset_info(dataset_id, revision)
        except Exception as exc:
            print(f"[ERROR] {dataset_id}: {exc}")
            failures += 1
            continue

        resolved_sha = info["sha"]

        if revision:
            print(f"[PINNED] {dataset_id}")
            print(f"         Requested revision: {revision}")
            print(f"         Resolved commit: {resolved_sha}")
            print("         Revision exists on Hugging Face.")
            print("         For reproducibility, prefer a full commit SHA.")
        else:
            unpinned += 1
            print(f"[UNPINNED] {dataset_id}")
            print(f"           Latest remote commit: {resolved_sha}")
            print("           WARNING: Add this commit SHA to datadep.json to pin it.")

    print(
        f"Remote check complete: {len(datasets) - failures} successful, "
        f"{failures} failed."
    )
    if failures and fail_on_remote_error:
        return 1
    if unpinned and fail_on_unpinned:
        print(
            f"POLICY VIOLATION: {unpinned} unpinned dataset(s); "
            "pin them or change policies.fail_on_unpinned."
        )
        return 3
    if failures:
        print("WARNING: Remote errors were allowed by policy.")
    return 0



def is_full_sha(value: str) -> bool:
    import re
    return bool(re.fullmatch(r"[0-9a-fA-F]{40}", value))
def pin_config(path: Path) -> int:
    config = load_config(path)
    if config is None:
        return 2
    pending = []
    for dataset in config["datasets"]:
        if dataset.get("revision") is not None:
            print(f"[ALREADY PINNED] {dataset['id']}")
            continue
        try:
            info = fetch_dataset_info(dataset["id"])
            sha = info["sha"]
            if not is_full_sha(sha):
                raise RuntimeError("Invalid commit SHA returned by Hugging Face.")
            pending.append((dataset, sha))
            print(f"[READY] {dataset['id']}: {sha}")
        except Exception as exc:
            print(f"[ERROR] {dataset['id']}: {exc}")
            print("Pinning cancelled. Configuration was not changed.")
            return 1
    if not pending:
        print("All datasets are already pinned. No changes made.")
        return 0
    for dataset, sha in pending:
        dataset["revision"] = sha
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"Successfully pinned {len(pending)} dataset(s) in {path}.")
    return 0


def create_manifest_command(dataset_id: str, revision: str, directory: Path, output: Path) -> int:
    """Create and save a SHA-256 manifest for a local dataset directory."""
    try:
        manifest = create_manifest(dataset_id, revision, directory)
        save_manifest(manifest, output)
    except (OSError, ValueError) as exc:
        print(f"ERROR: Manifest creation failed: {exc}", file=sys.stderr)
        return 2

    print(f"Created manifest for {dataset_id} ({manifest['file_count']} files).")
    print(f"Revision: {revision}")
    print(f"Output: {output}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if args == ["--version"]:
        print(f"datadep-guard {__version__}")
        return 0

    parser = argparse.ArgumentParser(
        prog="datadep-guard",
        description="Inspect dataset dependencies on Hugging Face.",
    )
    commands = parser.add_subparsers(dest="command")
    compare_parser = commands.add_parser(
        "compare",
        help="Compare two dataset manifests"
    )
    compare_parser.add_argument("old_manifest")
    compare_parser.add_argument("new_manifest")
    compare_parser.add_argument(
        "--fail-on-changes",
        action="store_true",
        help="Return exit code 3 when the manifests contain changes (useful in CI)",
    )
    scan_parser = commands.add_parser(
        "scan", help="Validate configuration and check remote dataset revisions"
    )
    scan_parser.add_argument(
        "config", nargs="?", default="datadep.json",
        help="Configuration file (default: datadep.json)",
    )

    manifest_parser = commands.add_parser(
        "manifest", help="Create a SHA-256 manifest for a local dataset directory"
    )
    manifest_parser.add_argument("--dataset-id", required=True, help="Dataset identifier")
    manifest_parser.add_argument("--revision", required=True, help="Dataset commit or revision")
    manifest_parser.add_argument("--directory", required=True, help="Local dataset directory")
    manifest_parser.add_argument("--output", required=True, help="Path for the output JSON manifest")

    pin_parser = commands.add_parser("pin", help="Pin unpinned datasets")
    pin_parser.add_argument(
        "config", nargs="?", default="datadep.json",
        help="Configuration file (default: datadep.json)",
    )
    if not args:
        parser.print_help()
        return 0

    parsed = parser.parse_args(args)

    if parsed.command == "scan":
        return scan_config(Path(parsed.config))
    if parsed.command == "pin":
        return pin_config(Path(parsed.config))
    if parsed.command == "manifest":
        if not parsed.dataset_id.strip() or not parsed.revision.strip():
            parser.error("--dataset-id and --revision must not be empty")
        return create_manifest_command(
            parsed.dataset_id,
            parsed.revision,
            Path(parsed.directory),
            Path(parsed.output),
        )
    if parsed.command == "compare":
        try:
            result = compare_manifest_files(
                Path(parsed.old_manifest),
                Path(parsed.new_manifest),
            )
            print_comparison_report(result)
            if parsed.fail_on_changes and result["status"] == "CHANGES DETECTED":
                print("POLICY VIOLATION: manifest changes detected.")
                return 3
            return 0
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"ERROR: Comparison failed: {exc}", file=sys.stderr)
            return 2

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

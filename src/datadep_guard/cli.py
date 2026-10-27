import argparse
import json
import sys
from pathlib import Path

from datadep_guard import __version__


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
            errors.append(f"Dataset {index + 1}: revision must be a non-empty string or null.")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(f"DataDep Guard: {len(datasets)} dataset(s) found.")

    for dataset in datasets:
        revision = dataset.get("revision")
        status = "PINNED" if revision else "UNPINNED"
        print(f"[{status}] {dataset['id']}")
        if revision:
            print(f"         Revision: {revision}")
        else:
            print("         WARNING: No revision specified.")

    print("Scan complete. No remote dataset changes were checked.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if args == ["--version"]:
        print(f"datadep-guard {__version__}")
        return 0

    parser = argparse.ArgumentParser(
        prog="datadep-guard",
        description="Inspect declared dataset dependencies."
    )
    commands = parser.add_subparsers(dest="command")
    scan_parser = commands.add_parser("scan", help="Validate dataset references")
    scan_parser.add_argument(
        "config", nargs="?", default="datadep.json",
        help="Configuration file (default: datadep.json)"
    )

    if not args:
        parser.print_help()
        return 0

    parsed = parser.parse_args(args)

    if parsed.command == "scan":
        return scan_config(Path(parsed.config))

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Command-line entry point for DataDep Guard."""

import argparse
from datadep_guard import __version__


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="datadep-guard",
        description="Check dataset dependencies in ML projects.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.parse_args()


if __name__ == "__main__":
    main()

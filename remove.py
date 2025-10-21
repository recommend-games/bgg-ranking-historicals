#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

"""Remove files shorter than the previous file and duplicates in a directory."""

import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def remove_and_deduplicate(
    *,
    in_dir: str | Path,
    glob: str | None = None,
    tolerance: float = 1.0,
    deduplicate: bool = True,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Remove files shorter than the previous file and duplicates in a directory."""

    assert 0 <= tolerance <= 1, "Tolerance must be in the range [0, 1]"

    in_dir = Path(in_dir).resolve()
    LOGGER.info(
        "Removing files shorter than the previous file in <%s> with a tolerance of %.1f%%",
        in_dir,
        tolerance * 100,
    )
    if deduplicate:
        LOGGER.info("Deduplicate identical files")

    prev_count = 0
    prev_content = ""
    removed_short = 0
    removed_duplicates = 0

    paths = in_dir.glob(glob) if glob else in_dir.iterdir()

    for path in sorted(paths):
        with path.open("r") as file:
            curr_count = sum(1 for _ in file)

        if curr_count < prev_count * tolerance:
            LOGGER.info(
                "File <%s> is shorter (%d lines) than the previous file (%d lines), removing",
                path.name,
                curr_count,
                prev_count,
            )
            if dry_run:
                print(path)
            else:
                path.unlink()
            removed_short += 1
            continue

        prev_count = max(prev_count, curr_count)

        if not deduplicate:
            continue

        with path.open("r") as file:
            curr_content = file.read()

        if curr_content == prev_content:
            LOGGER.info(
                "File <%s> is identical to the previous file, removing",
                path.name,
            )
            if dry_run:
                print(path)
            else:
                path.unlink()
            removed_duplicates += 1
        prev_content = curr_content

    return removed_short, removed_duplicates


def _arg_parse():
    parser = ArgumentParser(
        description="Remove files shorter than the previous file and duplicates",
    )
    parser.add_argument(
        "in_dir",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)",
    )
    parser.add_argument(
        "-g",
        "--glob",
        default="*.csv",
        help="Glob pattern to match files (default: '*.csv')",
    )
    parser.add_argument(
        "-t",
        "--tolerance",
        type=float,
        default=0.98,
        help="Tolerance factor for file length (default: 0.98)",
    )
    parser.add_argument(
        "-d",
        "--deduplicate",
        action="store_true",
        help="Remove duplicate files",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Do not remove files, only print them",
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    args = _arg_parse()
    remove_and_deduplicate(
        in_dir=args.in_dir,
        glob=args.glob,
        tolerance=args.tolerance,
        deduplicate=args.deduplicate,
        dry_run=args.dry_run,
    )

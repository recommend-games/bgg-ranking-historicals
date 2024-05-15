#!/usr/bin/env python3

"""Remove files shorter than the previous file in a directory."""

import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def remove_short_files(
    *,
    in_dir: str | Path,
    glob: str = "*.csv",
    tolerance: float = 1.0,
    dry_run: bool = False,
) -> int:
    """Remove files shorter than the previous file in a directory."""

    in_dir = Path(in_dir).resolve()
    LOGGER.info("Removing files shorter than the previous file in <%s>…", in_dir)

    prev = 0
    removed = 0

    for path in sorted(in_dir.glob(glob)):
        with path.open("r") as file:
            curr = sum(1 for _ in file)
        if curr < prev * tolerance:
            LOGGER.info(
                "File <%s> is shorter (%d lines) than the previous file (%d lines), removing…",
                path.name,
                curr,
                prev,
            )
            if dry_run:
                print(path)
            else:
                path.unlink()
            removed += 1
        prev = max(prev, curr)

    return removed


def _arg_parse():
    parser = ArgumentParser(description="Remove files shorter than the previous file")
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
        "-n",
        "--dry-run",
        action="store_true",
        help="Do not remove files, only print them",
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    args = _arg_parse()
    remove_short_files(
        in_dir=args.in_dir,
        glob=args.glob,
        tolerance=args.tolerance,
        dry_run=args.dry_run,
    )

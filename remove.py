#!/usr/bin/env python3

"""Remove files shorter than the previous file in a directory."""

import logging
import sys
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
                path,
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    remove_short_files(in_dir=".", dry_run=True, tolerance=0.98)

#!/usr/bin/env python

"""Rename the files in a repo to match the earliest commit on Git."""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from git import Repo
from pytility import parse_date

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATE_FORMAT = "%Y-%m-%dT%H-%M-%S"
FILE_GLOB = "20[0-9][0-9]-[0-1][0-9]-[0-3][0-9].csv"


def first_commit_date(repo: Repo, path_file: Path) -> Optional[datetime]:
    """Find the first commit date of a given file."""

    git = repo.git()
    log = git.log("--reverse", "--date-order", "--pretty=format:%aI", "--", path_file)
    if not log:
        return None
    date_iso = next(iter(log.split("\n", 1)), None)
    return parse_date(date_iso) or None


def rename_file(
    repo: Repo,
    path_file: Path,
    strict: bool = True,
    dry_run: bool = False,
) -> None:
    """Rename the given file to match the earliest commit on Git."""

    date = first_commit_date(repo, path_file)
    date_str = date.strftime(DATE_FORMAT)

    if strict and date_str[:10] != path_file.stem:
        LOGGER.error(
            "Dates of file <%s> and Git commit <%s> do not match, skipping…",
            path_file.stem,
            date_str,
        )
        return

    new_file_name = f"{date_str}.csv"
    new_path_file = path_file.parent / new_file_name

    LOGGER.info("Moving <%s> to <%s>…", path_file, new_path_file)

    if not dry_run:
        repo.git().mv(path_file, new_path_file)
        repo.index.commit(f"{path_file.name} -> {new_file_name}")


def rename_files(path_dir: Path, strict: bool = True, dry_run: bool = False) -> None:
    """Rename the files in a repo to match the earliest commit on Git."""

    path_dir = Path(path_dir).resolve()
    repo = Repo(path_dir)

    for path_file in sorted(path_dir.glob(FILE_GLOB)):
        rename_file(repo=repo, path_file=path_file, strict=strict, dry_run=dry_run)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Rename the files in a repo to match the earliest commit on Git."
    )
    parser.add_argument("--repo", "-r", default=BASE_DIR, help="The repo to process")
    parser.add_argument(
        "--non-strict",
        "-S",
        action="store_true",
        help="Don't be strict about renaming if the dates don't match",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Dry run, don't actually change anything",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="log level (repeat for more verbosity)",
    )

    return parser.parse_args()


def main():
    """CLI entry point."""

    args = _parse_args()

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG if args.verbose > 0 else logging.INFO,
        format="%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s",
    )

    LOGGER.info(args)

    path_dir = Path(args.repo).resolve()

    rename_files(path_dir=path_dir, strict=not args.non_strict, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

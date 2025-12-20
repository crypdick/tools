#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click>=8.1.0",
#     "rich>=13.0.0",
# ]
# ///
"""
Find and delete duplicate files between two directories.
"""

import hashlib
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import click
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
)


def compare_files(old_path: str, new_path: str) -> bool | None:
    """
    Compare two files for equality.

    Returns True if identical, False if different, None if new_path doesn't exist.
    """
    if not os.path.exists(new_path):
        return None

    old_stat = os.stat(old_path)
    new_stat = os.stat(new_path)

    if old_stat.st_size != new_stat.st_size:
        return False

    # For large files (>10MB), sample at start, middle, and end
    if old_stat.st_size > 10 * 1024 * 1024:
        positions = [0, old_stat.st_size // 2, max(0, old_stat.st_size - 65536)]
        for pos in positions:
            with open(old_path, "rb") as f1, open(new_path, "rb") as f2:
                f1.seek(pos)
                f2.seek(pos)
                if f1.read(65536) != f2.read(65536):
                    return False
        return True

    # For smaller files, compare MD5 hashes
    def md5(path: str) -> str:
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    return md5(old_path) == md5(new_path)


def process_file(
    args: tuple[str, str, str, bool],
) -> tuple[str, str, str | None]:
    """Process a single file comparison."""
    rel_path, old_base, new_base, do_delete = args
    old_path = os.path.join(old_base, rel_path)
    new_path = os.path.join(new_base, rel_path)

    try:
        result = compare_files(old_path, new_path)
        if result is True:
            if do_delete:
                os.remove(old_path)
            return ("DELETED" if do_delete else "IDENTICAL", rel_path, None)
        elif result is False:
            return ("DIFFERS", rel_path, None)
        else:
            return ("NOT_IN_NEW", rel_path, None)
    except Exception as e:
        return ("ERROR", rel_path, str(e))


@click.command()
@click.argument("old_dir", type=click.Path(exists=True))
@click.argument("new_dir", type=click.Path(exists=True))
@click.option(
    "--delete",
    is_flag=True,
    help="Actually delete identical files (default is dry run).",
)
@click.option(
    "--workers", "-w", type=int, default=8, help="Number of parallel workers."
)
def main(old_dir: str, new_dir: str, delete: bool, workers: int) -> None:
    """
    Find duplicate files between OLD_DIR and NEW_DIR, optionally deleting from OLD_DIR.

    Compares files by path and content. For large files (>10MB), uses sampling
    for speed. For smaller files, compares MD5 hashes. Runs in parallel for
    performance on large directory trees.

    Without --delete, runs in dry-run mode showing what would be deleted.
    With --delete, removes identical files from OLD_DIR and cleans up empty directories.

    Arguments:
        OLD_DIR: Source directory to deduplicate (files deleted from here).
        NEW_DIR: Reference directory to compare against (untouched).

    Examples:

        # Dry run - see what would be deleted
        uv run https://tools.ricardodecal.com/python/dedup_dirs.py ~/old-backup ~/new-backup

        # Actually delete duplicates
        uv run https://tools.ricardodecal.com/python/dedup_dirs.py ~/old-backup ~/new-backup --delete

        # Use more workers for faster processing
        uv run https://tools.ricardodecal.com/python/dedup_dirs.py ~/old ~/new --delete -w 16
    """
    console = Console()
    old_base = str(Path(old_dir).expanduser().resolve())
    new_base = str(Path(new_dir).expanduser().resolve())

    mode = (
        "[bold red]DELETE MODE[/bold red]"
        if delete
        else "[bold yellow]DRY RUN[/bold yellow]"
    )
    console.print(f"=== {mode} ===")
    console.print(f"Old: {old_base}")
    console.print(f"New: {new_base}\n")

    # Scan files
    console.print("Scanning files...")
    files: list[tuple[str, str, str, bool]] = []
    for root, _, filenames in os.walk(old_base):
        for f in filenames:
            rel = os.path.relpath(os.path.join(root, f), old_base)
            files.append((rel, old_base, new_base, delete))
    console.print(f"Found {len(files)} files\n")

    if not files:
        console.print("[yellow]No files to process.[/yellow]")
        return

    stats: dict[str, int] = {
        "DELETED": 0,
        "IDENTICAL": 0,
        "DIFFERS": 0,
        "NOT_IN_NEW": 0,
        "ERROR": 0,
    }
    problems: list[tuple[str, str, str | None]] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Processing files", total=len(files))

        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(process_file, f) for f in files]
            for future in as_completed(futures):
                status, rel_path, error = future.result()
                stats[status] += 1
                if status in ("DIFFERS", "NOT_IN_NEW", "ERROR"):
                    problems.append((status, rel_path, error))
                progress.advance(task)

    # Summary
    console.print(f"\n{'=' * 50}")
    ok_count = stats.get("DELETED", 0) + stats.get("IDENTICAL", 0)
    console.print(f"[green]OK (identical):[/green] {ok_count}")
    console.print(f"[yellow]DIFFERS:[/yellow]        {stats['DIFFERS']}")
    console.print(f"[yellow]NOT_IN_NEW:[/yellow]     {stats['NOT_IN_NEW']}")
    console.print(f"[red]ERRORS:[/red]          {stats['ERROR']}")

    if problems:
        console.print("\n[bold]Problem files (kept):[/bold]")
        for status, path, error in problems[:20]:
            error_msg = f" - {error}" if error else ""
            console.print(f"  [{status}] {path}{error_msg}")
        if len(problems) > 20:
            console.print(f"  ... and {len(problems) - 20} more")

    if delete:
        console.print("\nCleaning empty directories...")
        cleaned = 0
        for root, dirs, _ in os.walk(old_base, topdown=False):
            for d in dirs:
                try:
                    os.rmdir(os.path.join(root, d))
                    cleaned += 1
                except OSError:
                    pass
        console.print(f"Removed {cleaned} empty directories")
    else:
        console.print(
            "\n[dim]Dry run complete. Use --delete to remove identical files.[/dim]"
        )


if __name__ == "__main__":
    main()

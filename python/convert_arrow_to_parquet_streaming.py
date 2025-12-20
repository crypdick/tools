#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# category = "data"
# dependencies = [
#     "typer>=0.15.0",
#     "rich>=13.0.0",
#     "pyarrow",
# ]
# ///

"""
Convert .arrow shards to Parquet without loading entire dataset into memory.
"""

import glob
import os
import sys
from pathlib import Path
from typing import Annotated

import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.parquet as pq
import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn


def find_arrow_files(source_dir: str) -> list[str]:
    """Find all .arrow files in the source directory recursively."""
    pattern = os.path.join(source_dir, "**", "*.arrow")
    return sorted(glob.glob(pattern, recursive=True))


def convert_arrow_to_parquet(source_path: str, dest_path: str) -> None:
    """Convert a single .arrow file into a .parquet file using streaming batches.

    This tries File format first, then falls back to Stream format.
    """
    Path(os.path.dirname(dest_path)).mkdir(parents=True, exist_ok=True)

    with pa.memory_map(source_path, "r") as in_stream:
        writer = None
        try:
            reader = ipc.open_file(in_stream)
            schema = reader.schema
            writer = pq.ParquetWriter(dest_path, schema)
            for i in range(reader.num_record_batches):
                batch = reader.get_batch(i)
                writer.write_batch(batch)
        except pa.lib.ArrowInvalid:
            in_stream.seek(0)
            reader = ipc.open_stream(in_stream)
            schema = reader.schema
            writer = pq.ParquetWriter(dest_path, schema)
            for batch in reader:
                writer.write_batch(batch)
        finally:
            if writer is not None:
                writer.close()


def main(
    source_dir: Annotated[
        Path,
        typer.Option(
            "--source-dir",
            help="Directory containing .arrow files",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Directory to write .parquet files",
            file_okay=False,
            dir_okay=True,
            writable=True,
            resolve_path=True,
        ),
    ] = Path("parq_convert"),
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", help="Overwrite existing parquet files"),
    ] = False,
    preserve_subdirs: Annotated[
        bool,
        typer.Option(
            "--preserve-subdirs",
            help="Preserve input subdirectory structure inside output dir",
        ),
    ] = False,
) -> None:
    """
    Convert Arrow shards to Parquet.

    - Discovers all .arrow files under a given source directory
    - Converts each file to Parquet
    - Uses streaming in order to keep memory bounded and convert files larger than available RAM
    - Handles both Arrow IPC File and Stream formats (tries file, falls back to stream)

    Notes:
    - Use --preserve-subdirs to mirror the input directory tree under the output dir.
    - Use --overwrite to re-create files; otherwise existing outputs are skipped.

    Arguments:
        SOURCE_DIR: Directory containing .arrow files.
        OUTPUT_DIR: Directory to write .parquet files.

    Examples:

        uv run python/convert_arrow_to_parquet_streaming.py --source-dir ./arrow_data --output-dir ./parquet_data

        uv run python/convert_arrow_to_parquet_streaming.py --source-dir ./arrow_data --output-dir ./parquet_data --preserve-subdirs
    """
    source_dir_str = str(source_dir)
    output_dir_str = str(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    arrow_files = find_arrow_files(source_dir_str)
    if not arrow_files:
        print(f"[red]No .arrow files found under {source_dir_str}[/red]", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(arrow_files)} .arrow files under {source_dir_str}")

    converted_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
    ) as progress:
        task = progress.add_task("Converting files", total=len(arrow_files))

        for arrow_path in arrow_files:
            arrow_path = os.path.abspath(arrow_path)
            if preserve_subdirs:
                rel = os.path.relpath(arrow_path, source_dir_str)
                parquet_path = os.path.join(
                    output_dir_str, os.path.splitext(rel)[0] + ".parquet"
                )
            else:
                parquet_name = (
                    os.path.splitext(os.path.basename(arrow_path))[0] + ".parquet"
                )
                parquet_path = os.path.join(output_dir_str, parquet_name)

            if os.path.exists(parquet_path) and not overwrite:
                print(f"[dim]Skip (exists): {parquet_path}[/dim]")
                progress.advance(task)
                continue

            try:
                convert_arrow_to_parquet(arrow_path, parquet_path)
                converted_count += 1
            except Exception as exc:
                print(
                    f"[red]ERROR converting {arrow_path}: {exc}[/red]",
                    file=sys.stderr,
                )

            progress.advance(task)

    print(
        f"Done. Converted {converted_count}/{len(arrow_files)} files into {output_dir_str}"
    )


if __name__ == "__main__":
    typer.run(main)

#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
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

import click
import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.parquet as pq


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


@click.command()
@click.option(
    "--source-dir",
    required=True,
    help="Directory containing .arrow files",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
)
@click.option(
    "--output-dir",
    default="parq_convert",
    help="Directory to write .parquet files",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite existing parquet files",
)
@click.option(
    "--preserve-subdirs",
    is_flag=True,
    help="Preserve input subdirectory structure inside output dir",
)
def main(
    source_dir: str, output_dir: str, overwrite: bool, preserve_subdirs: bool
) -> None:
    """
    Convert Arrow shards to Parquet.

    - Discovers all .arrow files under a given source directory
    - Converts each file to Parquet
    - Uses streaming in order to keep memory bounded and convert files larger than available RAM
    - Handles both Arrow IPC File and Stream formats (tries file, falls back to stream)

    Notes:
    - Use `--preserve-subdirs` to mirror the input directory tree under the output dir.
    - Use `--overwrite` to re-create files; otherwise existing outputs are skipped.

    \b
    Arguments:
        SOURCE_DIR: Directory containing .arrow files.
        OUTPUT_DIR: Directory to write .parquet files.

    Examples:

    \b
        uv run python/convert_arrow_to_parquet_streaming.py --source-dir ./arrow_data --output-dir ./parquet_data
        uv run python/convert_arrow_to_parquet_streaming.py --source-dir ./arrow_data --output-dir ./parquet_data --preserve-subdirs
    """
    source_dir = os.path.abspath(os.path.expanduser(source_dir))
    output_dir = os.path.abspath(os.path.expanduser(output_dir))
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    arrow_files = find_arrow_files(source_dir)
    if not arrow_files:
        click.echo(f"No .arrow files found under {source_dir}", err=True)
        sys.exit(1)

    click.echo(f"Found {len(arrow_files)} .arrow files under {source_dir}")

    converted_count = 0
    with click.progressbar(arrow_files, label="Converting files") as bar:
        for arrow_path in bar:
            arrow_path = os.path.abspath(arrow_path)
            if preserve_subdirs:
                rel = os.path.relpath(arrow_path, source_dir)
                parquet_path = os.path.join(
                    output_dir, os.path.splitext(rel)[0] + ".parquet"
                )
            else:
                parquet_name = (
                    os.path.splitext(os.path.basename(arrow_path))[0] + ".parquet"
                )
                parquet_path = os.path.join(output_dir, parquet_name)

            if os.path.exists(parquet_path) and not overwrite:
                click.echo(f"Skip (exists): {parquet_path}")
                continue

            try:
                convert_arrow_to_parquet(arrow_path, parquet_path)
                # We can't easily print per-file stats inside the progress bar without messing it up
                # but we could verify if needed.
                # pf = pq.ParquetFile(parquet_path)
                converted_count += 1
            except Exception as exc:
                click.echo(
                    f"ERROR converting {arrow_path}: {exc}",
                    err=True,
                )

    click.echo(
        f"Done. Converted {converted_count}/{len(arrow_files)} files into {output_dir}"
    )


if __name__ == "__main__":
    main()

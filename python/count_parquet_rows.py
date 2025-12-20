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
Count rows in a parquet dataset (local or S3) using metadata headers.
"""

import os
from typing import Annotated

import pyarrow.dataset as ds
import typer
from rich import print


def main(
    dataset_path: Annotated[str, typer.Argument(help="Local file path or S3 URI.")],
) -> None:
    """
    Count the number of rows in a parquet file/dataset without reading data into memory.

    Works by reading just the metadata headers. Supports:
    - Single parquet files
    - Directories of parquet shards
    - Hive-style partitioned datasets
    - Local paths and S3 URIs

    Arguments:
        DATASET_PATH: Local file path or S3 URI to the parquet dataset.

    Examples:

        # Local file
        uv run https://tools.ricardodecal.com/python/count_parquet_rows.py ./data.parquet

        # Directory of shards
        uv run https://tools.ricardodecal.com/python/count_parquet_rows.py ./data_dir/

        # S3 URI
        uv run https://tools.ricardodecal.com/python/count_parquet_rows.py s3://my-bucket/data.parquet
    """
    try:
        # Expand user path (~) if it's a local path
        if not dataset_path.startswith("s3://"):
            dataset_path = os.path.expanduser(dataset_path)

        dataset = ds.dataset(dataset_path, format="parquet")
        row_count = sum(
            row_group.num_rows
            for fragment in dataset.get_fragments()
            for row_group in fragment.row_groups
        )
        print(row_count)
    except Exception as e:
        print(f"[bold red]Error:[/bold red] Failed to count rows: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)

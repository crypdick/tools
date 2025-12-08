#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "pikepdf",
# ]
# ///
"""
Strip metadata from a single PDF file.
"""

import sys
from pathlib import Path

import click
import pikepdf


def strip_metadata(src: Path, dst: Path) -> None:
    """Strip metadata from a PDF file."""
    try:
        with pikepdf.open(src) as pdf:
            root = pdf.trailer.get("/Root")
            if root and "/Metadata" in root:
                del root["/Metadata"]

            info = pdf.trailer.get("/Info")
            if info:
                for k in list(info.keys()):
                    del info[k]
                del pdf.trailer["/Info"]

            pdf.save(dst)
            click.echo(f"Successfully stripped metadata: {src} -> {dst}")
    except Exception as e:
        click.echo(f"Error stripping metadata from '{src}': {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument(
    "input_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.argument(
    "output_file",
    type=click.Path(writable=True, dir_okay=False, path_type=Path),
    required=False,
)
def main(input_file: Path, output_file: Path | None) -> None:
    """
    Strip metadata from a PDF file.

    If OUTPUT_FILE is not provided, writes to 'stripped_<INPUT_FILE>'.
    """
    if output_file is None:
        output_file = input_file.with_name(f"stripped_{input_file.name}")

    strip_metadata(input_file, output_file)


if __name__ == "__main__":
    main()

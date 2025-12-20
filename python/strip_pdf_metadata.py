#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# category = "data"
# dependencies = [
#     "typer>=0.15.0",
#     "rich>=13.0.0",
#     "pikepdf",
# ]
# ///
"""
Strip metadata from a single PDF file.
"""

import sys
from pathlib import Path
from typing import Annotated

import pikepdf
import typer
from rich import print


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
            print(f"[green]Successfully stripped metadata:[/green] {src} -> {dst}")
    except Exception as e:
        print(f"[bold red]Error:[/bold red] stripping metadata from '{src}': {e}")
        sys.exit(1)


def main(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input PDF file.",
            exists=True,
            dir_okay=False,
            resolve_path=True,
        ),
    ],
    output_file: Annotated[
        Path | None,
        typer.Argument(
            help="Output PDF file. Defaults to 'stripped_<INPUT_FILE>'.",
            dir_okay=False,
            resolve_path=True,
        ),
    ] = None,
) -> None:
    """
    Strip metadata from a PDF file.

    If OUTPUT_FILE is not provided, writes to 'stripped_<INPUT_FILE>'.
    """
    if output_file:
        dst = output_file
    else:
        dst = input_file.with_name(f"stripped_{input_file.name}")

    strip_metadata(input_file, dst)


if __name__ == "__main__":
    typer.run(main)

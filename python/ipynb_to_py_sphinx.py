#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# category = "dev"
# dependencies = [
#     "typer>=0.15.0",
#     "rich>=13.0.0",
#     "pypandoc>=1.13",
# ]
# ///
"""
Convert a Jupyter notebook to a Sphinx Gallery Python script.
"""

import json
import re
from pathlib import Path
from typing import Annotated

import pypandoc
import typer
from rich import print


def convert_cell_to_rst(source: list[str]) -> str:
    """Convert markdown source lines to RST."""
    md_source = "".join(source)
    try:
        # Handle potential Windows line endings issue mentioned in gist comments
        rst = pypandoc.convert_text(md_source, "rst", format="md").replace("\r", "")
        # Use Sphinx-specific code-block directive instead of generic code directive
        return rst.replace(".. code::", ".. code-block::")
    except OSError as e:
        if "No pandoc was found" in str(e) or "pandoc: not found" in str(e):
            print(
                "[bold red]Error:[/bold red] Pandoc not found. Please install pandoc "
                "(e.g. `brew install pandoc` or `sudo apt install pandoc`)."
            )
            raise typer.Exit(code=1)
        raise


def main(
    notebook: Annotated[
        Path,
        typer.Argument(
            help="The path to the input Jupyter notebook (.ipynb).",
            exists=True,
            resolve_path=True,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Output Python file path. Defaults to notebook name with .py extension.",
            resolve_path=True,
        ),
    ] = None,
) -> None:
    """
    Convert a Jupyter notebook to a Sphinx Gallery Python script.

    This tool converts a .ipynb file to a .py file formatted for Sphinx Gallery.
    It converts Markdown cells to RST (using pypandoc) and comments them out,
    while preserving code cells. It also handles magic commands by commenting them out.

    Based on: https://gist.github.com/chsasank/7218ca16f8d022e02a9c0deb94a310fe

    Arguments:
        NOTEBOOK: The path to the input Jupyter notebook (.ipynb).

    Examples:

        uv run https://tools.ricardodecal.com/python/ipynb_to_py_sphinx.py notebook.ipynb

        uv run https://tools.ricardodecal.com/python/ipynb_to_py_sphinx.py notebook.ipynb --output my_gallery_script.py
    """
    if output is None:
        output = notebook.with_suffix(".py")

    try:
        with notebook.open("r", encoding="utf-8") as f:
            nb_dict = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[bold red]Error:[/bold red] Invalid JSON in notebook file: {e}")
        raise typer.Exit(code=1)

    cells: list[dict[str, object]] = nb_dict.get("cells", [])
    python_content: list[str] = []

    for i, cell in enumerate(cells):
        cell_type = cell.get("cell_type")
        source = cell.get("source", [])

        if i == 0:
            if cell_type != "markdown":
                print("[bold red]Error:[/bold red] First cell has to be markdown")
                raise typer.Exit(code=1)

            # First cell is usually the title/description
            rst_source = convert_cell_to_rst(source)
            python_content.append(f'"""\n{rst_source}\n"""')
        else:
            if cell_type == "markdown" or cell_type == "raw":
                # Treat raw cells as potential reST or just comment them out
                # If it's raw, we assume it might be reST suitable for the gallery
                # but we'll comment it out to be safe and consistent with markdown behavior
                if cell_type == "markdown":
                    rst_source = convert_cell_to_rst(source)
                else:
                    # Raw cell: Just dump the content
                    rst_source = "".join(source)

                # Comment out RST lines
                commented_source = "\n".join(
                    f"# {line}" if line.strip() else "#"
                    for line in rst_source.splitlines()
                )
                python_content.append(f"\n\n{'#' * 70}\n{commented_source}")
            elif cell_type == "code":
                code_source = "".join(source)
                lines = code_source.splitlines(keepends=True)

                # Check for cell magics that should comment out the entire cell
                # If a cell starts with %%magic, and it's not a python-wrapping magic,
                # we assume the content is not valid Python (e.g. %%bash, %%html).
                is_non_python_cell_magic = False
                if lines:
                    first_line = lines[0].lstrip()
                    if first_line.startswith("%%"):
                        parts = first_line[2:].split()
                        if parts:
                            magic_name = parts[0]
                            # Whitelist of magics that wrap Python code or are valid in context
                            # time/timeit: benchmark python code
                            # capture: capture stdout/stderr of python code
                            # prun: profile python code
                            if magic_name not in {
                                "time",
                                "timeit",
                                "capture",
                                "prun",
                                "python",
                            }:
                                is_non_python_cell_magic = True

                if is_non_python_cell_magic:
                    processed_lines = [f"# {line}" for line in lines]
                    python_content.append(f"\n\n{''.join(processed_lines)}")
                    continue

                # Handle magic commands and system commands and help
                processed_lines = []
                for line in lines:
                    stripped = line.lstrip()
                    # %magic, !system, ?help, help?
                    is_magic = False
                    # Only consider it magic if it looks like %magic or %%magic
                    # i.e. followed by a letter or another %
                    # This avoids matching "% (args)" which is Python modulo formatting
                    if stripped.startswith("%") and re.match(
                        r"^%?%[a-zA-Z]+", stripped
                    ):
                        is_magic = True

                    # Check other magic/help patterns if not already identified
                    if not is_magic and (
                        stripped.startswith("!")
                        or stripped.startswith("?")
                        or stripped.strip().endswith("?")
                    ):
                        is_magic = True

                    if is_magic:
                        processed_lines.append(f"# {line}")
                    else:
                        processed_lines.append(line)
                python_content.append(f"\n\n{''.join(processed_lines)}")

    # Join all parts
    final_content = "".join(python_content)

    # Ensure newline at end of file
    if not final_content.endswith("\n"):
        final_content += "\n"

    try:
        output.write_text(final_content, encoding="utf-8")
        print(f"[green]Converted {notebook} to {output}[/green]")
    except OSError as e:
        print(f"[bold red]Error:[/bold red] Failed to write output file: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)

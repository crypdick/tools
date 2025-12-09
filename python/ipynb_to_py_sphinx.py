#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click>=8.1.0",
#     "pypandoc>=1.13",
# ]
# ///
"""
Convert a Jupyter notebook to a Sphinx Gallery Python script.
"""

import json
from pathlib import Path

import click
import pypandoc


def convert_cell_to_rst(source: list[str]) -> str:
    """Convert markdown source lines to RST."""
    md_source = "".join(source)
    # Handle potential Windows line endings issue mentioned in gist comments
    return pypandoc.convert_text(md_source, "rst", format="md").replace("\r", "")


@click.command()
@click.argument("notebook", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output Python file path. Defaults to notebook name with .py extension.",
)
def main(notebook: Path, output: Path | None) -> None:
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
        raise click.ClickException(f"Invalid JSON in notebook file: {e}") from e

    cells: list[dict[str, object]] = nb_dict.get("cells", [])
    python_content: list[str] = []

    for i, cell in enumerate(cells):
        cell_type = cell.get("cell_type")
        source = cell.get("source", [])

        if i == 0 and cell_type == "markdown":
            # First cell is usually the title/description
            rst_source = convert_cell_to_rst(source)
            python_content.append(f'"""\n{rst_source}\n"""')
        else:
            if cell_type == "markdown":
                rst_source = convert_cell_to_rst(source)
                # Comment out RST lines
                commented_source = "\n".join(
                    f"# {line}" if line.strip() else "#"
                    for line in rst_source.splitlines()
                )
                python_content.append(f"\n\n{'#' * 70}\n{commented_source}")
            elif cell_type == "code":
                code_source = "".join(source)
                # Handle magic commands and system commands
                lines = code_source.splitlines(keepends=True)
                processed_lines = []
                for line in lines:
                    stripped = line.lstrip()
                    if stripped.startswith("%") or stripped.startswith("!"):
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
        click.secho(f"Converted {notebook} to {output}", fg="green")
    except OSError as e:
        raise click.ClickException(f"Failed to write output file: {e}") from e


if __name__ == "__main__":
    main()

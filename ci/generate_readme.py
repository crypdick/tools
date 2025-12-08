#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Generate README.md from tool docstrings.
"""

import ast
import re
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).parent.parent
README_PATH = ROOT / "README.md"
README_BASE_PATH = ROOT / "ci" / "README_BASE.md"
PYTHON_DIR = ROOT / "python"
DOMAIN = "tools.ricardodecal.com"

START_MARKER = "<!-- TOOLS_START -->"
END_MARKER = "<!-- TOOLS_END -->"


class ToolInfo(NamedTuple):
    name: str
    filename: str
    docstring: str


def extract_tool_info(path: Path) -> ToolInfo | None:
    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree) or ""
        return ToolInfo(
            name=path.name,
            filename=path.name,
            docstring=docstring.strip(),
        )
    except Exception:
        return None


def format_tool_readme(info: ToolInfo) -> str:
    doc = info.docstring

    # Replace generic "uv run python/script.py" with nifty domain URL
    pattern = re.compile(rf"uv run python/{re.escape(info.filename)}")
    replacement = f"uv run https://{DOMAIN}/python/{info.filename}"

    # Also handle raw github URLs if present
    raw_pattern = re.compile(
        rf"https://raw\.githubusercontent\.com/[^/]+/[^/]+/[^/]+/python/{re.escape(info.filename)}"
    )

    doc = pattern.sub(replacement, doc)
    doc = raw_pattern.sub(replacement, doc)

    # We want to format it as a list item with the filename linking to the file
    # Then the full docstring indented.

    output = f"### [{info.filename}](python/{info.filename})\n\n"
    output += f"{doc}\n"

    return output


def generate_readme() -> None:
    if not README_BASE_PATH.exists():
        print(f"Error: {README_BASE_PATH} not found.")
        return

    content = README_BASE_PATH.read_text(encoding="utf-8")

    if START_MARKER not in content or END_MARKER not in content:
        print(
            f"Error: Markers {START_MARKER} and {END_MARKER} not found in README_BASE.md"
        )
        return

    # Process Python Tools
    tools_md = []
    if PYTHON_DIR.exists():
        for path in sorted(PYTHON_DIR.glob("*.py")):
            if path.name == "__init__.py":
                continue
            info = extract_tool_info(path)
            if info:
                tools_md.append(format_tool_readme(info))

    tools_content = "\n".join(tools_md)

    # Replace content between markers
    # We use string slicing instead of regex to avoid issues with backslashes in docstrings
    start_idx = content.find(START_MARKER)
    end_idx = content.find(END_MARKER)

    if start_idx == -1 or end_idx == -1:
        print(
            f"Error: Markers {START_MARKER} and {END_MARKER} not found in content (should have been checked earlier)"
        )
        return

    # We want to remove the markers from the output
    # content[:start_idx] includes everything before the start marker
    # content[end_idx + len(END_MARKER):] includes everything after the end marker
    new_content = (
        content[:start_idx] + tools_content + content[end_idx + len(END_MARKER) :]
    )

    current_content = ""
    if README_PATH.exists():
        current_content = README_PATH.read_text(encoding="utf-8")

    if new_content != current_content:
        README_PATH.write_text(new_content, encoding="utf-8")
        print(f"Successfully updated {README_PATH}")
    else:
        print("No changes needed for README.md")


if __name__ == "__main__":
    generate_readme()

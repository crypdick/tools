#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Generate README.md from tool --help output.
"""

import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).parent.parent
README_PATH = ROOT / "README.md"
README_BASE_PATH = ROOT / "ci" / "README_BASE.md"
PYTHON_DIR = ROOT / "python"
DOMAIN = "tools.ricardodecal.com"

START_MARKER = "<!-- TOOLS_START -->"
END_MARKER = "<!-- TOOLS_END -->"

# Category display order and titles
CATEGORY_ORDER = [
    "data",
    "dev",
    # "misc",  # Uncomment when needed
]
CATEGORY_TITLES = {
    "data": "📊 Data Processing",
    "dev": "🛠️ Development",
    # "misc": "📦 Misc",  # Uncomment when needed
}


class ToolInfo(NamedTuple):
    name: str
    filename: str
    help_output: str
    category: str


def extract_category(path: Path) -> str:
    """Extract category from PEP 723 script block."""
    content = path.read_text(encoding="utf-8")

    # Find the script block
    script_block_match = re.search(r"# /// script\s*\n(.*?)# ///", content, re.DOTALL)
    if not script_block_match:
        return "uncategorized"

    block = script_block_match.group(1)

    # Look for category = "..."
    category_match = re.search(r'#\s*category\s*=\s*"([^"]+)"', block)
    if category_match:
        return category_match.group(1)

    return "uncategorized"


def get_tool_help(path: Path) -> str:
    # Run from repo root
    try:
        result = subprocess.run(
            ["uv", "run", str(path), "--help"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running {path.name} --help: {e.stderr}")
        raise
    except Exception as e:
        print(f"Error executing {path.name}: {e}")
        raise


def extract_tool_info(path: Path) -> ToolInfo:
    help_output = get_tool_help(path)
    category = extract_category(path)

    return ToolInfo(
        name=path.name,
        filename=path.name,
        help_output=help_output,
        category=category,
    )


def format_tool_readme(info: ToolInfo) -> str:
    doc = info.help_output

    # Replace generic "uv run python/script.py" with nifty domain URL
    pattern = re.compile(rf"uv run python/{re.escape(info.filename)}")
    replacement = f"uv run https://{DOMAIN}/python/{info.filename}"

    # Also handle raw github URLs if present
    raw_pattern = re.compile(
        rf"https://raw\.githubusercontent\.com/[^/]+/[^/]+/[^/]+/python/{re.escape(info.filename)}"
    )

    doc = pattern.sub(replacement, doc)
    doc = raw_pattern.sub(replacement, doc)

    # Format as nested details element (use HTML tags since markdown isn't processed in HTML blocks)
    output = f"""<details>
<summary><a href="python/{info.filename}"><code>{info.filename}</code></a></summary>

Output of <code>uv run https://{DOMAIN}/python/{info.filename} --help</code>:

<pre><code>{doc}</code></pre>

</details>
"""
    return output


def format_category_section(category: str, tools: list[ToolInfo]) -> str:
    """Format a category with its tools as nested details."""
    title = CATEGORY_TITLES.get(category, category.title())
    tool_count = len(tools)

    tools_content = "\n".join(format_tool_readme(tool) for tool in tools)

    return f"""<details>
<summary><strong>{title}</strong> ({tool_count} tool{"s" if tool_count != 1 else ""})</summary>

{tools_content}
</details>
"""


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
    tools_by_category: dict[str, list[ToolInfo]] = defaultdict(list)

    if PYTHON_DIR.exists():
        for path in sorted(PYTHON_DIR.glob("*.py")):
            if path.name == "__init__.py":
                continue

            print(f"Processing {path.name}...")
            info = extract_tool_info(path)
            tools_by_category[info.category].append(info)

    # Generate content by category in order
    category_sections = []
    for category in CATEGORY_ORDER:
        if category in tools_by_category:
            section = format_category_section(category, tools_by_category[category])
            category_sections.append(section)

    # Add any uncategorized tools at the end
    for category in sorted(tools_by_category.keys()):
        if category not in CATEGORY_ORDER:
            section = format_category_section(category, tools_by_category[category])
            category_sections.append(section)

    tools_content = "\n".join(category_sections)

    # Replace content between markers
    start_idx = content.find(START_MARKER)
    end_idx = content.find(END_MARKER)

    if start_idx == -1 or end_idx == -1:
        print(
            f"Error: Markers {START_MARKER} and {END_MARKER} not found in content (should have been checked earlier)"
        )
        return

    new_content = (
        content[: start_idx + len(START_MARKER)]
        + "\n\n"
        + tools_content
        + "\n"
        + content[end_idx:]
    )

    # Check if README exists
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

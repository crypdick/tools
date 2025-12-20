#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Generate README.md from tool --help output and HTML tool metadata.
"""

import html
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).parent.parent
README_PATH = ROOT / "README.md"
README_BASE_PATH = ROOT / "ci" / "README_BASE.md"
PYTHON_DIR = ROOT / "python"
HTML_DIR = ROOT / "html"
DOMAIN = "tools.ricardodecal.com"

START_MARKER = "<!-- TOOLS_START -->"
END_MARKER = "<!-- TOOLS_END -->"

# Category titles (keep these in alphabetical order)
CATEGORY_TITLES = {
    "data": "📊 Data Processing",
    "dev": "🛠️ Development",
    # "misc": "📦 Misc",  # Save this here for later
}

# Tool type labels
TYPE_LABELS = {
    "script": "script",
    "page": "page",
}


class ToolInfo(NamedTuple):
    name: str
    filename: str
    help_output: str
    category: str
    tool_type: str  # "script" or "page"
    description: str  # Short description for the summary


def extract_python_category(path: Path) -> str:
    """Extract category from PEP 723 script block."""
    content = path.read_text(encoding="utf-8")

    script_block_match = re.search(r"# /// script\s*\n(.*?)# ///", content, re.DOTALL)
    if not script_block_match:
        raise ValueError(f"{path.name}: Missing PEP 723 script block")

    block = script_block_match.group(1)
    category_match = re.search(r'#\s*category\s*=\s*"([^"]+)"', block)
    if not category_match:
        raise ValueError(f"{path.name}: Missing category in script block")

    return category_match.group(1)


def extract_html_metadata(path: Path) -> tuple[str, str, str]:
    """Extract category, title, and description from HTML tool.

    Returns (category, title, description).
    Raises ValueError if required metadata is missing.
    """
    content = path.read_text(encoding="utf-8")

    # Extract category from frontmatter comment
    frontmatter_match = re.search(r"<!--\s*(.*?)\s*-->", content, re.DOTALL)
    if not frontmatter_match:
        raise ValueError(f"{path.name}: Missing frontmatter comment")

    frontmatter = frontmatter_match.group(1)
    category_match = re.search(r"category:\s*(\w+)", frontmatter)
    if not category_match:
        raise ValueError(f"{path.name}: Missing category in frontmatter")

    category = category_match.group(1)

    # Extract title from <title> tag
    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    if not title_match or not title_match.group(1).strip():
        raise ValueError(f"{path.name}: Missing or empty <title> tag")

    title = title_match.group(1).strip()

    # Extract description from .subtitle paragraph
    subtitle_match = re.search(
        r'<p\s+class="subtitle">(.*?)</p>', content, re.IGNORECASE | re.DOTALL
    )
    if not subtitle_match or not subtitle_match.group(1).strip():
        raise ValueError(f"{path.name}: Missing or empty <p class=\"subtitle\">")

    # Strip HTML tags and clean up
    desc_html = subtitle_match.group(1)
    description = re.sub(r"<[^>]+>", "", desc_html).strip()
    # Truncate if too long
    if len(description) > 150:
        description = description[:147] + "..."

    return category, title, description


def get_python_tool_help(path: Path) -> str:
    """Run --help on a Python tool and return output."""
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


def extract_python_description(help_output: str) -> str:
    """Extract short description from --help output (first non-empty line after Usage)."""
    lines = help_output.strip().split("\n")

    in_description = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_description:
                break
            continue
        if stripped.startswith("Usage:"):
            in_description = True
            continue
        if in_description and not stripped.startswith("-"):
            if len(stripped) > 150:
                return stripped[:147] + "..."
            return stripped

    # Fallback: first non-empty line
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("Usage:"):
            if len(stripped) > 150:
                return stripped[:147] + "..."
            return stripped

    return ""


def extract_python_tool_info(path: Path) -> ToolInfo:
    """Extract info from a Python tool."""
    help_output = get_python_tool_help(path)
    category = extract_python_category(path)
    description = extract_python_description(help_output)

    return ToolInfo(
        name=path.stem,
        filename=path.name,
        help_output=help_output,
        category=category,
        tool_type="script",
        description=description,
    )


def extract_html_tool_info(path: Path) -> ToolInfo:
    """Extract info from an HTML tool."""
    category, title, description = extract_html_metadata(path)

    return ToolInfo(
        name=path.stem,
        filename=path.name,
        help_output="",
        category=category,
        tool_type="page",
        description=description,
    )


def format_python_tool_readme(info: ToolInfo) -> str:
    """Format a Python tool for the README."""
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

    return f"""<details>
<summary><a href="python/{info.filename}"><code>{info.filename}</code></a> <kbd>{TYPE_LABELS[info.tool_type]}</kbd></summary>

Output of <code>uv run https://{DOMAIN}/python/{info.filename} --help</code>:

<pre><code>{html.escape(doc)}</code></pre>

</details>
"""


def format_html_tool_readme(info: ToolInfo) -> str:
    """Format an HTML tool for the README (non-collapsible)."""
    return f"""<div class="page">
<p><a href="html/{info.filename}"><code>{info.filename}</code></a> <kbd>{TYPE_LABELS[info.tool_type]}</kbd></p>
<p><a href="https://{DOMAIN}/html/{info.filename}">https://{DOMAIN}/html/{info.filename}</a><br>{info.description}</p>
</div>
"""


def format_tool_readme(info: ToolInfo) -> str:
    """Format a tool for the README based on its type."""
    if info.tool_type == "script":
        return format_python_tool_readme(info)
    else:
        return format_html_tool_readme(info)


def format_category_section(category: str, tools: list[ToolInfo]) -> str:
    """Format a category with its tools as nested details."""
    title = CATEGORY_TITLES.get(category, category.title())

    # Count by type
    scripts = [t for t in tools if t.tool_type == "script"]
    pages = [t for t in tools if t.tool_type == "page"]

    # Build count string
    counts = []
    if scripts:
        counts.append(f"{len(scripts)} script{'s' if len(scripts) != 1 else ''}")
    if pages:
        counts.append(f"{len(pages)} page{'s' if len(pages) != 1 else ''}")
    count_str = ", ".join(counts)

    # Sort all tools alphabetically by filename (interleaved)
    sorted_tools = sorted(tools, key=lambda t: t.filename)

    tools_content = "\n".join(format_tool_readme(tool) for tool in sorted_tools)

    return f"""<details>
<summary><strong>{title}</strong> ({count_str})</summary>

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

    # Collect all tools by category
    tools_by_category: dict[str, list[ToolInfo]] = defaultdict(list)

    # Process Python Tools
    if PYTHON_DIR.exists():
        for path in sorted(PYTHON_DIR.glob("*.py")):
            if path.name == "__init__.py":
                continue

            print(f"Processing {path.name}...")
            info = extract_python_tool_info(path)
            tools_by_category[info.category].append(info)

    # Process HTML Tools
    if HTML_DIR.exists():
        for path in sorted(HTML_DIR.glob("*.html")):
            print(f"Processing {path.name}...")
            info = extract_html_tool_info(path)
            tools_by_category[info.category].append(info)

    # Generate content by category in alphabetical order
    category_sections = []
    for category in sorted(tools_by_category.keys()):
        section = format_category_section(category, tools_by_category[category])
        category_sections.append(section)

    tools_content = "\n".join(category_sections)

    # Replace content between markers
    start_idx = content.find(START_MARKER)
    end_idx = content.find(END_MARKER)

    new_content = (
        content[: start_idx + len(START_MARKER)]
        + "\n\n"
        + tools_content
        + "\n"
        + content[end_idx:]
    )

    # Check if README exists and differs
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

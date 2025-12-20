#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "markdown",
# ]
# ///
"""
Generate index.html from README.md.
"""

import re
from pathlib import Path

import markdown

ROOT = Path(__file__).parent.parent
README_PATH = ROOT / "README.md"
INDEX_PATH = ROOT / "index.html"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ricardo Decal's Tools</title>
    <style>
        :root {
            --bg: #ffffff;
            --text: #24292f;
            --link: #0969da;
            --border: #d0d7de;
            --code-bg: #f6f8fa;
            --category-bg: #f6f8fa;
            --tool-bg: #ffffff;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #0d1117;
                --text: #c9d1d9;
                --link: #58a6ff;
                --border: #30363d;
                --code-bg: #161b22;
                --category-bg: #161b22;
                --tool-bg: #0d1117;
            }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                "Noto Sans",
                Helvetica,
                Arial,
                sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--bg);
            padding: 2rem 1rem;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
        }

        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        .subtitle {
            color: var(--text);
            opacity: 0.7;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }

        .section {
            margin: 2rem 0;
        }

        h2 {
            font-size: 1.5rem;
            margin: 2rem 0 1rem;
            padding-bottom: 0.3rem;
            border-bottom: 1px solid var(--border);
        }

        h2 a {
            color: var(--text);
            text-decoration: none;
        }

        h2 a:hover {
            color: var(--link);
            text-decoration: underline;
        }

        p {
            margin: 1rem 0;
        }

        code {
            background: var(--code-bg);
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family:
                ui-monospace,
                SFMono-Regular,
                "SF Mono",
                Menlo,
                Consolas,
                monospace;
            font-size: 0.9em;
        }

        pre {
            background: var(--code-bg);
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1rem 0;
        }

        pre code {
            background: none;
            padding: 0;
        }

        a {
            color: var(--link);
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        .repo-link {
            display: inline-block;
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background: var(--code-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-weight: 500;
        }

        .tools-list {
            margin: 1rem 0;
            padding-left: 2rem;
        }

        .tools-list li {
            margin: 0.5rem 0;
        }

        .tool {
            margin-top: 3rem;
        }

        /* Category-level details (outer) */
        details.category {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 1rem 0;
            background: var(--category-bg);
        }

        details.category[open] {
            padding-bottom: 1rem;
        }

        details.category > summary {
            cursor: pointer;
            font-weight: 600;
            font-size: 1.2rem;
            user-select: none;
            list-style: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        details.category > summary::-webkit-details-marker {
            display: none;
        }

        details.category > summary::before {
            content: '▶';
            display: inline-block;
            transition: transform 0.2s;
            font-size: 0.8em;
        }

        details.category[open] > summary::before {
            transform: rotate(90deg);
        }

        details.category > summary:hover {
            color: var(--link);
        }

        /* Tool-level details (nested inside category) */
        details.tool {
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.5rem 0.75rem;
            margin: 0.5rem 0;
            margin-left: 1.5rem;
            background: var(--tool-bg);
        }

        details.tool[open] {
            padding-bottom: 0.75rem;
        }

        details.tool > summary {
            cursor: pointer;
            font-weight: 500;
            font-size: 1rem;
            user-select: none;
            list-style: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        details.tool > summary::-webkit-details-marker {
            display: none;
        }

        details.tool > summary::before {
            content: '▸';
            display: inline-block;
            transition: transform 0.2s;
            font-size: 0.7em;
        }

        details.tool[open] > summary::before {
            transform: rotate(90deg);
        }

        details.tool > summary:hover {
            color: var(--link);
        }

        details.tool .content {
            margin-top: 0.75rem;
            padding-left: 1rem;
        }

        details.tool pre {
            margin: 0.5rem 0;
            font-size: 0.85em;
        }

        /* Fallback for any details without a class */
        details:not(.category):not(.tool) {
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.75rem 1rem;
            margin: 0.75rem 0;
            background: var(--code-bg);
        }

        details:not(.category):not(.tool)[open] {
            padding-bottom: 1rem;
        }

        details:not(.category):not(.tool) > summary {
            cursor: pointer;
            font-weight: 600;
            font-size: 1.1rem;
            user-select: none;
            list-style: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        details:not(.category):not(.tool) > summary::-webkit-details-marker {
            display: none;
        }

        details:not(.category):not(.tool) > summary::before {
            content: '▶';
            display: inline-block;
            transition: transform 0.2s;
            font-size: 0.8em;
        }

        details:not(.category):not(.tool)[open] > summary::before {
            transform: rotate(90deg);
        }

        details:not(.category):not(.tool) > summary:hover {
            color: var(--link);
        }

        details:not(.category):not(.tool) .content {
            margin-top: 1rem;
            padding-left: 1.3rem;
        }

        footer {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border);
            text-align: center;
            font-size: 0.9em;
            color: var(--text);
            opacity: 0.7;
        }

        footer p {
            margin: 0.5rem 0;
        }

        footer a {
            color: var(--link);
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ricardo Decal's Tools</h1>
        <p class="subtitle">Simple, self-contained, and immediately runnable</p>

        <div style="margin-bottom: 2rem;">
            <a href="https://github.com/crypdick/tools" class="repo-link">
                📦 View on GitHub
            </a>
        </div>

        {content}

        <footer>
            <p>Made by Ricardo Decal • Updated {date}</p>
            <p>
                <a href="https://ricardodecal.com">ricardodecal.com</a> |
                <a href="https://github.com/crypdick/tools">View on GitHub</a> |
                <a href="https://github.com/crypdick/tools/blob/main/index.html">View source</a>
            </p>
            <p><a href="LICENSE">Apache 2.0 License</a></p>
        </footer>
    </div>
</body>
</html>
"""


def add_details_classes(html: str) -> str:
    """Add CSS classes to nested details elements for styling.

    Category-level details (summaries with <strong>) get class="category".
    Tool-level details (summaries with <code>) get class="tool".
    """

    def classify_details(match: re.Match[str]) -> str:
        summary = match.group(1)
        # Categories have <strong> in their summary (e.g., <strong>Data</strong>)
        # Tools have <code> in their summary (e.g., <code>tool.py</code>)
        if "<strong>" in summary:
            return f'<details class="category">\n<summary>{summary}</summary>'
        else:
            return f'<details class="tool">\n<summary>{summary}</summary>'

    # Match <details> followed by <summary>...</summary>
    result = re.sub(
        r"<details>\s*<summary>(.*?)</summary>",
        classify_details,
        html,
        flags=re.DOTALL,
    )

    return result


def wrap_tool_content(html: str) -> str:
    """Wrap tool content (everything after summary) in a content div."""
    # Pattern: find tool details and wrap content after summary
    pattern = r'(<details class="tool">)\s*(<summary>.*?</summary>)\s*(.*?)(</details>)'

    def wrap_content(match: re.Match[str]) -> str:
        opening = match.group(1)
        summary = match.group(2)
        content = match.group(3).strip()
        closing = match.group(4)
        return (
            f'{opening}\n{summary}\n<div class="content">\n{content}\n</div>\n{closing}'
        )

    return re.sub(pattern, wrap_content, html, flags=re.DOTALL)


def generate_index() -> None:
    if not README_PATH.exists():
        print(f"Error: {README_PATH} not found.")
        return

    # 1. Process README
    content = README_PATH.read_text(encoding="utf-8")

    # Remove HTML comments (e.g. markers and warnings)
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

    # Remove leading whitespace which might be left after comment removal
    content = content.lstrip()

    # Remove the title (first line level 1 header)
    content = re.sub(r"^# .+\s+", "", content)

    # Remove the License section (it will be in the footer)
    content = re.sub(r"## License.*$", "", content, flags=re.DOTALL)

    # Convert README to HTML
    html_content = markdown.markdown(content, extensions=["fenced_code", "tables"])

    # Add CSS classes to details elements
    html_content = add_details_classes(html_content)

    # Wrap tool content in content divs
    html_content = wrap_tool_content(html_content)

    # Inject into template with current date
    from datetime import datetime

    current_date = datetime.now().strftime("%B %d, %Y")
    final_html = HTML_TEMPLATE.replace("{content}", html_content).replace(
        "{date}", current_date
    )

    # Ensure single trailing newline and no trailing whitespace on lines
    lines = [line.rstrip() for line in final_html.splitlines()]
    final_html = "\n".join(lines) + "\n"

    INDEX_PATH.write_text(final_html, encoding="utf-8")
    print(f"Successfully generated {INDEX_PATH}")


if __name__ == "__main__":
    generate_index()

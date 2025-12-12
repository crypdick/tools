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
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #0d1117;
                --text: #c9d1d9;
                --link: #58a6ff;
                --border: #30363d;
                --code-bg: #161b22;
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

        details {
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.75rem 1rem;
            margin: 0.75rem 0;
            background: var(--code-bg);
        }

        details[open] {
            padding-bottom: 1rem;
        }

        summary {
            cursor: pointer;
            font-weight: 600;
            font-size: 1.1rem;
            user-select: none;
            list-style: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        summary::-webkit-details-marker {
            display: none;
        }

        summary::before {
            content: '▶';
            display: inline-block;
            transition: transform 0.2s;
            font-size: 0.8em;
        }

        details[open] summary::before {
            transform: rotate(90deg);
        }

        summary:hover {
            color: var(--link);
        }

        details .content {
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


def wrap_tools_in_details(html: str) -> str:
    """Wrap each H3 tool section in a collapsible details element."""
    # Pattern to match H3 headings and their content until the next H3 or H2
    pattern = r'(<h3>.*?</h3>)(.*?)(?=<h3>|<h2>|$)'

    def replace_tool(match):
        h3_tag = match.group(1)
        content = match.group(2)

        # Extract the tool name from the h3 tag
        tool_name_match = re.search(r'<a[^>]*>([^<]+)</a>', h3_tag)
        if tool_name_match:
            tool_name = tool_name_match.group(1)
            return f'<details>\n<summary>{tool_name}</summary>\n<div class="content">\n{content.strip()}\n</div>\n</details>\n'
        return h3_tag + content

    return re.sub(pattern, replace_tool, html, flags=re.DOTALL)


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

    # Wrap tool sections in collapsible details elements
    html_content = wrap_tools_in_details(html_content)

    # Inject into template with current date
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    final_html = HTML_TEMPLATE.replace("{content}", html_content).replace("{date}", current_date)

    # Ensure single trailing newline and no trailing whitespace on lines
    lines = [line.rstrip() for line in final_html.splitlines()]
    final_html = "\n".join(lines) + "\n"

    INDEX_PATH.write_text(final_html, encoding="utf-8")
    print(f"Successfully generated {INDEX_PATH}")


if __name__ == "__main__":
    generate_index()

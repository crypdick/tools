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
            margin: 1.5rem 0 1rem;
            padding-bottom: 0.3rem;
            border-bottom: 1px solid var(--border);
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

        footer {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border);
            text-align: center;
            opacity: 0.7;
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

    </div>
</body>
</html>
"""


def generate_index() -> None:
    if not README_PATH.exists():
        print(f"Error: {README_PATH} not found.")
        return

    content = README_PATH.read_text(encoding="utf-8")

    # Remove the title
    # We look for the first line being a level 1 header and remove it,
    # and any following blank lines
    content = re.sub(r"^# .+\s+", "", content)

    # Convert to HTML
    html_content = markdown.markdown(content, extensions=["fenced_code", "tables"])

    # Inject into template
    final_html = HTML_TEMPLATE.replace("{content}", html_content)

    INDEX_PATH.write_text(final_html, encoding="utf-8")
    print(f"Successfully generated {INDEX_PATH}")


if __name__ == "__main__":
    generate_index()

#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Check that all HTML tools have required metadata.

Every HTML file in html/ must have:
1. A frontmatter comment with category
2. A <title> tag
3. A <p class="subtitle"> element for description
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
HTML_DIR = ROOT / "html"

# Categories are displayed alphabetically in the README
VALID_CATEGORIES = {"data", "dev", "misc"}


def check_html_file(path: Path) -> list[str]:
    """Check a single HTML file for required metadata. Returns list of errors."""
    errors = []
    content = path.read_text(encoding="utf-8")

    # Check frontmatter comment with category
    frontmatter_match = re.search(r"<!--\s*(.*?)\s*-->", content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Missing frontmatter comment at top of file")
    else:
        frontmatter = frontmatter_match.group(1)
        category_match = re.search(r"category:\s*(\w+)", frontmatter)
        if not category_match:
            errors.append("Missing 'category' in frontmatter")
        else:
            category = category_match.group(1)
            if category not in VALID_CATEGORIES:
                errors.append(
                    f"Invalid category '{category}'. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}"
                )

    # Check <title> tag
    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    if not title_match:
        errors.append("Missing <title> tag")
    elif not title_match.group(1).strip():
        errors.append("<title> tag is empty")

    # Check <p class="subtitle"> element
    subtitle_match = re.search(
        r'<p\s+class="subtitle">(.*?)</p>', content, re.IGNORECASE | re.DOTALL
    )
    if not subtitle_match:
        errors.append('Missing <p class="subtitle"> element for description')
    elif not subtitle_match.group(1).strip():
        errors.append('<p class="subtitle"> element is empty')

    return errors


def main() -> int:
    if not HTML_DIR.exists():
        print("No html/ directory found, skipping check.")
        return 0

    html_files = sorted(HTML_DIR.glob("*.html"))
    if not html_files:
        print("No HTML files found in html/")
        return 0

    all_passed = True

    for path in html_files:
        errors = check_html_file(path)
        if errors:
            all_passed = False
            print(f"❌ {path.name}:")
            for error in errors:
                print(f"   - {error}")
        else:
            print(f"✓ {path.name}")

    if all_passed:
        print(f"\n✓ All {len(html_files)} HTML files have valid metadata")
        return 0
    else:
        print("\n❌ Some HTML files have missing or invalid metadata")
        return 1


if __name__ == "__main__":
    sys.exit(main())

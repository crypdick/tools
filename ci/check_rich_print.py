#!/usr/bin/env python3
"""Check that Python tools import print from rich."""

import ast
import sys
from pathlib import Path


def has_rich_print_import(tree: ast.Module) -> bool:
    """Check if file has 'from rich import print' statement."""
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "rich"
            and any(alias.name == "print" for alias in node.names)
        ):
            return True
    return False


def check_file(filepath: Path) -> bool:
    """Check if file imports print from rich."""
    try:
        content = filepath.read_text()
        tree = ast.parse(content, filename=str(filepath))

        if not has_rich_print_import(tree):
            print(f"{filepath}: missing 'from rich import print'")
            return False

        return True
    except SyntaxError as e:
        print(f"{filepath}: syntax error: {e}")
        return False


def main() -> int:
    """Check all Python tool files passed as arguments."""
    files = [Path(f) for f in sys.argv[1:]]
    # Only check files in python/ directory
    python_tools = [
        f
        for f in files
        if f.suffix == ".py"
        and f.is_file()
        and "python/" in str(f)
        and not f.name.startswith("test_")
    ]

    if not python_tools:
        return 0

    all_good = True
    for filepath in python_tools:
        if not check_file(filepath):
            all_good = False

    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())


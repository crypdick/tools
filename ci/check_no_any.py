#!/usr/bin/env python3
"""Check that Python files don't use typing.Any."""

import ast
import sys
from pathlib import Path


def check_file(filepath: Path) -> bool:
    """Check if file uses typing.Any."""
    try:
        content = filepath.read_text()
        tree = ast.parse(content, filename=str(filepath))

        # Track if typing.Any is imported
        any_imported = False
        any_alias = None

        for node in ast.walk(tree):
            # Check for: from typing import Any
            if isinstance(node, ast.ImportFrom) and node.module == "typing":
                for alias in node.names:
                    if alias.name == "Any":
                        any_alias = alias.asname or "Any"
                        any_imported = True

            # Check for usage of Any in annotations
            if any_imported and isinstance(node, ast.Name) and node.id == any_alias:
                print(f"{filepath}: uses typing.Any (use specific types instead)")
                return False

        return True
    except SyntaxError as e:
        print(f"{filepath}: syntax error: {e}")
        return False


def main() -> int:
    """Check all Python files passed as arguments."""
    files = [Path(f) for f in sys.argv[1:]]
    python_files = [f for f in files if f.suffix == ".py" and f.is_file()]

    if not python_files:
        return 0

    all_good = True
    for filepath in python_files:
        if not check_file(filepath):
            all_good = False

    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())

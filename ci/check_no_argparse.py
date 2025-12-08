#!/usr/bin/env python3
"""Check that Python files use click instead of argparse."""

import ast
import sys
from pathlib import Path


def check_file(filepath: Path) -> bool:
    """Check if file imports argparse."""
    try:
        content = filepath.read_text()
        tree = ast.parse(content, filename=str(filepath))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "argparse":
                        print(f"{filepath}: uses argparse (use click instead)")
                        return False
            elif isinstance(node, ast.ImportFrom) and node.module == "argparse":
                print(f"{filepath}: imports from argparse (use click instead)")
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

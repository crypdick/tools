#!/usr/bin/env python3
"""Check that Python files use click.echo instead of print()."""

import ast
import sys
from pathlib import Path


def check_file(filepath: Path) -> bool:
    """Check if file uses print() calls."""
    try:
        content = filepath.read_text()
        tree = ast.parse(content, filename=str(filepath))

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ):
                line = node.lineno
                print(f"{filepath}:{line}: uses print() (use click.echo instead)")
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

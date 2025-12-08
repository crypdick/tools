#!/usr/bin/env python3
"""Check that Python CLI tools have if __name__ == '__main__' guard."""

import ast
import sys
from pathlib import Path


def has_main_guard(tree: ast.Module) -> bool:
    """Check if AST has if __name__ == '__main__' pattern."""
    for node in tree.body:
        if (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "__name__"
            and len(node.test.ops) == 1
            and isinstance(node.test.ops[0], ast.Eq)
            and len(node.test.comparators) == 1
            and isinstance(node.test.comparators[0], ast.Constant)
            and node.test.comparators[0].value == "__main__"
        ):
            return True
    return False


def check_file(filepath: Path) -> bool:
    """Check if file has main guard."""
    try:
        content = filepath.read_text()
        tree = ast.parse(content, filename=str(filepath))

        if not has_main_guard(tree):
            print(f"{filepath}: missing 'if __name__ == \"__main__\":' guard")
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

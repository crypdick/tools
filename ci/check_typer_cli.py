#!/usr/bin/env python3
"""Check that Python files use typer instead of argparse or click."""

import ast
import sys
from pathlib import Path

BANNED_MODULES = {
    "argparse": "use typer instead",
    "click": "use typer instead",
}


def check_file(filepath: Path) -> bool:
    """Check if file imports banned CLI modules."""
    try:
        content = filepath.read_text()
        tree = ast.parse(content, filename=str(filepath))

        all_good = True
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in BANNED_MODULES:
                        reason = BANNED_MODULES[alias.name]
                        print(f"{filepath}:{node.lineno}: imports {alias.name} ({reason})")
                        all_good = False
            elif isinstance(node, ast.ImportFrom) and node.module in BANNED_MODULES:
                reason = BANNED_MODULES[node.module]
                print(f"{filepath}:{node.lineno}: imports from {node.module} ({reason})")
                all_good = False

        return all_good
    except SyntaxError as e:
        print(f"{filepath}: syntax error: {e}")
        return False


def main() -> int:
    """Check all Python files passed as arguments."""
    files = [Path(f) for f in sys.argv[1:]]
    # Only check files in python/ directory (not ci/ scripts)
    python_files = [
        f
        for f in files
        if f.suffix == ".py"
        and f.is_file()
        and "python/" in str(f)
    ]

    if not python_files:
        return 0

    all_good = True
    for filepath in python_files:
        if not check_file(filepath):
            all_good = False

    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())

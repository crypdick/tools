#!/usr/bin/env python3
"""Check that scripts are executable."""

import os
import sys
from pathlib import Path


def main() -> int:
    """Check all files passed as arguments are executable."""
    files = [Path(f) for f in sys.argv[1:]]

    if not files:
        return 0

    non_executable = []
    for filepath in files:
        if filepath.is_file() and not os.access(filepath, os.X_OK):
            non_executable.append(filepath)

    if non_executable:
        for f in non_executable:
            print(f"{f}: not executable (run: chmod +x {f})")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

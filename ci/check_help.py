#!/usr/bin/env python3
"""Check that all python tools support --help."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Check python scripts support --help.

    If arguments are provided, check those files.
    If no arguments, check all .py files in python/ directory.
    """
    files_to_check = []

    if len(sys.argv) > 1:
        files_to_check = [Path(f) for f in sys.argv[1:]]
    else:
        # Find the root of the repo (assuming this script is in ci/)
        repo_root = Path(__file__).parent.parent
        python_dir = repo_root / "python"

        if not python_dir.exists():
            print(f"Directory not found: {python_dir}")
            return 1

        files_to_check = list(python_dir.glob("*.py"))

    failed = []

    for script in files_to_check:
        # Skip __init__.py if it exists
        if script.name == "__init__.py":
            continue

        # Only check .py files
        if script.suffix != ".py":
            continue

        print(f"Checking {script.name}...")
        try:
            # We use uv run to execute the script with its dependencies
            result = subprocess.run(
                ["uv", "run", str(script), "--help"], capture_output=True, text=True
            )

            if result.returncode != 0:
                print(f"FAIL: {script.name} returned non-zero exit code with --help")
                print(f"Stderr: {result.stderr}")
                failed.append(script.name)
            elif "--help" not in result.stdout and "Usage:" not in result.stdout:
                if "Options:" not in result.stdout:
                    print(
                        f"WARN: {script.name} might not be printing help info correctly."
                    )
        except Exception as e:
            print(f"ERROR running {script.name}: {e}")
            failed.append(script.name)

    if failed:
        print(f"\nFailed checks: {', '.join(failed)}")
        return 1

    print("\nAll python tools support --help!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

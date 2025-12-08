# Library Code

This directory contains shared code and utilities used by multiple tools in this repository.

## Purpose

The `lib/` directory is for:

- Common functions used across multiple tools
- Utility modules
- Shared configuration
- Helper classes and functions

## Usage

### In Python Tools

To use library code in Python tools while maintaining the single-file execution model, you have a few options:

#### Option 1: Inline the Code (Recommended for uv run)

For tools that need to be runnable via `uv run` from URLs, inline any needed utility functions directly in the tool file.

#### Option 2: Import from lib/ (Local Execution Only)

For tools run locally, you can import from the lib directory:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import sys
from pathlib import Path

# Add lib directory to path
lib_path = Path(__file__).parent.parent / "lib"
sys.path.insert(0, str(lib_path))

from common_utils import some_function

# ... rest of your tool
```

Note: This approach only works for local execution, not for `uv run` from URLs.

### In Bash Scripts

Source shared bash functions:

```shell
#!/usr/bin/env bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common functions
source "$SCRIPT_DIR/../lib/common.sh"

# ... rest of your script
```

## Examples

### Python Library Module

```python
# lib/common_utils.py
"""Common utility functions for tools."""

def format_output(message: str, color: str = "default") -> str:
    """Format a message with optional color."""
    colors = {
        "red": "\033[0;31m",
        "green": "\033[0;32m",
        "yellow": "\033[1;33m",
        "default": "\033[0m",
    }
    color_code = colors.get(color, colors["default"])
    reset = "\033[0m"
    return f"{color_code}{message}{reset}"
```

### Bash Library Module

```shell
# lib/common.sh
# Common bash functions

# Print colored messages
print_error() {
    echo -e "\033[0;31mError: $*\033[0m" >&2
}

print_success() {
    echo -e "\033[0;32m$*\033[0m"
}

print_warning() {
    echo -e "\033[1;33m$*\033[0m" >&2
}
```

## Guidelines

1. **Keep it Simple**: Only add truly reusable code to lib/
2. **Document Well**: Every function should have clear documentation
3. **Avoid Dependencies**: Library code should have minimal dependencies
4. **Test Thoroughly**: Add tests for library functions in `tests/`
5. **Consider Inlining**: For tools meant to run via `uv run` URLs, consider inlining code instead of creating library dependencies

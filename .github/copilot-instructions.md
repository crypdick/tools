# Custom Instructions for GitHub Copilot

## Project Overview

This repository contains a collection of command-line tools organized by implementation language. Tools are designed to be self-contained, executable, and runnable using `uv run` for Python tools.

## Code Style and Standards

### Python Tools

- **Python Version**: Target Python 3.12 or later
- **Style Guide**: Follow PEP 8
- **Dependency Management**: Use PEP 723 inline script metadata
- **CLI Framework**: Prefer `click` for argument parsing
- **Type Hints**: Include type hints where appropriate
- **Docstrings**: Use clear, concise docstrings

### Bash Scripts

- **Shell**: Use `bash`, not `sh`
- **Error Handling**: Always include `set -euo pipefail`
- **Portability**: Write portable bash that works on Linux and macOS
- **Quoting**: Always quote variables
- **Comments**: Include header comments explaining purpose

## Tool Structure

### Python Tool Template

Every Python tool should:

1. Start with `#!/usr/bin/env python3` shebang
2. Include PEP 723 inline script metadata with dependencies
3. Have a module-level docstring
4. Use `click` for CLI argument parsing
5. Include a `if __name__ == "__main__":` guard
6. Be runnable directly with `uv run`

Example:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click>=8.1.0",
# ]
# ///
"""
Tool description here.
"""

import click

@click.command()
def main():
    """Main function."""
    pass

if __name__ == "__main__":
    main()
```

### Bash Script Template

Every bash script should:

1. Start with `#!/usr/bin/env bash` shebang
2. Include header comments (description, usage)
3. Use `set -euo pipefail` for error handling
4. Provide `--help` option
5. Use functions for complex logic
6. Be executable (`chmod +x`)

## Dependencies

- **Python**: Specify dependencies in PEP 723 metadata
- **Bash**: Prefer standard utilities; document external dependencies in comments
- **Minimal**: Keep dependencies minimal for easy execution
- **Versions**: Pin major versions but allow minor updates

## Documentation

- **TOOLS_GUIDE.md**: Document each new tool in the tools guide
- **Help Text**: Every tool must have helpful `--help` output
- **Examples**: Include usage examples in docstrings or comments
- **README**: Keep README.md updated with project overview

## Testing

- **Python**: Write pytest tests in `tests/` directory
- **Bash**: Use shellcheck for linting
- **CI/CD**: All tools are tested via GitHub Actions

## AI-Assisted Development Guidelines

When generating new tools:

1. Create self-contained, single-file tools when possible
2. Include all necessary imports and dependencies
3. Provide clear error messages for user mistakes
4. Make tools immediately runnable after creation
5. Follow the principle of least surprise
6. Prefer simplicity over cleverness

## Special Considerations

- **Security**: Never hard-code credentials or sensitive data
- **Cross-platform**: Consider macOS and Linux compatibility
- **Offline-first**: Tools should work without network when possible
- **Idempotency**: Scripts should be safe to run multiple times
- **Exit Codes**: Use appropriate exit codes (0 for success, non-zero for errors)

## File Organization

```
tools/
├── python/          # Python CLI tools
├── bash/            # Bash scripts
├── lib/             # Shared library code
├── tests/           # Test files
├── .github/         # GitHub Actions and config
├── TOOLS_GUIDE.md   # Comprehensive tool documentation
└── README.md        # Project overview
```

## One-Shot Tool Development

For rapid tool development with AI:

1. Describe the tool's purpose clearly
2. Specify any required dependencies
3. Request adherence to these guidelines
4. Ask for complete, runnable code
5. Include basic error handling
6. Ensure the tool is self-documenting

## Common Patterns

### CLI Input

- Use `click.command()` and `click.option()` for Python
- Use `while [[ $# -gt 0 ]]` pattern for bash argument parsing

### Error Handling

- Use `try/except` with informative messages in Python
- Check exit codes and use `|| { echo "Error"; exit 1; }` in bash

### Output Formatting

- Use `click.echo()` for consistent output in Python
- Provide `--verbose` and `--quiet` options where appropriate
- Use colors sparingly and make them optional

### File Operations

- Use `pathlib.Path` in Python for file operations
- Always check if files exist before operations
- Clean up temporary files

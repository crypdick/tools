# Python Tools

Python CLI tools runnable with `uv run`, using PEP 723 inline metadata for dependencies.

## Running Tools

```shell
# From GitHub URL (no clone needed)
uv run https://tools.ricardodecal.com/python/foo.py [args]

# Locally
uv run python/foo.py [args]
```

## Creating Tools

### Required Structure

**CRITICAL:** The tool's `--help` output is used to **auto-generate the main README.md and the website**.

- Ensure your tool supports `--help` (standard with `click`).
- **Module Docstring**: Keep the top-level module docstring to a single sentence summary.
- **Main Docstring**: The docstring of your main command function (decorated with `@click.command`) provides the full help description.
- Keep the first line of the main docstring as a clear, concise summary.
- Manually document `@click.argument` arguments in an `Arguments:` section (Click does not auto-document them).
- Include concrete `Examples:` section showing exactly how to run it.
- Do not use generic `Usage:` placeholders.

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click>=8.1.0",
# ]
# ///
"""
A 1-sentence description of the tool.
"""

import click

@click.command()
@click.argument("name")
@click.option("--output", type=click.Path(), default=None, help="Output file (optional)")
def main(name: str, output: str | None) -> None:
    """
    Tool description that will be used to auto-generate the main README.md and the website.

    This docstring is the source of truth for the tool's documentation.
    It should include a detailed description, arguments list, and usage examples.

    Arguments:
        NAME: The name of the person to greet.

    Examples:

        uv run https://tools.ricardodecal.com/python/tool.py arg1
    """
    click.echo(f"Hello, {name}!")
    if output:
        Path(output).write_text(f"Hello {name}")

if __name__ == "__main__":
    main()

```

### Managing Dependencies

**NEVER manually edit the PEP 723 metadata block.** Use `uv` commands:

```shell
# Add dependencies
uv add --script python/foo.py requests rich

# Remove dependencies
uv remove --script python/foo.py rich

# Update Python version requirement
uv add --script python/foo.py --python ">=3.13"
```

This automatically updates the `# /// script` block.

---

## Standard Dependencies

Prefer these well-maintained packages:

- `click` - CLI framework (required for this repo)
- `requests` - HTTP requests
- `rich` - Terminal formatting
- `httpx` - Async HTTP
- `beautifulsoup4` - HTML parsing
- `pydantic` - Data validation

---

## Output Patterns

```python
import click

# Standard output
click.echo("message")

# Colored (optional)
click.secho("Success!", fg="green")
click.secho("Error!", fg="red", err=True)

# Errors
raise click.UsageError("Invalid input")
raise click.ClickException("Operation failed")
```

### Rich Formatting

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()
console.print("[bold green]Success![/bold green]")

table = Table()
table.add_column("Name")
table.add_row("Value")
console.print(table)

for item in track(items, description="Processing..."):
    process(item)
```

---

## Common Patterns

### File I/O

```python
@click.argument("input", type=click.File("r"), default="-")
@click.argument("output", type=click.File("w"), required=False)
def main(input, output):
    if output is None:
        output = open("output.txt", "w")

    for line in input:
        output.write(line.upper())
```

### Path Handling

```python
from pathlib import Path

@click.argument("directory", type=click.Path(exists=True))
@click.option("--output-dir", type=click.Path(), default=".")
def main(directory, output_dir):
    path = Path(directory)
    out = Path(output_dir)
    out.mkdir(exist_ok=True)

    for file in path.glob("*.txt"):
        process(file, out)
```

### HTTP Requests

```python
import requests

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
except requests.RequestException as e:
    raise click.ClickException(f"Request failed: {e}")
```

### JSON Processing

```python
import json

try:
    data = json.load(input_file)
except json.JSONDecodeError as e:
    raise click.ClickException(f"Invalid JSON: {e}")

click.echo(json.dumps(data, indent=2))
```

---

## Anti-Patterns

❌ Using `argparse` instead of `click`
❌ Using `print()` instead of `click.echo()`
❌ Manually editing PEP 723 block (use `uv add --script`)
❌ Forgetting `if __name__ == "__main__":`
❌ No type hints
❌ Silent exception handling
❌ Generic "Usage" in docstring instead of real "Examples"

---

## Workflow

```shell
# Create tool
touch python/foo.py
chmod +x python/foo.py

# Add template and basic code

# Add dependencies
uv add --script python/foo.py click requests

# Test
uv run python/foo.py --help

# Bump dependencies to latest versions
uv remove --script python/foo.py click requests && uv add --script python/foo.py click requests

# Commit
git add python/foo.py
git commit -m "Add foo: description"

# Test from URL after push
uv run https://tools.ricardodecal.com/python/foo.py --help
```

# Python Tools

Python CLI tools runnable with `uv run`, using PEP 723 inline metadata for dependencies.

## Running Tools

```shell
# From GitHub URL (no clone needed)
uv run https://tools.ricardodecal.com/python/foo.py [args]

# Locally
uv run python/foo.py [args]
```

## Available Tools

- `yt_transcript.py`: Fetch YouTube transcripts for a single video or a whole playlist into a single file.

---

## Creating Tools

### Required Structure

**CRITICAL:** The module-level docstring (at the top of the file) is used to **auto-generate the main README.md and the website**.

- Keep the first line as a clear, concise summary.
- Include concrete `Examples:` section showing exactly how to run it (use markdown code blocks).
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
Tool description.

Examples:

```shell
uv run https://tools.ricardodecal.com/python/tool.py arg1
```

"""

import click

@click.command()
@click.argument("name")
def main(name: str) -> None:
    """Help text for --help."""
    click.echo(f"Hello, {name}!")

if **name** == "**main**":
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

## Testing

Create `tests/test_your_tool.py`:

```python
from pathlib import Path
import subprocess

TOOL = Path(__file__).parent.parent / "python" / "foo.py"

def run_tool(*args):
    return subprocess.run(
        ["uv", "run", str(TOOL), *args],
        capture_output=True,
        text=True,
        check=False,
    )

def test_help():
    result = run_tool("--help")
    assert result.returncode == 0
    assert "Usage:" in result.stdout

def test_basic():
    result = run_tool("arg")
    assert result.returncode == 0
```

Run: `uv run pytest tests/test_your_tool.py -v`

See [tests/README.md](../tests/README.md) for details.

---

## Common Patterns

### File I/O

```python
@click.argument("input", type=click.File("r"), default="-")
@click.argument("output", type=click.File("w"), default="-")
def main(input, output):
    for line in input:
        output.write(line.upper())
```

### Path Handling

```python
from pathlib import Path

@click.argument("directory", type=click.Path(exists=True))
def main(directory):
    path = Path(directory)
    for file in path.glob("*.txt"):
        process(file)
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

# Add tests
touch tests/test_my_tool.py
uv run pytest tests/test_my_tool.py -v

# Commit
git add python/foo.py tests/test_my_tool.py
git commit -m "Add foo: description"

# Test from URL after push
uv run https://tools.ricardodecal.com/python/foo.py --help
```

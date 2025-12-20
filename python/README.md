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

- Ensure your tool supports `--help` (standard with `typer`).
- **Module Docstring**: Keep the top-level module docstring to a single sentence summary.
- **Main Docstring**: The docstring of your main function provides the full help description.
- Keep the first line of the main docstring as a clear, concise summary.
- Manually document arguments in an `Arguments:` section (Typer documents them via `help=` in Annotated types).
    - Include concrete `Examples:` section showing exactly how to run it.
    - Separate multiple examples with blank lines to ensure correct formatting in the generated docs.
    - Do not use generic `Usage:` placeholders.

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "typer>=0.15.0",
#     "rich>=13.0.0",
# ]
# ///
"""
A 1-sentence description of the tool.
"""

from pathlib import Path
from typing import Annotated

import typer
from rich import print


def main(
    name: Annotated[str, typer.Argument(help="The name of the person to greet.")],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file (optional)."),
    ] = None,
) -> None:
    """
    Tool description that will be used to auto-generate the main README.md and the website.

    This docstring is the source of truth for the tool's documentation.
    It should include a detailed description, arguments list, and usage examples.

    Arguments:
        NAME: The name of the person to greet.

    Examples:

        uv run https://tools.ricardodecal.com/python/tool.py arg1
    """
    print(f"[green]Hello, {name}![/green]")
    if output:
        output.write_text(f"Hello {name}")


if __name__ == "__main__":
    typer.run(main)

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

- `typer` - CLI framework (required for this repo)
- `rich` - Terminal formatting (included with typer, use for output)
- `requests` - HTTP requests
- `httpx` - Async HTTP
- `beautifulsoup4` - HTML parsing
- `pydantic` - Data validation

---

## Output Patterns

Always import `print` from `rich` at the top of every tool. This shadows the built-in `print` and gives you Rich formatting everywhere:

```python
from rich import print

# All print() calls now support Rich markup
print("Plain message")
print("[green]Success![/green]")
print("[bold red]Error:[/bold red] Something went wrong")

# Errors - use typer.Exit for clean exit codes
print("[bold red]Error:[/bold red] Operation failed")
raise typer.Exit(code=1)
```

### Rich Formatting

```python
from rich import print
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

# All output uses print() - it handles Rich objects too
print("[bold green]Success![/bold green]")

# Tables work with print() directly
table = Table()
table.add_column("Name")
table.add_row("Value")
print(table)

# Progress bar
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    MofNCompleteColumn(),
) as progress:
    task = progress.add_task("Processing...", total=100)
    for i in range(100):
        progress.advance(task)
```

**Note:** Don't use `Console` - just use `print()` for everything. Rich's print handles all Rich objects (Tables, Trees, Panels, etc.).

---

## Common Patterns

### Type Annotations with Typer

```python
from pathlib import Path
from typing import Annotated

import typer

def main(
    # Required argument
    name: Annotated[str, typer.Argument(help="Person's name")],

    # Optional argument with default
    count: Annotated[int, typer.Argument(help="Number of greetings")] = 1,

    # Option with short flag
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file"),
    ] = None,

    # Boolean flag
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,

    # Multiple values
    tags: Annotated[
        list[str] | None,
        typer.Option("--tag", "-t", help="Tags to apply"),
    ] = None,
) -> None:
    ...
```

### Path Handling

```python
from pathlib import Path
from typing import Annotated

import typer

def main(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input file path",
            exists=True,      # File must exist
            dir_okay=False,   # Must be a file, not directory
            resolve_path=True,  # Resolve to absolute path
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir", "-o",
            help="Output directory",
            file_okay=False,  # Must be directory
            resolve_path=True,
        ),
    ] = Path("."),
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for file in input_file.parent.glob("*.txt"):
        process(file, output_dir)
```

### HTTP Requests

```python
import requests
import typer
from rich import print

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
except requests.RequestException as e:
    print(f"[bold red]Error:[/bold red] Request failed: {e}")
    raise typer.Exit(code=1)
```

### JSON Processing

```python
import json
import typer
from rich import print

try:
    data = json.load(input_file)
except json.JSONDecodeError as e:
    print(f"[bold red]Error:[/bold red] Invalid JSON: {e}")
    raise typer.Exit(code=1)

print(json.dumps(data, indent=2))
```

### Confirmations and Prompts

```python
import typer

# Simple confirmation
if not typer.confirm("Are you sure you want to continue?"):
    raise typer.Abort()

# With default
delete = typer.confirm("Delete files?", default=False)

# Prompt for input
name = typer.prompt("What's your name?")
password = typer.prompt("Password", hide_input=True)
```

---

## Anti-Patterns

❌ Using `argparse` instead of `typer`
❌ Using `click` instead of `typer`
❌ Forgetting `from rich import print` at the top
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
uv add --script python/foo.py typer rich requests

# Test
uv run python/foo.py --help

# Bump dependencies to latest versions
uv remove --script python/foo.py typer rich requests && uv add --script python/foo.py typer rich requests

# Commit
git add python/foo.py
git commit -m "Add foo: description"

# Test from URL after push
uv run https://tools.ricardodecal.com/python/foo.py --help
```

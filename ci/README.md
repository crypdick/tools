# CI Custom Hooks

## Hooks

### Python Tools
- `check_executable.py` - Scripts must be executable
- `check_typer_cli.py` - Use `typer`, not `argparse` or `click`
- `check_rich_print.py` - Require `from rich import print`
- `check_main_guard.py` - Require `if __name__ == "__main__":`
- `check_no_any.py` - Ban `typing.Any`

### HTML Tools
- `check_html_metadata.py` - Require frontmatter with category, `<title>`, and `<p class="subtitle">`

## Usage

```shell
# Run all checks
uvx pre-commit run --all-files

# Test individual hook
python ci/check_typer_cli.py python/tool.py
python ci/check_rich_print.py python/tool.py
```

All hooks run automatically via `.pre-commit-config.yaml`.

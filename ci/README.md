# CI Custom Hooks

## Hooks

### Python Tools
- `check_executable.py` - Scripts must be executable
- `check_no_argparse.py` - Use `click`, not `argparse`
- `check_no_print.py` - Use `click.echo()`, not `print()`
- `check_main_guard.py` - Require `if __name__ == "__main__":`
- `check_no_any.py` - Ban `typing.Any`
- `check_help.py` - Ensure scripts support `--help`

### HTML Tools
- `check_html_metadata.py` - Require frontmatter with category, `<title>`, and `<p class="subtitle">`

## Usage

```shell
# Run all checks
uvx pre-commit run --all-files

# Test individual hook
python ci/check_no_argparse.py python/tool.py
```

All hooks run automatically via `.pre-commit-config.yaml`.

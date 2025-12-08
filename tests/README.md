# Tests

## Running Tests

```bash
uv run pytest tests/ -v
```

## Test Pattern

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

Why `uv run`: Installs dependencies from PEP 723 metadata automatically.

## Bash Scripts

```bash
shellcheck bash/script.sh
```

Optional: Use [BATS](https://github.com/bats-core/bats-core) for bash testing.

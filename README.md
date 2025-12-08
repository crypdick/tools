# tools

A collection of command-line utilities and scripts, organized by implementation language. Built to be simple, self-contained, and immediately runnable using `uv run`.

## Quick Start

```bash
# Run a Python tool from URL
uv run https://raw.githubusercontent.com/crypdick/tools/main/python/your-tool.py

# Run locally
git clone https://github.com/crypdick/tools.git
cd tools
uv run python/your-tool.py
```

## Repository Structure

```
tools/
├── python/          # Python CLI tools (see python/README.md)
├── bash/            # Bash scripts (see bash/README.md)
├── lib/             # Shared library code
├── tests/           # Automated tests (see tests/README.md)
└── .github/         # GitHub Actions workflows
```

## Available Tools

<!-- Tools will be listed here as they are added -->

*No tools yet - start by reading [TOOLS_GUIDE.md](TOOLS_GUIDE.md) for opinionated guidance on creating tools.*

## Documentation

- **[TOOLS_GUIDE.md](TOOLS_GUIDE.md)** - Opinionated guide on building tools for this repository
- **[python/README.md](python/README.md)** - Python tool patterns and templates
- **[bash/README.md](bash/README.md)** - Bash script patterns and templates
- **[tests/README.md](tests/README.md)** - Testing guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## Prerequisites

- Python 3.12+ for Python tools
- [uv](https://github.com/astral-sh/uv) for running Python tools
- Bash 4.0+ for shell scripts

## Philosophy

- **Self-contained**: Single-file tools when possible
- **Immediately runnable**: `uv run` works without setup
- **Well-documented**: Clear usage instructions and examples
- **Simple**: Prefer simplicity over cleverness
- **Tested**: All tools validated via CI/CD

## License

Apache 2.0 - See [LICENSE](LICENSE)

## Inspiration

Inspired by [Simon Willison's tools collection](https://github.com/simonw/tools).

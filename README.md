# Ricardo Decal's Tools

A collection of command-line utilities and scripts, organized by implementation language. Built to be simple, self-contained, and immediately runnable using `uv run`.

> **Note**: Most of these tools are "vibe coded" but verified for functionality.

## Quick Start

Using `uv run` creates an ephemeral Python environment for execution, so these tools won't pollute your system's global Python packages.

```bash
# Run a Python tool from URL
uv run https://tools.ricardodecal.com/python/foo.py

# Run locally
git clone https://github.com/crypdick/tools.git
cd tools
uv run python/foo.py
```

## Available Tools

<!-- Tools will be listed here as they are added -->

- **[yt_transcript.py](python/yt_transcript.py)**
  Fetch YouTube transcripts for a single video or a whole playlist.
  `uv run https://tools.ricardodecal.com/python/yt_transcript.py https://www.youtube.com/watch?v=jNQXAC9IVRw`

## Documentation

- **[TOOLS_GUIDE.md](TOOLS_GUIDE.md)** - Opinionated guide on building tools for this repository
- **[python/README.md](python/README.md)** - Python tool patterns and templates
- **[bash/README.md](bash/README.md)** - Bash script patterns and templates
- **[tests/README.md](tests/README.md)** - Testing guide

## Prerequisites

- Python 3.12+ for Python tools
- [uv](https://github.com/astral-sh/uv) for running Python tools
- Bash 4.0+ for shell scripts

## Philosophy

- **Self-contained**: Single-file tools when possible
- **Immediately runnable**: `uv run` works without setup and without polluting your system's global Python packages.

## License

Apache 2.0 - See [LICENSE](LICENSE)

## Inspiration

Inspired by [Simon Willison's tools collection](https://github.com/simonw/tools).

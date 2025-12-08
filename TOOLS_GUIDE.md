# Tools Guide

## Python Tools

### `yt_transcript.py`

Fetch YouTube transcripts for a single video or a whole playlist into a single flat text file.

**Usage:**

```bash
uv run python/yt_transcript.py [URL] [OUTPUT_FILE]
```

**Options:**

- `-l, --lang`: Language codes to prefer (default: en, en-US, en-GB). Can be used multiple times.

**Example:**

```bash
uv run python/yt_transcript.py "https://www.youtube.com/playlist?list=PL..." transcript.txt
```

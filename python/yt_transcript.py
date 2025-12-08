#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "youtube-transcript-api",
#     "yt-dlp",
# ]
# ///
"""
Fetch YouTube transcripts for a single video or a whole playlist into a single flat text file.

Examples:

```shell
uv run https://tools.ricardodecal.com/python/yt_transcript.py "https://youtu.be/..." out.txt
uv run https://tools.ricardodecal.com/python/yt_transcript.py "https://youtube.com/playlist?list=..." out.txt
```

Options:

- `-l, --lang TEXT`: Language codes to prefer (default: en, en-US, en-GB). Can be used multiple times (e.g. `-l en -l fr`).
"""

# mypy: ignore-errors

import sys
from pathlib import Path

import click
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)
from yt_dlp import YoutubeDL


def get_video_list(url: str) -> list[dict[str, str | None]]:
    """
    Return a list of video dictionaries (id, title) from the URL.
    Handles both single videos and playlists.
    """
    ydl_opts = {
        "quiet": True,
        "ignoreerrors": True,
        "extract_flat": True,
        "noplaylist": False,  # Allow playlist extraction if available
    }

    videos: list[dict[str, str | None]] = []
    try:
        with YoutubeDL(ydl_opts) as ydl:
            click.echo(f"Fetching metadata for {url}...")
            info = ydl.extract_info(url, download=False)

            if not info:
                raise click.ClickException("Could not fetch video info.")

            if "entries" in info:
                # It's a playlist or channel
                click.echo(f"Found playlist: {info.get('title', 'Unknown')}")
                entries = info["entries"]
                for e in entries:
                    if e:
                        videos.append(
                            {
                                "id": e.get("id"),
                                "title": e.get("title", "Unknown Title"),
                            }
                        )
            else:
                # Single video
                videos.append(
                    {"id": info.get("id"), "title": info.get("title", "Unknown Title")}
                )
    except Exception as e:
        raise click.ClickException(f"Error fetching metadata: {e}") from e

    return videos


def get_transcript_text(
    video_id: str, languages: list[str] | None = None
) -> str | None:
    """
    Return the plain text transcript for a single video, or None if unavailable.
    """
    if languages is None:
        languages = ["en", "en-US", "en-GB"]

    try:
        # Newer versions of the API use instance methods
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=languages)
        # FetchedTranscript object has 'snippets' list of FetchedTranscriptSnippet
        segments = [{"text": s.text} for s in fetched.snippets]
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        click.echo(f"Error fetching transcript for {video_id}: {e}", err=True)
        return None

    # Concatenate all text segments
    lines = [seg["text"].strip() for seg in segments if seg["text"].strip()]
    return "\n".join(lines)


@click.command()
@click.argument("url")
@click.argument("output_file", type=click.Path(writable=True, path_type=Path))
@click.option(
    "--lang",
    "-l",
    multiple=True,
    default=["en", "en-US", "en-GB"],
    help="Language codes to prefer (e.g. -l en -l fr)",
)
def main(url: str, output_file: Path, lang: list[str]) -> None:
    """
    Download transcripts from a YouTube URL (video or playlist) to a single file.

    URL: YouTube video or playlist URL.
    OUTPUT_FILE: Path to save the transcript text.

    Options:

    - `--lang, -l`: Language codes to prefer (e.g. `-l en -l fr`). Default: `en`, `en-US`, `en-GB`

    Examples:

    ```shell
    uv run https://tools.ricardodecal.com/python/yt_transcript.py "https://youtu.be/..." out.txt

    uv run https://tools.ricardodecal.com/python/yt_transcript.py "https://youtube.com/playlist?list=..." out.txt
    ```
    """
    videos = get_video_list(url)

    if not videos:
        click.echo("No videos found.")
        return

    click.echo(f"Found {len(videos)} video(s). Processing...")

    parts = []
    success_count = 0

    with click.progressbar(videos, label="Fetching transcripts") as bar:
        for i, video in enumerate(bar, start=1):
            vid = video["id"]
            title = video["title"]

            if not vid:
                continue

            txt = get_transcript_text(vid, languages=list(lang))

            if txt:
                # Add a clear separator
                header = f"\n\n===== VIDEO {i}: {title} ({vid}) =====\n\n"
                parts.append(header + txt)
                success_count += 1
            # We don't print "skipping" inside the progress bar to avoid clutter,
            # unless we want to use bar.update with item_show_func

    if not parts:
        click.secho("No transcripts were found for any videos.", fg="yellow")
        sys.exit(1)

    full_text = "".join(parts)
    # Strip leading newlines from the first header
    full_text = full_text.lstrip()

    output_file.write_text(full_text, encoding="utf-8")
    click.secho(
        f"\nSuccessfully wrote {success_count} transcripts to {output_file}", fg="green"
    )


if __name__ == "__main__":
    main()

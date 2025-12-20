#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# category = "data"
# dependencies = [
#     "typer>=0.15.0",
#     "rich>=13.0.0",
#     "youtube-transcript-api",
#     "yt-dlp",
# ]
# ///
"""
Fetch YouTube transcripts for a single video or a whole playlist into a single flat text file.

Examples:
    uv run python/yt_transcript.py "https://youtu.be/..." out.txt
    uv run python/yt_transcript.py "https://youtube.com/playlist?list=..." out.txt
"""

# mypy: ignore-errors

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn
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
            print(f"Fetching metadata for {url}...")
            info = ydl.extract_info(url, download=False)

            if not info:
                print("[bold red]Error:[/bold red] Could not fetch video info.")
                raise typer.Exit(code=1)

            if "entries" in info:
                # It's a playlist or channel
                print(f"Found playlist: {info.get('title', 'Unknown')}")
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
    except typer.Exit:
        raise
    except Exception as e:
        print(f"[bold red]Error:[/bold red] fetching metadata: {e}")
        raise typer.Exit(code=1)

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
        print(f"[dim]Error fetching transcript for {video_id}: {e}[/dim]", file=sys.stderr)
        return None

    # Concatenate all text segments
    lines = [seg["text"].strip() for seg in segments if seg["text"].strip()]
    return "\n".join(lines)


def main(
    url: Annotated[str, typer.Argument(help="YouTube video or playlist URL.")],
    output_file: Annotated[
        Path | None,
        typer.Argument(
            help="Path to save the transcript text. Defaults to transcript.txt.",
            resolve_path=True,
        ),
    ] = None,
    lang: Annotated[
        list[str] | None,
        typer.Option(
            "--lang",
            "-l",
            help="Language codes to prefer (e.g. -l en -l fr)",
        ),
    ] = None,
) -> None:
    """
    Download transcripts from a YouTube URL (video or playlist) to a single file.

    Arguments:
        URL: YouTube video or playlist URL.
        OUTPUT_FILE: Path to save the transcript text. Defaults to transcript.txt.

    Examples:

        uv run python/yt_transcript.py "https://youtu.be/..."

        uv run python/yt_transcript.py "https://youtube.com/playlist?list=..." out.txt
    """
    if lang is None:
        lang = ["en", "en-US", "en-GB"]

    if output_file is None:
        output_file = Path.cwd() / "transcript.txt"

    videos = get_video_list(url)

    if not videos:
        print("[yellow]No videos found.[/yellow]")
        return

    print(f"Found {len(videos)} video(s). Processing...")

    parts = []
    success_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
    ) as progress:
        task = progress.add_task("Fetching transcripts", total=len(videos))

        for i, video in enumerate(videos, start=1):
            vid = video["id"]
            title = video["title"]

            if not vid:
                progress.advance(task)
                continue

            txt = get_transcript_text(vid, languages=list(lang))

            if txt:
                # Add a clear separator
                header = f"\n\n===== VIDEO {i}: {title} ({vid}) =====\n\n"
                parts.append(header + txt)
                success_count += 1

            progress.advance(task)

    if not parts:
        print("[yellow]No transcripts were found for any videos.[/yellow]")
        sys.exit(1)

    full_text = "".join(parts)
    # Strip leading newlines from the first header
    full_text = full_text.lstrip()

    output_file.write_text(full_text, encoding="utf-8")
    print(
        f"\n[green]Successfully wrote {success_count} transcripts to {output_file}[/green]"
    )


if __name__ == "__main__":
    typer.run(main)

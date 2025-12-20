#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# category = "data"
# dependencies = [
#     "typer>=0.15.0",
#     "rich>=13.0.0",
#     "yt-dlp",
# ]
# ///
"""
Download videos from various platforms (Twitter/X, YouTube, etc.).
"""

import os
from pathlib import Path
from typing import Annotated

import typer
import yt_dlp
from rich import print


def main(
    url: Annotated[str, typer.Argument(help="The URL of the video page.")],
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Output filepath (file or directory). Defaults to 'Title [ID].mp4' in current directory.",
        ),
    ] = None,
) -> None:
    """
    Download a video from a supported platform (Twitter/X, YouTube, etc.).

    Uses yt-dlp to download videos from a wide variety of websites.
    Twitter "GIFs" are actually MP4 videos, which this tool can also download.

    Arguments:

        URL: The URL of the video page (e.g., Twitter post, YouTube video).

    Examples:

        uv run python/download_video.py https://x.com/SemiAnalysis_/status/1990449859321888935

        uv run python/download_video.py https://www.youtube.com/watch?v=dQw4w9WgXcQ --output my_video.mp4
    """
    ydl_opts: dict[str, object] = {
        "format": "best",
        # Default filename format: Title (truncated) [ID].extension
        "outtmpl": "%(title).100s [%(id)s].%(ext)s",
        "quiet": False,
        "no_warnings": True,
    }

    if output:
        # Expand user path (~) and resolve absolute path
        output_path = Path(output).expanduser().resolve()

        if output_path.is_dir() or output.endswith(os.sep):
            # If it's a directory (existing or ends with slash), save there with default filename
            # Create directory if it doesn't exist and ends with separator
            if output.endswith(os.sep):
                output_path.mkdir(parents=True, exist_ok=True)

            ydl_opts["paths"] = {"home": str(output_path)}
        else:
            # It's a file path
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            ydl_opts["outtmpl"] = str(output_path)

    try:
        print(f"Downloading from {url}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"[green]Success![/green] Saved to: {filename}")

    except Exception as e:
        print(f"[bold red]Error:[/bold red] Failed to download: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)

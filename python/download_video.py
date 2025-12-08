#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click>=8.1.0",
#     "yt-dlp",
# ]
# ///
"""
Download videos from various platforms (Twitter/X, YouTube, etc.).
"""

import click
import yt_dlp


@click.command()
@click.argument("url")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output filename (optional). Defaults to 'Title [ID].mp4'",
)
def main(url: str, output: str | None) -> None:
    """
    Download a video from a supported platform (Twitter/X, YouTube, etc.).

    Uses yt-dlp to download videos from a wide variety of websites.
    Twitter "GIFs" are actually MP4 videos, which this tool can also download.

    Arguments:

        URL: The URL of the video page (e.g., Twitter post, YouTube video).

    Examples:

        uv run python/download_video.py https://x.com/SemiAnalysis_/status/1990449859321888935
        uv run python/download_video.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
    """
    ydl_opts = {
        "format": "best",
        # Default filename format: Title (truncated) [ID].extension
        "outtmpl": "%(title).100s [%(id)s].%(ext)s",
        "quiet": False,
        "no_warnings": True,
    }

    if output:
        ydl_opts["outtmpl"] = output

    try:
        click.echo(f"Downloading from {url}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            click.secho(f"Success! Saved to: {filename}", fg="green")

    except Exception as e:
        raise click.ClickException(f"Failed to download: {e}") from e


if __name__ == "__main__":
    main()

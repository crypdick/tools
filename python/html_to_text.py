#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# category = "data"
# dependencies = [
#     "click>=8.1.0",
#     "requests",
#     "inscriptis",
# ]
# ///
"""
Fetch a webpage and convert its content to plain text.
"""

import re
from urllib.parse import urlparse

import click
import requests
from inscriptis import get_text


def normalize_url(url: str) -> str:
    """Normalize a URL by adding https:// scheme if missing."""
    parsed = urlparse(url)
    if not parsed.scheme:
        return f"https://{url}"
    return url


def fetch_url(url: str, timeout: int) -> str:
    """Fetch a URL and return HTML text."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; html_to_text/1.0)"}
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text


def html_to_text(html: str) -> str:
    """Convert HTML to trimmed text via Inscriptis."""
    text = get_text(html)
    return text.strip()


def clean_text(text: str) -> str:
    """Collapse whitespace and blank lines in the rendered text."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()


@click.command()
@click.argument("url")
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=15,
    help="Request timeout in seconds.",
)
@click.option(
    "--raw",
    is_flag=True,
    help="Skip whitespace cleanup (preserve original formatting).",
)
def main(url: str, timeout: int, raw: bool) -> None:
    """
    Fetch a webpage and convert its readable content to plain text.

    Uses inscriptis to extract text from HTML while preserving basic structure.
    Automatically adds https:// if no scheme is provided.

    Arguments:

        URL: The webpage URL to fetch (e.g., example.com or https://example.com).

    Examples:

        uv run https://tools.ricardodecal.com/python/html_to_text.py example.com

        uv run https://tools.ricardodecal.com/python/html_to_text.py https://news.ycombinator.com --timeout 30

        uv run https://tools.ricardodecal.com/python/html_to_text.py wikipedia.org/wiki/Python --raw
    """
    target_url = normalize_url(url)

    try:
        html = fetch_url(target_url, timeout=timeout)
    except requests.RequestException as e:
        raise click.ClickException(f"Failed to fetch {target_url}: {e}") from e

    try:
        text = html_to_text(html)
    except Exception as e:
        raise click.ClickException(f"Failed to convert HTML to text: {e}") from e

    if not raw:
        text = clean_text(text)

    click.echo(text)


if __name__ == "__main__":
    main()

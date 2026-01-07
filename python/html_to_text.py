#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# category = "data"
# dependencies = [
#     "typer>=0.15.0",
#     "rich>=13.0.0",
#     "requests",
#     "inscriptis",
#     "readability-lxml",
#     "beautifulsoup4",
#     "lxml",
# ]
# ///
"""
Fetch a webpage and convert its content to plain text.
"""

import os
import re
import sys
from enum import StrEnum
from typing import Annotated
from urllib.parse import urlparse

import requests
import typer
from bs4 import BeautifulSoup
from inscriptis import get_text
from readability import Document
from rich import print


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
    # Respect server-declared encoding when present; apparent_encoding can be wrong.
    if response.encoding is None:
        response.encoding = response.apparent_encoding
    return response.text


class ExtractMode(StrEnum):
    auto = "auto"
    readability = "readability"
    heuristic = "heuristic"
    full = "full"


def html_to_text(html: str) -> str:
    """Convert HTML to trimmed text via Inscriptis."""
    return get_text(html).strip()


def extract_html_readability(html: str) -> str | None:
    """
    Extract main content HTML using Readability (boilerplate removal).

    Returns None if extraction fails or yields an empty result.
    """
    try:
        doc = Document(html)
        summary = doc.summary(html_partial=True)
    except Exception:
        return None

    if not summary or not summary.strip():
        return None
    return summary


def extract_html_heuristic(html: str) -> str | None:
    """
    Extract main-ish content HTML using semantic tags and light boilerplate removal.

    This is intentionally conservative: if we can't find a clear main container,
    we return the cleaned <body> (or whole document) rather than guessing.
    """
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        return None

    # Drop non-content / boilerplate containers that are rarely useful in plain text.
    for tag in soup.find_all(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "canvas",
            "iframe",
            "form",
            "nav",
            "header",
            "footer",
            "aside",
        ]
    ):
        tag.decompose()

    # Prefer explicit "main content" containers.
    candidate = (
        soup.find("main")
        or soup.find("article")
        or soup.find(attrs={"role": "main"})
        or soup.find(id="mw-content-text")  # common on Wikipedia
        or soup.find(id="content")
    )

    if candidate is None:
        candidate = soup.body or soup

    rendered = str(candidate)
    if not rendered.strip():
        return None
    return rendered


def extract_html_auto(
    html: str,
    *,
    min_chars: int,
    min_ratio: float,
) -> str:
    """
    Auto-select the best extraction strategy with conservative fallbacks.

    - Try Readability
    - Fallback to a heuristic main-container extraction
    - Fallback to full HTML
    """
    full_text = html_to_text(html)
    full_len = len(full_text)

    # 1) Readability
    readable_html = extract_html_readability(html)
    if readable_html is not None:
        readable_text = html_to_text(readable_html)
        if len(readable_text) >= min_chars and (
            full_len == 0 or (len(readable_text) / full_len) >= min_ratio
        ):
            return readable_html

    # 2) Heuristic
    heuristic_html = extract_html_heuristic(html)
    if heuristic_html is not None:
        heuristic_text = html_to_text(heuristic_html)
        if len(heuristic_text) >= min_chars and (
            full_len == 0 or (len(heuristic_text) / full_len) >= min_ratio
        ):
            return heuristic_html

    # 3) Full
    return html


def clean_text(text: str) -> str:
    """Collapse whitespace and blank lines in the rendered text."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()


def write_output(text: str) -> None:
    """Write output to stdout, exiting cleanly on broken pipes (e.g. piping to head)."""
    try:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()
    except BrokenPipeError:
        os._exit(0)


def main(
    url: Annotated[str, typer.Argument(help="The webpage URL to fetch.")],
    timeout: Annotated[
        int, typer.Option("--timeout", "-t", help="Request timeout in seconds.")
    ] = 15,
    mode: Annotated[
        ExtractMode,
        typer.Option(
            "--mode",
            "-m",
            help=(
                "Extraction mode: auto (default), readability (boilerplate removal), "
                "heuristic (semantic tags), or full (whole page)."
            ),
        ),
    ] = ExtractMode.auto,
    min_chars: Annotated[
        int,
        typer.Option(
            "--min-chars",
            help="Minimum extracted text length to accept before falling back (auto mode).",
            min=0,
        ),
    ] = 200,
    min_ratio: Annotated[
        float,
        typer.Option(
            "--min-ratio",
            help="Minimum extracted/full text length ratio to accept before falling back (auto mode).",
            min=0.0,
            max=1.0,
        ),
    ] = 0.2,
    raw: Annotated[
        bool,
        typer.Option(
            "--raw", help="Skip whitespace cleanup (preserve original formatting)."
        ),
    ] = False,
) -> None:
    """
    Fetch a webpage and convert its readable content to plain text.

    Uses Readability-style boilerplate removal by default, with conservative fallbacks.
    Then uses inscriptis to render HTML to text while preserving basic structure.
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
        print(f"[bold red]Error:[/bold red] Failed to fetch {target_url}: {e}")
        raise typer.Exit(code=1) from e

    try:
        extracted_html: str
        if mode == ExtractMode.full:
            extracted_html = html
        elif mode == ExtractMode.readability:
            extracted_html = extract_html_readability(html) or html
        elif mode == ExtractMode.heuristic:
            extracted_html = extract_html_heuristic(html) or html
        else:
            extracted_html = extract_html_auto(
                html,
                min_chars=min_chars,
                min_ratio=min_ratio,
            )

        text = html_to_text(extracted_html)
    except Exception as e:
        print(f"[bold red]Error:[/bold red] Failed to convert HTML to text: {e}")
        raise typer.Exit(code=1) from e

    if not raw:
        text = clean_text(text)

    write_output(text)


if __name__ == "__main__":
    typer.run(main)

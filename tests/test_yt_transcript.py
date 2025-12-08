import subprocess
from pathlib import Path

TOOL = Path(__file__).parent.parent / "python" / "yt_transcript.py"


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
    assert "Download transcripts" in result.stdout

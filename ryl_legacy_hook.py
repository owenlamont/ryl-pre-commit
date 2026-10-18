import os
from pathlib import Path
import subprocess  # ruff: ignore[suspicious-subprocess-import]
import sys
import sysconfig


def _run(markdown: bool) -> int:
    legacy_id = "ryl-markdown" if markdown else "ryl"
    replacement = "ryl-check-markdown" if markdown else "ryl-check"
    print(
        f"warning: hook id `{legacy_id}` is deprecated; use `{replacement}` instead",
        file=sys.stderr,
    )
    ryl = Path(sysconfig.get_path("scripts")) / (
        "ryl.exe" if os.name == "nt" else "ryl"
    )
    args = [str(ryl), "check"]
    if markdown:
        args.append("--markdown")
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [*args, *sys.argv[1:]], check=False
    )
    return result.returncode


def _yaml() -> int:
    return _run(markdown=False)


def _markdown() -> int:
    return _run(markdown=True)

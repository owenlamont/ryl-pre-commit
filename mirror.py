# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "packaging==23.2",
#   "urllib3==2.2.1",
# ]
# ///
"""Update ryl-pre-commit to mirror the latest ryl release."""

from __future__ import annotations

from collections.abc import Sequence
import os
from pathlib import Path
import re
import subprocess  # noqa: S404
import time

from packaging.requirements import Requirement
from packaging.version import InvalidVersion, Version
import tomllib
import urllib3


def main() -> None:
    """Update this repository to track mirrored ryl releases."""
    pyproject = _load_pyproject()
    current_version = _current_ryl_version(pyproject)
    dispatch_version = _dispatch_version()
    if dispatch_version is not None:
        if dispatch_version <= current_version:
            print(
                "Dispatch requested version"
                f" {dispatch_version}, current is {current_version}; no change needed."
            )
            return
        _wait_for_pypi_release(dispatch_version)
        versions = [dispatch_version]
    else:
        versions = _available_versions()

    for version in versions:
        if version <= current_version:
            continue
        changed_paths = _update_files(version)
        if _git_has_changes():
            _git_commit_and_tag(version, changed_paths)
        else:
            print(f"No change v{version}")


def _load_pyproject() -> dict:
    with Path(Path(__file__).parent / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def _available_versions() -> list[Version]:
    response = urllib3.request("GET", "https://pypi.org/pypi/ryl/json")
    if response.status != 200:
        raise RuntimeError("Failed to fetch versions from PyPI")
    releases = response.json()["releases"]
    versions = [Version(release) for release in releases]
    return sorted(versions)


def _dispatch_version() -> Version | None:
    raw = os.getenv("DISPATCH_VERSION", "").strip()
    if not raw:
        return None

    normalized = raw.removeprefix("v")
    try:
        return Version(normalized)
    except InvalidVersion as exc:
        raise RuntimeError(f"Invalid DISPATCH_VERSION: {raw}") from exc


def _git_has_changes() -> bool:
    return bool(subprocess.check_output(["git", "status", "-s"]).strip())  # noqa: S607


def _git_commit_and_tag(version: Version, changed_paths: Sequence[str]) -> None:
    subprocess.run(["git", "add", *changed_paths], check=True)  # noqa: S603,S607
    subprocess.run(  # noqa: S603
        ["git", "commit", "-m", f"Mirror: {version}"],  # noqa: S607
        check=True,
    )
    subprocess.run(["git", "tag", f"v{version}"], check=True)  # noqa: S603,S607


def _wait_for_pypi_release(
    version: Version, max_wait_seconds: int = 300, poll_interval_seconds: int = 15
) -> None:
    url = f"https://pypi.org/pypi/ryl/{version}/json"
    elapsed = 0

    while elapsed <= max_wait_seconds:
        response = urllib3.request("GET", url)
        if response.status == 200:
            print(f"Version {version} is available on PyPI.")
            return
        if response.status != 404:
            raise RuntimeError(
                "Unexpected PyPI response while waiting for"
                f" {version}: HTTP {response.status}"
            )
        if elapsed == max_wait_seconds:
            break
        print(f"Waiting for ryl {version} on PyPI ({elapsed}s/{max_wait_seconds}s)...")
        time.sleep(poll_interval_seconds)
        elapsed += poll_interval_seconds

    raise RuntimeError(
        f"Timed out waiting for ryl {version} on PyPI after {max_wait_seconds}s."
    )


def _current_ryl_version(pyproject: dict) -> Version:
    dependencies = pyproject["project"]["dependencies"]
    requirement: Requirement | None = None
    for dependency in dependencies:
        parsed = Requirement(dependency)
        if parsed.name == "ryl":
            requirement = parsed
            break
    if requirement is None:
        raise AssertionError("pyproject.toml must declare a dependency on ryl")

    specifiers = list(requirement.specifier)
    if len(specifiers) != 1 or specifiers[0].operator != "==":
        raise AssertionError(f"ryl specifier must pin to exact version: {requirement}")
    return Version(specifiers[0].version)


def _update_files(version: Version) -> Sequence[str]:
    files = {
        "pyproject.toml": lambda content: re.sub(
            r'"ryl==[^"]+"', f'"ryl=={version}"', content
        ),
        "README.md": lambda content: re.sub(
            r"rev: v\d+\.\d+\.\d+", f"rev: v{version}", content
        ),
    }

    touched: list[str] = []
    for path, replace in files.items():
        file_path = Path(path)
        original = file_path.read_text()
        updated = replace(original)
        if updated != original:
            file_path.write_text(updated)
            touched.append(path)
    return tuple(touched)


if __name__ == "__main__":
    main()

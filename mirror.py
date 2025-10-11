# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "packaging==23.2",
#   "urllib3==2.2.1",
# ]
# ///
"""Update ryl-pre-commit to mirror the latest ryl release."""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path
from typing import Sequence

import urllib3
from packaging.requirements import Requirement
from packaging.version import Version


def main() -> None:
    pyproject = _load_pyproject()
    current_version = _current_ryl_version(pyproject)
    for version in _available_versions():
        if version <= current_version:
            continue
        changed_paths = _update_files(version)
        if subprocess.check_output(["git", "status", "-s"]).strip():
            subprocess.run(["git", "add", *changed_paths], check=True)
            subprocess.run(["git", "commit", "-m", f"Mirror: {version}"], check=True)
            subprocess.run(["git", "tag", f"v{version}"], check=True)
        else:
            print(f"No change v{version}")


def _load_pyproject() -> dict:
    with open(Path(__file__).parent / "pyproject.toml", "rb") as handle:
        return tomllib.load(handle)


def _available_versions() -> list[Version]:
    response = urllib3.request("GET", "https://pypi.org/pypi/ryl/json")
    if response.status != 200:
        raise RuntimeError("Failed to fetch versions from PyPI")
    releases = response.json()["releases"]
    versions = [Version(release) for release in releases]
    return sorted(versions)


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

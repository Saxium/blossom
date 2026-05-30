import os
import re
import shutil
import subprocess
from pathlib import Path

import nox


def _python_version(name: str) -> tuple[str, str, tuple[int, int, int]] | None:
    path = shutil.which(name)
    if not path:
        return None
    resolved = str(Path(path).resolve())
    result = subprocess.run(
        [path, "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    version_text = result.stdout.strip() or result.stderr.strip()
    match = re.search(r"Python\s+(\d+)\.(\d+)\.(\d+)", version_text)
    if not match:
        return None
    version = tuple(int(part) for part in match.groups())
    return name, resolved, version


def discover_python_versions() -> list[str]:
    """Return all available Python 3 interpreters on the host."""
    pattern = re.compile(r"^python3(?:\.[0-9]+)*$")
    seen: dict[str, tuple[str, tuple[int, int, int]]] = {}
    candidates: set[str] = set()

    for path_dir in os.environ.get("PATH", os.defpath).split(os.pathsep):
        try:
            for entry in Path(path_dir).iterdir():
                if not entry.is_file() or not os.access(entry, os.X_OK):
                    continue
                if pattern.match(entry.name):
                    candidates.add(entry.name)
        except FileNotFoundError:
            continue

    if shutil.which("python3"):
        candidates.add("python3")

    for candidate in sorted(candidates):
        info = _python_version(candidate)
        if not info:
            continue
        name, resolved, version = info
        if resolved in seen:
            existing_name, existing_version = seen[resolved]
            if existing_name != "python3" and name == "python3":
                seen[resolved] = (name, version)
            continue
        seen[resolved] = (name, version)

    if not seen:
        raise RuntimeError("No Python 3 interpreter found on this host")

    versions = sorted(
        seen.values(),
        key=lambda item: item[1],
        reverse=True,
    )
    return [name for name, _ in versions]


PYTHON_VERSIONS = discover_python_versions()


@nox.session(python=PYTHON_VERSIONS)
def pytest(session: nox.Session) -> None:
    """Run the test suite with pytest."""
    session.install("pytest")
    session.run("pytest", *session.posargs or ["-q"])


@nox.session(python=PYTHON_VERSIONS)
def pylint(session: nox.Session) -> None:
    """Run static analysis with pylint."""
    session.install("pylint", "pytest")
    session.run("pylint", "blossom.py", "test_blossom.py")


@nox.session(python=PYTHON_VERSIONS)
def mypy(session: nox.Session) -> None:
    """Run type checking with mypy."""
    session.install("mypy")
    session.run("mypy", "--strict", "blossom.py")

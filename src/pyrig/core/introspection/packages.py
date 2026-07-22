"""Utilities for Python packages."""

from collections.abc import Iterable
from pathlib import Path

import typer

from pyrig.core.strings import write_text_utf8


def make_init_files(paths: Iterable[Path], content: str) -> tuple[Path, ...]:
    """Create `__init__.py` files in the given directories.

    Skips any directory that already has an `__init__.py`.

    Args:
        paths: Paths of directories to initialize as packages.
        content: Content to write into each `__init__.py` file.

    Returns:
        Tuple of paths where `__init__.py` files were created.
        Empty if all already existed.
    """
    return tuple(
        path
        for path, created in (make_init_file(path, content) for path in paths)
        if created
    )


def make_package_dir(path: Path, root: Path, content: str) -> None:
    """Create a directory tree and mark it as packages with `__init__.py` files.

    Create `path` and any missing parents, then write an `__init__.py` into
    `path` and each ancestor up to and including `root`. Existing `__init__.py`
    files are left unchanged.

    Args:
        path: Directory to create and mark as a package.
        root: Directory at which to stop, which must be an ancestor of
            `path` (or `path` itself). It receives an `__init__.py`;
            directories above it are left untouched.
        content: Text written into each newly created `__init__.py`.
    """
    relative = path.relative_to(root)
    path.mkdir(parents=True, exist_ok=True)
    for p in (relative, *relative.parents):
        _path, _created = make_init_file(root / p, content=content)


def make_init_file(path: Path, content: str) -> tuple[Path, bool]:
    """Create an `__init__.py` file in the specified directory.

    No-op if `__init__.py` already exists in the directory.

    Args:
        path: Directory path where `__init__.py` should be created.
        content: Content to write into the `__init__.py` file.

    Returns:
        `True` if the file was created, `False` if it already existed.
    """
    path = path / "__init__.py"

    if path.exists():
        return path, False

    write_text_utf8(path, content)
    typer.echo(f"Created: {path}")
    return path, True

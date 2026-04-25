"""Utilities for creating, importing, and traversing Python packages."""

import logging
import sys
from collections.abc import Generator, Iterable
from functools import cache
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from types import ModuleType

import typer

import pyrig
from pyrig.core.introspection.classes import discover_all_subclasses
from pyrig.core.introspection.modules import import_module_with_default, iter_modules
from pyrig.core.strings import snake_to_kebab_case, write_text_utf8

logger = logging.getLogger(__name__)


def make_package_dir(path: Path, until: tuple[Path, ...], content: str) -> None:
    """Create a directory and add ``__init__.py`` files up the directory tree.

    Creates the target directory (and all missing parents), then places
    ``__init__.py`` files in the target directory and each ancestor up the
    tree. Traversal stops at the first ancestor that appears in ``until`` or
    matches the current working directory. This ensures the full path is
    importable as a Python package hierarchy.

    Args:
        path: Directory path to create.
        until: Tuple of directory paths at which to stop adding
            ``__init__.py`` files. Directories in this tuple will not
            receive an ``__init__.py``. The current working directory is
            always implicitly included.
        content: Content to write into each ``__init__.py`` file.

    Note:
        Directories that already contain an ``__init__.py`` are skipped.
    """
    path.mkdir(parents=True, exist_ok=True)
    until = (*until, Path(), Path.cwd())
    for p in (path, *path.parents):
        if p in until:
            break
        make_init_file(p, content=content)


def make_init_file(path: Path, content: str) -> None:
    """Create an ``__init__.py`` file in the specified directory.

    Prints the created path to stdout. No-op if ``__init__.py`` already
    exists in the directory.

    Args:
        path: Directory path where ``__init__.py`` should be created.
        content: Content to write into the ``__init__.py`` file.
    """
    path = path / "__init__.py"

    if path.exists():
        return

    typer.echo(f"Creating: {path}")

    write_text_utf8(path, content)


def src_package_is_pyrig() -> bool:
    """Check if the current project is pyrig itself.

    Returns ``True`` when pyrig is being run from its own development
    repository rather than as an installed dependency in another project.

    Returns:
        True if the current working directory is named ``pyrig``.

    Examples:
        >>> if src_package_is_pyrig():
        ...     print("Running in pyrig development mode")
    """
    return src_package_is_package(pyrig)


@cache
def src_package_is_package(package: ModuleType) -> bool:
    """Check if the given module is the top-level package of the current project.

    Compares the current working directory name against the kebab-case form
    of the module name. For example, if the CWD is ``/home/user/my-project``
    and ``package.__name__`` is ``"my_project"``, this returns ``True``.

    Args:
        package: The module to check.

    Returns:
        True if the current working directory is named after this package.
    """
    return Path.cwd().name == snake_to_kebab_case(package.__name__)


def import_package_with_dir_fallback(path: Path, name: str) -> ModuleType:
    """Import a package by name, falling back to a direct directory import if needed.

    Uses a two-stage strategy:

    1. Attempts a standard import via ``import_module_with_default``.
    2. If the module is not found, falls back to importing directly from
       the directory at ``path`` via ``import_package_from_dir``.

    The fallback handles packages not yet registered in ``sys.modules``,
    such as dynamically created packages or packages in non-standard locations.

    Args:
        path: Path to the package directory. Resolved to an absolute path
            before the fallback import is attempted.
        name: Dotted module name for the package (e.g., ``"myproject.utils"``).

    Returns:
        Imported package module.

    Raises:
        FileNotFoundError: If the fallback import fails because the directory
            or its ``__init__.py`` does not exist.
    """
    path = path.resolve()
    package = import_module_with_default(name)
    if isinstance(package, ModuleType):
        return package
    return import_package_from_dir(path, name)


def import_package_from_dir(path: Path, name: str) -> ModuleType:
    """Import a package directly from a directory, always reading from disk.

    Unlike a standard import, this function does not check ``sys.modules``
    first — it always loads from the ``__init__.py`` on disk. The loaded
    module is registered in ``sys.modules`` under ``name`` after successful
    execution. Prefer ``import_package_with_dir_fallback`` when a standard
    import should be attempted first.

    Args:
        path: Directory containing the package (must have ``__init__.py``).
        name: Dotted module name for the package (e.g., ``"myproject.utils"``).

    Returns:
        Imported package module.

    Raises:
        FileNotFoundError: If the package directory or its ``__init__.py``
            does not exist.
        ImportError: If the module spec cannot be created from the path.
    """
    init_path = path / "__init__.py"

    loader = SourceFileLoader(fullname=name, path=init_path.as_posix())
    spec = spec_from_loader(name=name, loader=loader, is_package=True)
    if spec is None:
        msg = f"Could not create spec for {init_path}"
        raise ImportError(msg)
    module = module_from_spec(spec)
    loader.exec_module(module)
    sys.modules[name] = module
    return module


def all_modules_from_package(package: ModuleType) -> Generator[ModuleType, None, None]:
    """Recursively discover all modules (non-packages) in a package.

    Walks the entire package hierarchy via ``walk_package`` and yields only
    the leaf modules, excluding intermediate sub-packages.

    Args:
        package: Root package to discover modules from.

    Yields:
        Every module found anywhere within the package hierarchy, excluding
        sub-packages themselves.
    """
    return (module for module, is_pkg in walk_package(package) if not is_pkg)


def discover_all_subclasses_across_package[T: type](
    cls: T,
    package: ModuleType,
) -> set[T]:
    """Discover all subclasses of ``cls`` defined within a package.

    Addresses the limitation of ``__subclasses__()``, which only sees classes
    already imported into the interpreter. This function first walks
    ``package`` (importing every module within it) to trigger class
    registration, then collects all subclasses of ``cls`` and filters them
    to only those defined inside ``package``.

    Args:
        cls: Base class whose subclasses should be discovered.
        package: Package to walk before discovery. All modules within it are
            imported so their classes register as subclasses of ``cls``.
            Only subclasses whose ``__module__`` starts with
            ``package.__name__`` are returned.

    Returns:
        Set of all subclass types of ``cls`` that are defined within
        ``package``. Does not include ``cls`` itself.

    Example:
        >>> from pyrig.rig.configs.base.base import ConfigFile
        >>> from pyrig.rig import configs
        >>> discovered = discover_all_subclasses_across_package(
        ...     ConfigFile,
        ...     package=configs,
        ... )
    """
    # exhaust the generator to trigger imports, but ignore the output
    _ = tuple(walk_package(package))
    subclasses = discover_all_subclasses(cls)
    # remove all not in the package
    return {
        subclass
        for subclass in subclasses
        if subclass.__module__.startswith(package.__name__)
    }


def walk_package(
    package: ModuleType,
    exclude: Iterable[str] = (),
) -> Generator[tuple[ModuleType, bool], None, None]:
    """Recursively walk and import all modules in a package hierarchy.

    Performs a depth-first traversal of ``package`` and its sub-packages.
    Each visited module is imported as a side effect, ensuring that subclass
    registrations (via ``__subclasses__()``) are complete before any
    discovery queries run. The root ``package`` itself is not yielded.

    Args:
        package: Root package to start traversal from.
        exclude: Regex patterns matched against fully qualified names of the
            direct children of ``package``. Any child whose name matches a
            pattern is skipped entirely, along with all of its descendants,
            because excluded sub-packages are never recursed into. Patterns
            are not propagated to deeper levels of the hierarchy.

    Yields:
        ``(module, is_package)`` tuples for each visited module, where
        ``is_package`` is ``True`` when the module is itself a sub-package.
    """
    for module, is_package in iter_modules(package, exclude=exclude):
        if is_package:
            yield module, True
            yield from walk_package(module)
        else:
            yield module, False

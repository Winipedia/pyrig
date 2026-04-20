"""Package discovery, traversal, and cross-dependency subclass discovery.

Provides utilities for package creation, name conversion, recursive traversal,
and cross-dependency discovery. Uses ``DependencyGraph`` from
``pyrig.src.dependency_graph`` to find all packages that depend on a given
dependency, enabling automatic discovery of ``ConfigFile`` implementations and
``BuilderConfigFile`` subclasses across the ecosystem.
"""

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


def make_init_file(path: Path, content: str) -> None:
    """Create an ``__init__.py`` file in the specified directory.

    Creates the file with default content from ``default_init_file_content``.
    Logs the creation at INFO level.

    Args:
        path: Directory path where ``__init__.py`` should be created.
        content: Content to write into the ``__init__.py`` file.

    Note:
        No-op if ``__init__.py`` already exists in the directory.
    """
    path = path / "__init__.py"

    if path.exists():
        return

    typer.echo(f"Creating: {path}")

    write_text_utf8(path, content)


def make_package_dir(path: Path, until: tuple[Path, ...], content: str) -> None:
    """Create a directory and add ``__init__.py`` files up the directory tree.

    Creates the target directory (and missing parents), then adds ``__init__.py``
    files to the target and all parent directories up to (but not including) the
    current working directory. This ensures the entire path is importable as a
    Python package hierarchy.

    Args:
        path: Directory path to create. must be relative to the cwd.
        until: Directory path to stop at when adding ``__init__.py`` files. The
            directory specified by ``until`` will not get an __init__.py
        content: Content to write into each ``__init__.py`` file.


    Note:
        Skips directories that already contain an ``__init__.py`` file.
        Does not create ``__init__.py`` in the CWD itself.
    """
    path.mkdir(parents=True, exist_ok=True)
    until = (*until, Path(), Path.cwd())
    for p in (path, *path.parents):
        if p in until:
            break
        make_init_file(p, content=content)


@cache
def src_package_is_package(package: ModuleType) -> bool:
    """Check if the given module is the src package of the current project.

    Args:
        package: The module to check.

    Returns:
        True if the module's name matches the top-level package of the current project.
    """
    return Path.cwd().name == snake_to_kebab_case(package.__name__)


def src_package_is_pyrig() -> bool:
    """Check if the current project is pyrig itself.

    Determines whether the current working directory is the pyrig project by
    checking if "pyrig" is among the top-level packages.

    Returns:
        True if "pyrig" is a top-level package in the current directory.

    Examples:
        Conditional logic for pyrig development:

            >>> if src_package_is_pyrig():
            ...     print("Running in pyrig development mode")

    Note:
        Detects the pyrig repository, not pyrig as an installed dependency.
    """
    return src_package_is_package(pyrig)


def import_package_from_dir(path: Path, name: str) -> ModuleType:
    """Import a package directly from a directory path.

    Low-level import that bypasses `sys.modules` caching. Creates a module spec
    from the directory's ``__init__.py`` and executes it. Use
    ``import_package_with_dir_fallback`` for normal imports with fallback behavior.

    Args:
        path: Directory containing the package (must have ``__init__.py``).
        name: The dotted module name for the package.


    Returns:
        Imported package module.

    Raises:
        FileNotFoundError: If package directory or ``__init__.py`` doesn't exist.
        ImportError: If module spec cannot be created from the path.
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


def import_package_with_dir_fallback(path: Path, name: str) -> ModuleType:
    """Import a package, falling back to direct directory import if needed.

    Primary package import function with two-stage strategy:
        1. Attempts standard import via
            ``import_module_with_default`` (uses ``sys.modules``)
        2. Falls back to direct file import via ``import_package_from_dir``

    The fallback handles packages not yet in ``sys.modules``, such as dynamically
    created packages or packages in non-standard locations.

    Args:
        path: Absolute or relative path to the package directory.
            Will be resolved to absolute before deriving module name.
        name: The dotted module name for the package.

    Returns:
        Imported package module.

    Raises:
        FileNotFoundError: If fallback fails and package doesn't exist.
    """
    path = path.resolve()
    package = import_module_with_default(name)
    if isinstance(package, ModuleType):
        return package
    return import_package_from_dir(path, name)


def all_modules_from_package(package: ModuleType) -> Generator[ModuleType, None, None]:
    """Recursively discover all modules in a package.

    Uses ``walk_package`` to traverse the package hierarchy and yields only
    modules (not subpackages).

    Args:
        package: The root package module to discover modules from.

    Yields:
        All modules found within the package and its subpackages.
    """
    return (module for module, is_pkg in walk_package(package) if not is_pkg)


def walk_package(
    package: ModuleType,
    exclude: Iterable[str] = (),
) -> Generator[tuple[ModuleType, bool], None, None]:
    """Recursively walk and import all modules in a package hierarchy.

    Performs depth-first traversal, yielding each package with its direct
    module children. Essential for pyrig's discovery system - ensures all
    modules are imported so that subclass registration (via ``__subclasses__()``)
    is complete before discovery queries.

    It does not include the given root package itself in the output,
    only its children and their descendants.

    Args:
        package: Root package module to start traversal from.
        exclude: Optional iterable of regex patterns to exclude from results.
        Patterns are matched against fully qualified module names
        (e.g., "pyrig.rig.configs.base").

    Yields:
        Tuples of (package, modules) where modules is the list of direct
        module children (not subpackages) in that package.
    """
    for module, is_package in iter_modules(package, exclude=exclude):
        if is_package:
            yield module, True
            yield from walk_package(module)
        else:
            yield module, False


def discover_all_subclasses_across_package[T: type](
    cls: T,
    package: ModuleType,
) -> set[T]:
    """Recursively discover all subclasses of a class.

    Python's ``__subclasses__()`` method only returns classes that have been
    imported into the interpreter. This function addresses that limitation by
    optionally walking (importing) a package before discovery, ensuring all
    subclasses defined in that package are visible.

    The discovery process:
        1. If ``package`` is provided, recursively imports all
           modules in that package (triggering class registration)
        2. Recursively collects all subclasses via ``__subclasses__()``
        3. If ``package`` was provided, filters results to only
           include classes whose ``__module__`` contains the package name
        4. Optionally removes parent classes (keeping only leaves)
        5. Optionally removes abstract classes

    Args:
        cls: Base class to find subclasses of. The base class itself is
            included in the results.
        package: Package to walk (import) before discovery.
            When provided, all modules in this package are imported to ensure
            subclasses are registered with Python. Results are then filtered
            to only include classes from this package.

    Returns:
        Set of discovered subclass types (including ``cls`` itself unless
        filtered out by other options).

    Example:
        >>> # Discover all ConfigFile subclasses in pyrig.rig.configs
        >>> from pyrig.rig.configs.base.base import ConfigFile
        >>> from pyrig.rig import configs
        >>> discovered = discover_all_subclasses_across_package(
        ...     ConfigFile,
        ...     package=configs,
        ... )

    Note:
        The recursive ``__subclasses__()`` traversal finds the complete
        inheritance tree, not just direct children. This is essential for
        discovering deeply nested subclasses.

    See Also:
        `discard_parent_classes`: Logic for filtering to leaf classes only.
        `pyrig.src.modules.imports.walk_package`: Package traversal that
            triggers imports.
    """
    # exhaust the generator to trigger imports, but ignore the output
    _ = tuple(walk_package(package))
    subclasses = discover_all_subclasses(cls)
    # remove all not in the package
    return {
        subclass for subclass in subclasses if package.__name__ in subclass.__module__
    }

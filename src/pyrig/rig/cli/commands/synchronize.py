"""Reconciliation of a project's managed files with their canonical state."""

from collections.abc import Iterable
from importlib import import_module
from pathlib import Path

import typer

from pyrig.core.introspection.paths import path_as_module_name
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.packages.manager import PackageManager


def synchronize_project(files: Iterable[Path] | None) -> None:
    """Bring the project into its canonical state.

    Run the ordered reconciliation steps that update managed configuration and
    refresh generated tests. Each step is idempotent, so the whole operation
    is safe to re-run.

    Args:
        files: Specific files to synchronize, relative to the project root.
            If None, all files are synchronized.

    Raises:
        typer.Exit: With code 1 if any file was created or updated during
            the run.
    """
    changed_configs = validate_config_files(files)
    changed_tests = validate_test_files(files)
    if changed_configs or changed_tests:
        raise typer.Exit(code=1)


def validate_config_files(files: Iterable[Path] | None) -> tuple[type[ConfigFile], ...]:
    """Validate pyrig-managed configuration files for the project.

    Args:
        files: Specific config files to validate, relative to the project root.
            If None, all config files are validated.

    Returns:
        A tuple of ConfigFile subclasses that were changed.
    """
    subclasses = ConfigFile.concrete_leaves()
    if files is not None:
        files = set(files)
        subclasses = (cls for cls in subclasses if cls().path() in files)
    return ConfigFile.validate_subclasses(subclasses)


def validate_test_files(
    files: Iterable[Path] | None,
) -> tuple[type[MirrorTestConfigFile], ...]:
    """Validate mirror test files for the project.

    Args:
        files: Source files whose mirrored test file should be validated,
            relative to the project root. Files outside the package's source
            tree, non-Python files, and `__init__.py` files are silently
            ignored. If None, every source file in the package is considered.

    Returns:
        A tuple of MirrorTestConfigFile subclasses that were changed.
    """
    package_root = PackageManager.I.package_root()
    if files is None:
        files = package_root.rglob("*.py")
    else:
        files = (
            file
            for file in files
            if file.suffix == ".py" and file.is_relative_to(package_root)
        )

    files = (file for file in files if file.name != "__init__.py")

    source_root = PackageManager.I.source_root()
    module_names = (
        path_as_module_name(file.relative_to(source_root)) for file in files
    )
    modules = (import_module(name) for name in module_names)
    subclasses = (
        MirrorTestConfigFile.L.generate_subclass(module) for module in modules
    )
    return MirrorTestConfigFile.L.validate_subclasses(subclasses)

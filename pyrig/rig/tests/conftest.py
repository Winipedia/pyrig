"""Pytest configuration and automatic fixture discovery for pyrig tests.

Discovers and registers pytest fixtures from all packages depending on pyrig,
making them available in all test modules without explicit imports.

Discovery Process:
    1. Finds equivalent ``fixtures`` modules in all packages depending on pyrig
       using ``discover_equivalent_modules_across_dependents``
    2. Collects all ``.py`` files within each discovered fixtures package
    3. Registers them as pytest plugins via the ``pytest_plugins`` list

Attributes:
    fixtures_packages (tuple[ModuleType, ...]): Discovered fixtures modules from pyrig
        and all dependent packages.
    pytest_plugin_paths (list[Path]): Relative paths to all fixture Python
        files to be registered as pytest plugins.
    pytest_plugins (tuple[str, ...]): Dotted module names of all fixture files,
        registered as pytest plugins for automatic fixture availability.

See Also:
    pyrig.rig.tests.fixtures: Base fixtures package that is mirrored.
    pyrig.src.modules.package.discover_equivalent_modules_across_dependents:
        Core discovery function for multi-package architecture.
"""

from pathlib import Path

import pyrig
from pyrig.rig.tests import fixtures
from pyrig.src.modules.package import discover_equivalent_modules_across_dependents
from pyrig.src.modules.path import ModulePath

pytest_plugins = tuple(
    ModulePath.relative_path_to_module_name(path.relative_to(package_root))
    for package in discover_equivalent_modules_across_dependents(fixtures, pyrig)
    if (absolute_path := ModulePath.package_type_to_dir_path(package))
    if (relative_path := ModulePath.package_name_to_relative_dir_path(package.__name__))
    if (
        package_root := Path(
            absolute_path.as_posix().removesuffix(relative_path.as_posix())
        )
    )
    for path in absolute_path.rglob("*.py")
)

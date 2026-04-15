"""Pytest configuration and automatic fixture discovery for pyrig tests.

Discovers and registers pytest fixtures from all packages depending on pyrig,
making them available in all test modules without explicit imports.

Discovery Process:
    1. Finds equivalent ``fixtures`` modules in all packages depending on pyrig
       using ``discover_equivalent_modules_across_dependents``
    2. Collects all ``.py`` files within each discovered fixtures package
    3. Registers them as pytest plugins via the ``pytest_plugins`` list

Attributes:
    fixtures_packages (list[ModuleType]): Discovered fixtures modules from pyrig
        and all dependent packages.
    pytest_plugin_paths (list[Path]): Relative paths to all fixture Python
        files to be registered as pytest plugins.
    pytest_plugins (list[str]): Dotted module names of all fixture files,
        registered as pytest plugins for automatic fixture availability.

See Also:
    pyrig.rig.tests.fixtures: Base fixtures package that is mirrored.
    pyrig.src.modules.package.discover_equivalent_modules_across_dependents:
        Core discovery function for multi-package architecture.
"""

import pyrig
from pyrig.core.introspection.packages import (
    discover_equivalent_modules_across_dependents,
)
from pyrig.core.introspection.paths import package_dir_path
from pyrig.rig.tests import fixtures

module_names: list[str] = []
for package in discover_equivalent_modules_across_dependents(fixtures, pyrig):
    package_name = package.__name__
    package_path = package_dir_path(package)

    for path in package_path.rglob("*.py"):
        if path.name == "__init__.py":
            continue

        module_name = (
            package_name
            + "."
            + path.relative_to(package_path)
            .with_suffix("")
            .as_posix()
            .replace("/", ".")
        )

        module_names.append(module_name)

pytest_plugins = tuple(module_names)

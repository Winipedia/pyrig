"""Pytest configuration for automatic fixture discovery across the pyrig ecosystem.

Registers fixture modules from pyrig and all installed packages that depend on
it as pytest plugins. This makes all discovered fixtures available in every
test module without explicit imports.

The registration walks the ``rig.tests.fixtures`` package path across each
dependent in the pyrig ecosystem, collects all ``.py`` files (excluding
``__init__.py``), converts them to dotted module names, and assigns the result
to ``pytest_plugins`` for pytest to load automatically.

Attributes:
    pytest_plugins (tuple[str]): Dotted module names of all discovered fixture
        files, registered as pytest plugins for automatic fixture availability.
"""

import pyrig
from pyrig.core.introspection.dependencies import (
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

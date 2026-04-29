"""Pytest configuration for automatic fixture discovery across the pyrig ecosystem.

Registers fixture modules from pyrig and all installed packages that depend on
it as pytest plugins. This makes all discovered fixtures available in every
test module without explicit imports.

The registration walks the ``rig.tests.fixtures`` package path in each
dependent package, collecting all Python modules and registers them as plugins.
"""

from pathlib import Path

import pyrig
from pyrig.core.introspection.dependencies import (
    discover_equivalent_modules_across_dependents,
)
from pyrig.core.introspection.paths import package_dir_path, path_as_module_name
from pyrig.rig.tests import fixtures

module_names: list[str] = []
for package in discover_equivalent_modules_across_dependents(fixtures, pyrig):
    package_name = package.__name__
    package_path = package_dir_path(package)

    for path in package_path.rglob("*.py"):
        if path.name == "__init__.py":
            continue

        module_name_as_path = Path(package_name) / path.relative_to(package_path)

        module_name = path_as_module_name(module_name_as_path)

        module_names.append(module_name)

pytest_plugins = tuple(module_names)

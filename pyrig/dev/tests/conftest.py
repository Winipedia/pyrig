"""Pytest configuration and automatic fixture discovery for pyrig tests.

Discovers and registers pytest fixtures from all packages depending on pyrig,
making them available in all test modules without explicit imports.

Discovery Process:
    1. Finds all ``fixtures`` modules in packages depending on pyrig
    2. Collects all ``.py`` files within each fixtures module
    3. Registers them as pytest plugins via the ``pytest_plugins`` list

Module Attributes:
    fixtures_pkgs: List of all fixtures modules found across dependent packages.
    pytest_plugin_paths: Relative paths to all fixture Python files.
    pytest_plugins: Module names registered as pytest plugins.
"""

from pathlib import Path

import pyrig
from pyrig.dev.tests import fixtures
from pyrig.src.modules.package import discover_equivalent_modules_across_dependents
from pyrig.src.modules.path import ModulePath

# find the fixtures module in all packages that depend on pyrig
# and add all paths to pytest_plugins
fixtures_pkgs = discover_equivalent_modules_across_dependents(fixtures, pyrig)


pytest_plugin_paths: list[Path] = []
for pkg in fixtures_pkgs:
    absolute_path = ModulePath.pkg_type_to_dir_path(pkg)
    relative_path = ModulePath.pkg_name_to_relative_dir_path(pkg.__name__)

    pkg_root = Path(absolute_path.as_posix().removesuffix(relative_path.as_posix()))

    for path in absolute_path.rglob("*.py"):
        rel_plugin_path = path.relative_to(pkg_root)
        pytest_plugin_paths.append(rel_plugin_path)

pytest_plugins = [
    ModulePath.relative_path_to_module_name(path) for path in pytest_plugin_paths
]

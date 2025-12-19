"""Pytest configuration for pyrig tests.

This module automatically discovers and registers pytest plugins from all
packages that depend on pyrig. It finds fixtures modules across the dependency
graph and adds them to pytest_plugins for automatic fixture availability.

The discovery process:
    1. Finds all packages depending on pyrig
    2. Locates their fixtures modules
    3. Collects all Python files within those modules
    4. Registers them as pytest plugins
"""

from pathlib import Path

import pyrig
from pyrig.dev.tests import fixtures
from pyrig.src.modules.package import get_same_modules_from_deps_depen_on_dep
from pyrig.src.modules.path import ModulePath

# find the fixtures module in all packages that depend on pyrig
# and add all paths to pytest_plugins
fixtures_pkgs = get_same_modules_from_deps_depen_on_dep(fixtures, pyrig)


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

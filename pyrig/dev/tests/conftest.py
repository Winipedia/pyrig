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
from pyrig.src.modules.module import (
    get_same_modules_from_deps_depen_on_dep,
    to_module_name,
    to_path,
)

# find the fixtures module in all packages that depend on pyrig
# and add all paths to pytest_plugins
fixtures_pkgs = get_same_modules_from_deps_depen_on_dep(fixtures, pyrig)


pytest_plugin_paths: list[Path] = []
for pkg in fixtures_pkgs:
    absolute_path = Path(pkg.__path__[0])
    relative_path = to_path(pkg.__name__, is_package=True)

    pkg_root = Path(absolute_path.as_posix().removesuffix(relative_path.as_posix()))

    for path in absolute_path.rglob("*.py"):
        rel_plugin_path = path.relative_to(pkg_root)
        pytest_plugin_paths.append(rel_plugin_path)

pytest_plugins = [to_module_name(path) for path in pytest_plugin_paths]

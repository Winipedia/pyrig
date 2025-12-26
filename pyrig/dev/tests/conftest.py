"""Pytest configuration and automatic fixture discovery for pyrig tests.

This module serves as the pytest configuration file (conftest.py) for pyrig-based
projects. It implements automatic discovery and registration of pytest fixtures
from all packages in the dependency chain that depend on pyrig.

The module leverages pyrig's multi-package architecture to enable fixture sharing
across the entire dependency graph. When pytest runs, this configuration
automatically finds and registers all fixtures from all dependent packages,
making them available to all test modules without explicit imports.

Discovery and Registration Process:
    1. **Find dependent packages**: Uses `get_same_modules_from_deps_depen_on_dep()`
       to find all packages depending on pyrig

    2. **Locate fixtures modules**: For each dependent package, finds the
       corresponding `fixtures` module (e.g., `myapp.dev.tests.fixtures`)

    3. **Collect Python files**: Recursively collects all `.py` files within
       each fixtures module using `Path.rglob("*.py")`

    4. **Build plugin paths**: Converts absolute file paths to relative paths
       from the package root

    5. **Register as plugins**: Converts relative paths to module names and
       adds them to `pytest_plugins` list for automatic registration

How It Works:
    - **Input**: `pyrig.dev.tests.fixtures` module as the reference
    - **Discovery**: Finds all `fixtures` modules in packages depending on pyrig
    - **Output**: `pytest_plugins` list containing module names like:
      - `"pyrig.dev.tests.fixtures.assertions"`
      - `"pyrig.dev.tests.fixtures.factories"`
      - `"pyrig.dev.tests.fixtures.autouse.session"`
      - `"myapp.dev.tests.fixtures.custom_fixtures"`
      - etc.

Benefits:
    - **No explicit imports**: Fixtures are available in all test modules
      automatically without `import` statements
    - **Multi-package support**: Fixtures from all dependent packages are
      available everywhere
    - **Automatic discovery**: New fixtures are automatically registered when
      added to `fixtures` modules
    - **Centralized configuration**: Single point of configuration for all
      pytest plugins across the dependency chain

Example:
    Given this project structure::

        myapp/
        ├── dev/
        │   └── tests/
        │       ├── conftest.py  # This file (from pyrig)
        │       └── fixtures/
        │           ├── assertions.py
        │           └── custom_fixtures.py
        └── pyproject.toml  # depends on pyrig

    When pytest runs, this conftest.py will:
    1. Find `pyrig.dev.tests.fixtures` and `myapp.dev.tests.fixtures`
    2. Register all `.py` files in both as pytest plugins
    3. Make all fixtures available to all test modules

Module Attributes:
    fixtures_pkgs (list[ModuleType]): List of all fixtures modules found across
        packages depending on pyrig. Each element is a module object representing
        a `fixtures` package.

    pytest_plugin_paths (list[Path]): List of relative paths to all Python files
        in all fixtures modules. Paths are relative to their respective package
        roots.

    pytest_plugins (list[str]): List of module names to register as pytest
        plugins. This is the standard pytest mechanism for plugin registration.
        Pytest automatically imports and registers all modules in this list.

See Also:
    pyrig.src.modules.package.get_same_modules_from_deps_depen_on_dep:
        Discovery mechanism for finding fixtures modules
    pyrig.src.modules.path.ModulePath: Utilities for path/module name conversion
    pyrig.dev.tests.fixtures: Base fixtures module that serves as discovery anchor
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

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

pytest_plugins = ["pyrig.rig.tests.conftest"]

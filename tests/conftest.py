"""Pytest configuration for automatic fixture discovery across the pyrig ecosystem.

Registers fixture modules from pyrig and all installed packages that depend on
it as pytest plugins. This makes all discovered fixtures available in every
test module without explicit imports.

The registration walks the ``<project_name>.rig.tests.fixtures`` package path in
pyrig and all pyrig dependent packages, collecting all Python modules except
``__init__.py`` modules and registers them as plugins.
"""

pytest_plugins = ["pyrig.rig.tests.conftest"]

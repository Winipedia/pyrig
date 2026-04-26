"""Pytest fixture package for pyrig and pyrig-based projects.

All Python modules inside this package (excluding ``__init__.py``) are
automatically discovered by the project conftest and registered as pytest
plugins. This makes every fixture defined in those submodules available in
all test modules without explicit imports.

Installed packages that depend on pyrig and mirror this package path are
discovered and registered in the same way, allowing downstream projects to
extend the base fixture set transparently.
"""

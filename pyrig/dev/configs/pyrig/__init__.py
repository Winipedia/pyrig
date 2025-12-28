"""Pyrig-specific configuration file overrides.

Provides ConfigFile subclasses that are only active when pyrig itself is the
project being configured. Uses conditional class definition based on
``src_pkg_is_pyrig()`` to prevent pyrig-specific configs from leaking into
dependent projects.

Architecture
------------

This package contains configuration overrides that only apply to pyrig itself:

- **PyprojectConfigFile**: Adds pyrig-specific PyPI classifiers and keywords
  (development status, intended audience, topics, project-setup keywords)

The conditional class definition pattern ensures that ``__subclasses__()`` only
returns these classes when running within the pyrig project itself, so other
projects using pyrig as a dependency get their own appropriate defaults.

Example:
    When running ``uv run pyrig mkroot`` in pyrig's repository::

        >>> from pyrig.dev.configs.pyrig.pyproject import PyprojectConfigFile
        >>> # PyprojectConfigFile exists and adds pyrig-specific classifiers

    When running ``uv run myproject mkroot`` in another project::

        >>> from pyrig.dev.configs.pyrig.pyproject import PyprojectConfigFile
        >>> # ImportError or class doesn't exist (conditional definition)

See Also:
    pyrig.dev.configs.pyproject.PyprojectConfigFile: Base pyproject.toml config
    pyrig.dev.utils.packages.src_pkg_is_pyrig: Package detection utility
"""

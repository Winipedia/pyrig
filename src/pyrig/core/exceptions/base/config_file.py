"""Base exception for config file errors."""

from pyrig.core.exceptions.base.dependency_subclass import DependencySubclassError


class ConfigFileError(DependencySubclassError):
    """Base exception for config file errors."""

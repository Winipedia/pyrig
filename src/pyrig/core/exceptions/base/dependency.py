"""Module containing the base exception for dependency-related errors in Pyrig."""

from pyrig.core.exceptions.base.error import PyrigError


class DependencyError(PyrigError):
    """Raised when exceptions related to dependencies occur."""

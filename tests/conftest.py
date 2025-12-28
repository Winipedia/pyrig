"""Pytest configuration for tests.

This defines the pyrig pytest plugin that provides access to pyrig's test
infrastructure, including fixtures, hooks, and test utilities.
"""

pytest_plugins = ["pyrig.dev.tests.conftest"]

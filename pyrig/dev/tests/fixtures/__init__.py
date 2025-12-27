"""Reusable pytest fixtures for pyrig-based projects.

Fixtures defined in this package are automatically discovered and registered
via pytest's plugin mechanism. They are available in all test modules without
explicit imports.

Modules:
    assertions: Fixtures for test coverage verification.
    factories: Factory fixtures for ConfigFile and Builder testing.
    autouse: Scope-specific autouse fixtures for automatic validation.
"""

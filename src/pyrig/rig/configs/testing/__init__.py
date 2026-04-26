"""Configuration file management for test infrastructure.

This package contains ``ConfigFile`` subclasses that generate and maintain
pytest scaffolding files for pyrig-based projects. These files establish a
working test environment immediately, even before any application tests
have been written.

To add a new managed test file, define a concrete ``ConfigFile`` subclass
inside this package.
"""

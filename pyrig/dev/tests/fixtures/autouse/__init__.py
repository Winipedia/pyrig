"""Scope-specific autouse pytest fixtures for automatic test validation.

Contains autouse fixtures organized by pytest scope that run automatically
to enforce test coverage and project standards.

Modules:
    session: Session-scoped fixtures for project-wide validation (structure,
        dependencies, git state, development environment).
    module: Module-scoped fixtures for test coverage per test module.
    class_: Class-scoped fixtures for test coverage per test class.
"""

"""Pytest fixtures for pyrig-based projects.

This package contains reusable pytest fixtures that are automatically discovered
and registered via the pytest_plugins mechanism in conftest.py. All fixtures
defined in this package and its submodules are available in all test modules
without explicit imports.

The fixtures are organized by purpose and scope:

Modules:
    assertions: Fixtures that assert test coverage and code completeness,
        including `assert_no_untested_objs` which verifies all code has tests.

    factories: Factory fixtures for creating test instances of ConfigFile and
        Builder classes using temporary directories. Includes `config_file_factory`
        and `builder_factory`.

    autouse/: Scope-specific autouse fixtures that run automatically:
        - session: Session-scoped fixtures (run once per test session)
        - module: Module-scoped fixtures (run once per test module)
        - class_: Class-scoped fixtures (run once per test class)

Automatic Registration:
    All Python files in this package are automatically registered as pytest
    plugins via conftest.py. This means:

    - Fixtures are available in all test modules without imports
    - New fixtures are automatically discovered when added
    - Multi-package projects share fixtures across the dependency chain

See Also:
    pyrig.dev.tests.conftest: Pytest configuration and plugin discovery
    pyrig.dev.tests.fixtures.assertions: Test coverage assertion fixtures
    pyrig.dev.tests.fixtures.factories: Factory fixtures for testing
    pyrig.dev.tests.fixtures.autouse: Scope-specific autouse fixtures
"""

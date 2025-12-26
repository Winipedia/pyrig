"""Test infrastructure and pytest fixtures for pyrig-based projects.

This package provides a comprehensive testing framework for pyrig projects,
including pytest configuration, fixtures, assertions, and automatic test
discovery across the dependency chain.

Architecture Overview:
    The testing infrastructure is organized into several components:

    1. **conftest.py**: Pytest configuration that automatically discovers and
       registers pytest plugins (fixtures) from all packages depending on pyrig.
       This enables multi-package fixture sharing across the dependency graph.

    2. **fixtures/**: Package containing reusable pytest fixtures organized by
       purpose and scope:
       - **assertions.py**: Fixtures that assert code coverage and test completeness
       - **factories.py**: Factory fixtures for creating test instances of
         ConfigFile and Builder classes with temporary directories
       - **autouse/**: Scope-specific autouse fixtures that run automatically:
         - **session.py**: Session-scoped fixtures (run once per test session)
         - **module.py**: Module-scoped fixtures (run once per test module)
         - **class_.py**: Class-scoped fixtures (run once per test class)

Key Features:
    - **Automatic fixture discovery**: Finds and registers fixtures from all
      packages depending on pyrig via `pytest_plugins` mechanism
    - **Multi-package testing**: Enables fixture sharing across dependency chain
    - **Test coverage enforcement**: Autouse fixtures ensure all code has tests
    - **Project structure validation**: Session fixtures verify project structure,
      naming conventions, and configuration correctness
    - **Dependency isolation**: Fixtures verify that src code doesn't depend on
      dev dependencies
    - **Factory fixtures**: Provide test instances of ConfigFile and Builder
      classes using temporary directories

Automatic Fixture Registration:
    All fixtures defined in this package and in `fixtures` modules of packages
    depending on pyrig are automatically registered via the `pytest_plugins`
    mechanism in `conftest.py`. This means:

    - Fixtures are available in all test modules without explicit imports
    - New fixtures are automatically discovered when added to `fixtures` modules
    - Multi-package projects share fixtures across the dependency chain

Example:
    Using the test infrastructure in a test module::

        # No imports needed - fixtures are auto-registered
        def test_my_config(config_file_factory):
            '''Test using the config_file_factory fixture.'''
            TestConfig = config_file_factory(MyConfigFile)
            assert TestConfig.get_path().exists()

        def test_my_function(assert_no_untested_objs):
            '''Test using the assert_no_untested_objs fixture.'''
            assert_no_untested_objs(my_module)

Session-Level Validations:
    The following validations run automatically once per test session:

    - No unstaged git changes (in CI only)
    - Project root structure is correct
    - No namespace packages (all packages have `__init__.py`)
    - All source code in single package
    - Source package correctly named
    - All modules have corresponding test modules
    - No unittest package usage (pytest only)
    - Dependencies are up to date
    - Pre-commit hooks installed
    - Source code runs without dev dependencies
    - Source code doesn't import dev code
    - All dev dependencies declared in pyproject.toml
    - Project management tool (uv) is up to date
    - Version control (git) is installed
    - Container engine (podman) is installed (local only)

Module-Level Validations:
    - All functions and classes in module have corresponding tests

Class-Level Validations:
    - All methods in class have corresponding test methods

See Also:
    pyrig.dev.tests.conftest: Pytest configuration and plugin discovery
    pyrig.dev.tests.fixtures.assertions: Test coverage assertion fixtures
    pyrig.dev.tests.fixtures.factories: Factory fixtures for testing
    pyrig.dev.tests.fixtures.autouse: Scope-specific autouse fixtures
"""

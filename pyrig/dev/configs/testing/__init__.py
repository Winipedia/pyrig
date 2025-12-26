"""Test configuration file management.

This subpackage provides configuration file managers for pytest test
infrastructure and test skeleton files.

The subpackage includes:
    - **ConftestConfigFile**: Manages tests/conftest.py for pytest configuration
      and plugin setup
    - **FixturesInitConfigFile**: Manages tests/fixtures/__init__.py for custom
      test fixtures
    - **MainTestConfigFile**: Manages test_main.py for CLI entry point tests
    - **ZeroTestConfigFile**: Manages test_zero.py for basic sanity tests

Key Features:
    - Automatic pytest configuration setup
    - Integration with pyrig's test fixtures and plugins
    - Test skeleton generation for new projects
    - Proper test directory structure
    - CLI testing infrastructure

Modules:
    conftest: tests/conftest.py pytest configuration
    fixtures_init: tests/fixtures/__init__.py custom fixtures
    main_test: test_main.py CLI entry point tests
    zero_test: test_zero.py basic sanity tests

See Also:
    pyrig.dev.tests.conftest
        pyrig's conftest module with fixtures and plugins
    pytest documentation: https://docs.pytest.org/
"""

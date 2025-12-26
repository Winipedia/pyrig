"""Pytest fixture decorators and skip markers.

This module provides convenience decorators and markers for pytest testing. It
simplifies common patterns like creating fixtures with specific scopes, autouse
fixtures, and conditional test skipping.

All decorators are partial applications of pytest.fixture with pre-configured
scope and autouse parameters, providing a more concise and readable syntax for
fixture definitions.

Module Attributes:
    skip_fixture_test: Skip marker for tests of fixtures that cannot be called
        directly
    skip_in_github_actions: Skip marker for tests that cannot run in GitHub
        Actions CI environment

Fixture Decorators (by scope):
    function_fixture: Function-scoped fixture (default pytest scope)
    class_fixture: Class-scoped fixture
    module_fixture: Module-scoped fixture
    package_fixture: Package-scoped fixture
    session_fixture: Session-scoped fixture

Autouse Fixture Decorators:
    autouse_function_fixture: Function-scoped autouse fixture
    autouse_class_fixture: Class-scoped autouse fixture
    autouse_module_fixture: Module-scoped autouse fixture
    autouse_package_fixture: Package-scoped autouse fixture
    autouse_session_fixture: Session-scoped autouse fixture

Examples:
    Create a session-scoped fixture::

        >>> from pyrig.dev.utils.testing import session_fixture
        >>>
        >>> @session_fixture
        ... def database_connection():
        ...     conn = create_connection()
        ...     yield conn
        ...     conn.close()

    Create an autouse module fixture::

        >>> from pyrig.dev.utils.testing import autouse_module_fixture
        >>>
        >>> @autouse_module_fixture
        ... def setup_logging():
        ...     configure_logging()
        ...     yield
        ...     cleanup_logging()

    Skip tests in GitHub Actions::

        >>> from pyrig.dev.utils.testing import skip_in_github_actions
        >>>
        >>> @skip_in_github_actions
        ... def test_local_only():
        ...     # This test only runs locally, not in CI
        ...     assert local_resource_exists()

    Skip fixture tests::

        >>> from pyrig.dev.utils.testing import skip_fixture_test
        >>>
        >>> @skip_fixture_test
        ... def test_my_fixture(my_fixture):
        ...     # Fixtures cannot be called directly, so this test is skipped
        ...     pass

Note:
    All fixture decorators are equivalent to using @pytest.fixture with the
    appropriate scope and autouse parameters. They are provided for convenience
    and improved code readability.

See Also:
    pytest.fixture: The underlying pytest fixture decorator
    pytest.mark.skip: The underlying skip marker
    pytest.mark.skipif: The underlying conditional skip marker
"""

import functools

import pytest

from pyrig.src.git import running_in_github_actions

skip_fixture_test: pytest.MarkDecorator = functools.partial(
    pytest.mark.skip,
    reason="Fixtures are not testable bc they cannot be called directly.",
)()
"""Skip marker for fixture tests that cannot be called directly.

Pytest fixtures cannot be called directly as regular functions, so tests that
attempt to test fixture behavior directly should be skipped. This marker provides
a standard reason message for such skips.

Type:
    pytest.MarkDecorator

Examples:
    Skip a test that would call a fixture directly::

        >>> from pyrig.dev.utils.testing import skip_fixture_test
        >>>
        >>> @skip_fixture_test
        ... def test_my_fixture(my_fixture):
        ...     # This test is skipped because fixtures can't be called directly
        ...     pass
"""

skip_in_github_actions: pytest.MarkDecorator = functools.partial(
    pytest.mark.skipif,
    running_in_github_actions(),
    reason="Test cannot run in GitHub action.",
)()
"""Skip marker for tests that cannot run in GitHub Actions CI environment.

Some tests require local resources, interactive input, or specific system
configurations that are not available in GitHub Actions. This marker automatically
skips such tests when running in the CI environment.

Type:
    pytest.MarkDecorator

Examples:
    Skip a test that requires local resources::

        >>> from pyrig.dev.utils.testing import skip_in_github_actions
        >>>
        >>> @skip_in_github_actions
        ... def test_local_database():
        ...     # This test only runs locally, not in CI
        ...     assert local_db.connect()
"""

function_fixture = functools.partial(pytest.fixture, scope="function")
"""Decorator for function-scoped pytest fixtures.

Creates a fixture that is set up and torn down for each test function. This is
the default pytest fixture scope. Use this when the fixture state should not be
shared between tests.

Type:
    functools.partial[pytest.fixture]

Examples:
    Create a function-scoped fixture::

        >>> from pyrig.dev.utils.testing import function_fixture
        >>>
        >>> @function_fixture
        ... def temp_file():
        ...     f = create_temp_file()
        ...     yield f
        ...     f.cleanup()
"""

class_fixture = functools.partial(pytest.fixture, scope="class")
"""Decorator for class-scoped pytest fixtures.

Creates a fixture that is set up once per test class and shared among all test
methods in that class. Use this when the fixture is expensive to create and can
be safely shared within a class.

Type:
    functools.partial[pytest.fixture]

Examples:
    Create a class-scoped fixture::

        >>> from pyrig.dev.utils.testing import class_fixture
        >>>
        >>> @class_fixture
        ... def database_connection():
        ...     conn = create_connection()
        ...     yield conn
        ...     conn.close()
"""

module_fixture = functools.partial(pytest.fixture, scope="module")
"""Decorator for module-scoped pytest fixtures.

Creates a fixture that is set up once per test module and shared among all tests
in that module. Use this when the fixture is expensive to create and can be safely
shared across all tests in a module.

Type:
    functools.partial[pytest.fixture]

Examples:
    Create a module-scoped fixture::

        >>> from pyrig.dev.utils.testing import module_fixture
        >>>
        >>> @module_fixture
        ... def api_client():
        ...     client = APIClient()
        ...     yield client
        ...     client.disconnect()
"""

package_fixture = functools.partial(pytest.fixture, scope="package")
"""Decorator for package-scoped pytest fixtures.

Creates a fixture that is set up once per test package and shared among all tests
in that package. Use this when the fixture is very expensive to create and can be
safely shared across an entire package.

Type:
    functools.partial[pytest.fixture]

Examples:
    Create a package-scoped fixture::

        >>> from pyrig.dev.utils.testing import package_fixture
        >>>
        >>> @package_fixture
        ... def test_database():
        ...     db = setup_test_database()
        ...     yield db
        ...     teardown_test_database(db)
"""

session_fixture = functools.partial(pytest.fixture, scope="session")
"""Decorator for session-scoped pytest fixtures.

Creates a fixture that is set up once per test session and shared among all tests
in the entire test run. Use this when the fixture is extremely expensive to create
and can be safely shared across all tests.

Type:
    functools.partial[pytest.fixture]

Examples:
    Create a session-scoped fixture::

        >>> from pyrig.dev.utils.testing import session_fixture
        >>>
        >>> @session_fixture
        ... def docker_container():
        ...     container = start_docker_container()
        ...     yield container
        ...     stop_docker_container(container)
"""

autouse_function_fixture = functools.partial(
    pytest.fixture, scope="function", autouse=True
)
"""Decorator for autouse function-scoped pytest fixtures.

Creates a fixture that automatically runs for each test function without needing
to be explicitly requested. Use this for setup/teardown that should happen for
every test.

Type:
    functools.partial[pytest.fixture]

Examples:
    Create an autouse function fixture::

        >>> from pyrig.dev.utils.testing import autouse_function_fixture
        >>>
        >>> @autouse_function_fixture
        ... def reset_state():
        ...     clear_global_state()
        ...     yield
        ...     clear_global_state()
"""

autouse_class_fixture = functools.partial(pytest.fixture, scope="class", autouse=True)
"""Decorator for autouse class-scoped pytest fixtures.

Creates a fixture that automatically runs once per test class without needing to
be explicitly requested. Use this for setup/teardown that should happen once per
test class.

Type:
    functools.partial[pytest.fixture]

Examples:
    Create an autouse class fixture::

        >>> from pyrig.dev.utils.testing import autouse_class_fixture
        >>>
        >>> @autouse_class_fixture
        ... def setup_test_class():
        ...     initialize_class_resources()
        ...     yield
        ...     cleanup_class_resources()
"""

autouse_module_fixture = functools.partial(pytest.fixture, scope="module", autouse=True)
"""Decorator for autouse module-scoped pytest fixtures.

Creates a fixture that automatically runs once per test module without needing to
be explicitly requested. Use this for setup/teardown that should happen once per
test module.

Type:
    functools.partial[pytest.fixture]

Examples:
    Create an autouse module fixture::

        >>> from pyrig.dev.utils.testing import autouse_module_fixture
        >>>
        >>> @autouse_module_fixture
        ... def configure_logging():
        ...     setup_logging()
        ...     yield
        ...     teardown_logging()
"""

autouse_package_fixture = functools.partial(
    pytest.fixture, scope="package", autouse=True
)
"""Decorator for autouse package-scoped pytest fixtures.

Creates a fixture that automatically runs once per test package without needing to
be explicitly requested. Use this for setup/teardown that should happen once per
test package.

Type:
    functools.partial[pytest.fixture]

Examples:
    Create an autouse package fixture::

        >>> from pyrig.dev.utils.testing import autouse_package_fixture
        >>>
        >>> @autouse_package_fixture
        ... def setup_package():
        ...     initialize_package_resources()
        ...     yield
        ...     cleanup_package_resources()
"""

autouse_session_fixture = functools.partial(
    pytest.fixture, scope="session", autouse=True
)
"""Decorator for autouse session-scoped pytest fixtures.

Creates a fixture that automatically runs once per test session without needing to
be explicitly requested. Use this for setup/teardown that should happen once for
the entire test run.

Type:
    functools.partial[pytest.fixture]

Examples:
    Create an autouse session fixture::

        >>> from pyrig.dev.utils.testing import autouse_session_fixture
        >>>
        >>> @autouse_session_fixture
        ... def setup_test_environment():
        ...     initialize_test_environment()
        ...     yield
        ...     cleanup_test_environment()
"""

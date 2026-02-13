"""Pytest fixture decorators and skip markers.

Convenience decorators and markers for pytest testing. Simplifies common patterns
like creating fixtures with specific scopes, autouse fixtures, and conditional
test skipping.

All decorators are partial applications of pytest.fixture with pre-configured
scope and autouse parameters.

Module Attributes:
    skip_fixture_test: Skip marker for fixture tests
    skip_in_github_actions: Skip marker for tests that can't run in CI
    skip_if_no_internet: Skip marker for tests that require internet connection

Fixture Decorators (by scope):
    function_fixture, class_fixture, module_fixture, package_fixture,
    session_fixture

Autouse Fixture Decorators:
    autouse_function_fixture, autouse_class_fixture, autouse_module_fixture,
    autouse_package_fixture, autouse_session_fixture

Examples:
    Create a session-scoped fixture::

        >>> from pyrig.rig.utils.testing import session_fixture
        >>> @session_fixture
        ... def database_connection():
        ...     conn = create_connection()
        ...     yield conn
        ...     conn.close()

    Skip tests in GitHub Actions::

        >>> from pyrig.rig.utils.testing import skip_in_github_actions
        >>> @skip_in_github_actions
        ... def test_local_only():
        ...     assert local_resource_exists()

See Also:
    pytest.fixture: Underlying pytest fixture decorator
"""

import functools

import pytest

from pyrig.src.git import running_in_github_actions
from pyrig.src.requests import internet_is_available

skip_fixture_test: pytest.MarkDecorator = functools.partial(
    pytest.mark.skip,
    reason="Fixtures are not testable bc they cannot be called directly.",
)()
"""Skip marker for tests of fixture functions themselves.

Pytest fixtures cannot be invoked as regular functions; they are called by pytest's
dependency injection system. Use this marker to skip placeholder tests that exist
to satisfy test coverage requirements for fixture definitions.

Type:
    pytest.MarkDecorator

Examples:
    Skip a test for a fixture function::

        >>> @skip_fixture_test
        ... def test_my_fixture_function():
        ...     # This test exists for coverage but cannot actually test the fixture
        ...     pass
"""

skip_in_github_actions: pytest.MarkDecorator = functools.partial(
    pytest.mark.skipif,
    running_in_github_actions(),
    reason="Test cannot run in GitHub action.",
)()
"""Skip marker for tests that cannot run in GitHub Actions CI.

Automatically skips tests requiring local resources, interactive input, or
specific system configurations not available in CI.

Type:
    pytest.MarkDecorator

Examples:
    Skip a test requiring local resources::

        >>> @skip_in_github_actions
        ... def test_local_database():
        ...     assert local_db.connect()
"""

skip_if_no_internet: pytest.MarkDecorator = functools.partial(
    pytest.mark.skipif,
    not internet_is_available(),
    reason="Test requires internet connection.",
)()
"""Skip marker for tests that require an internet connection.

Automatically skips tests when no internet connectivity is detected. Uses a quick
socket connection check to Cloudflare DNS (1.1.1.1) to determine availability.

Type:
    pytest.MarkDecorator

Examples:
    Skip a test requiring network access::

        >>> @skip_if_no_internet
        ... def test_api_integration():
        ...     response = api_client.fetch_data()
        ...     assert response.status_code == 200

See Also:
    pyrig.src.requests.internet_is_available: Underlying connectivity check
"""

"""Testing decorators and pytest mark utilities.

This module provides convenience decorators for defining pytest fixtures
with specific scopes and skip conditions. It simplifies common patterns
like creating autouse fixtures or skipping tests in CI environments.

Example:
    Using a scoped fixture decorator::

        @session_fixture
        def database_connection():
            return create_connection()

    Using an autouse fixture::

        @autouse_module_fixture
        def setup_logging():
            configure_logging()
"""

import functools

import pytest

from pyrig.src.git.git import running_in_github_actions

#: Skip marker for fixture tests that cannot be called directly.
skip_fixture_test: pytest.MarkDecorator = functools.partial(
    pytest.mark.skip,
    reason="Fixtures are not testable bc they cannot be called directly.",
)()

#: Skip marker for tests that cannot run in GitHub Actions.
skip_in_github_actions: pytest.MarkDecorator = functools.partial(
    pytest.mark.skipif,
    running_in_github_actions(),
    reason="Test cannot run in GitHub action.",
)()

#: Decorator for function-scoped fixtures.
function_fixture = functools.partial(pytest.fixture, scope="function")
#: Decorator for class-scoped fixtures.
class_fixture = functools.partial(pytest.fixture, scope="class")
#: Decorator for module-scoped fixtures.
module_fixture = functools.partial(pytest.fixture, scope="module")
#: Decorator for package-scoped fixtures.
package_fixture = functools.partial(pytest.fixture, scope="package")
#: Decorator for session-scoped fixtures.
session_fixture = functools.partial(pytest.fixture, scope="session")

#: Decorator for autouse function-scoped fixtures.
autouse_function_fixture = functools.partial(
    pytest.fixture, scope="function", autouse=True
)
#: Decorator for autouse class-scoped fixtures.
autouse_class_fixture = functools.partial(pytest.fixture, scope="class", autouse=True)
#: Decorator for autouse module-scoped fixtures.
autouse_module_fixture = functools.partial(pytest.fixture, scope="module", autouse=True)
#: Decorator for autouse package-scoped fixtures.
autouse_package_fixture = functools.partial(
    pytest.fixture, scope="package", autouse=True
)
#: Decorator for autouse session-scoped fixtures.
autouse_session_fixture = functools.partial(
    pytest.fixture, scope="session", autouse=True
)

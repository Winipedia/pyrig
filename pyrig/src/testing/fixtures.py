"""Testing fixtures for pytest.

This module provides custom fixtures for pytest that can be used to
automate common testing tasks and provide consistent setup and teardown
for tests.
"""

import functools

import pytest

function_fixture = functools.partial(pytest.fixture, scope="function")
class_fixture = functools.partial(pytest.fixture, scope="class")
module_fixture = functools.partial(pytest.fixture, scope="module")
package_fixture = functools.partial(pytest.fixture, scope="package")
session_fixture = functools.partial(pytest.fixture, scope="session")

autouse_function_fixture = functools.partial(
    pytest.fixture, scope="function", autouse=True
)
autouse_class_fixture = functools.partial(pytest.fixture, scope="class", autouse=True)
autouse_module_fixture = functools.partial(pytest.fixture, scope="module", autouse=True)
autouse_package_fixture = functools.partial(
    pytest.fixture, scope="package", autouse=True
)
autouse_session_fixture = functools.partial(
    pytest.fixture, scope="session", autouse=True
)

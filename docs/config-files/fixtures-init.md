# FixturesInitConfigFile

## Overview

**File Location:** `tests/fixtures.py`
**ConfigFile Class:** `FixturesInitConfigFile`
**File Type:** Python
**Priority:** Standard

Creates a fixtures file where you can define custom pytest fixtures for your test suite. This file is automatically discovered by pytest through the conftest.py configuration.

## Purpose

The `tests/fixtures.py` file provides a place for custom fixtures:

- **Custom Fixtures** - Define project-specific test fixtures
- **Automatic Discovery** - Fixtures are automatically available in all tests
- **Organization** - Separates fixtures from test logic
- **Reusability** - Fixtures can be used across multiple test files
- **Documentation** - Docstring explains the file's purpose

### Why pyrig manages this file

pyrig creates `tests/fixtures.py` to:
1. **Immediate extensibility** - You can add fixtures from day one
2. **Best practices** - Follows pytest conventions
3. **Automatic discovery** - Fixtures are automatically registered
4. **Documentation** - Docstring explains how to use the file
5. **Separation of concerns** - Keeps fixtures separate from conftest.py

The file is created during `pyrig init` with only the docstring from pyrig's fixtures module.

## File Location

The file is placed in the tests directory:

```
my-awesome-project/
├── my_awesome_project/
│   └── ...
├── tests/
│   ├── conftest.py
│   ├── fixtures.py  # <-- Here
│   └── test_*.py
└── pyproject.toml
```

This mirrors pyrig's structure:

```
pyrig/
├── pyrig/
│   └── ...
├── tests/
│   ├── conftest.py
│   ├── fixtures.py  # <-- Mirrored from here
│   └── test_*.py
└── pyproject.toml
```

## File Structure

### Docstring Only

The file contains **only the docstring** from pyrig's `dev.tests.fixtures`:

```python
"""__init__ module."""
```

- **Type:** Module docstring
- **Default:** Copied from `pyrig.dev.tests.fixtures.__init__`
- **Required:** Yes (minimal module marker)
- **Purpose:** Documents the module
- **Why pyrig sets it:** Provides context for the module

**Why only the docstring:**
- **Minimal** - Doesn't impose fixtures
- **Flexible** - You can add your own fixtures
- **Documentation** - Preserves pyrig's documentation
- **Module marker** - Valid Python module

## Default Configuration

For a project named `my-awesome-project`:

**File location:** `tests/fixtures.py`

**File contents:**
```python
"""__init__ module."""
```

## What Are Fixtures?

Fixtures are reusable test components that provide data, setup, or teardown for tests. They're a core pytest feature.

### Basic Fixture

```python
import pytest


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value"}


def test_something(sample_data):
    """Test using the fixture."""
    assert sample_data["key"] == "value"
```

### Fixture with Setup/Teardown

```python
import pytest


@pytest.fixture
def database():
    """Provide a test database."""
    # Setup
    db = create_test_database()

    # Provide to test
    yield db

    # Teardown
    db.cleanup()
```

## Creating Custom Fixtures

### Example: Data Fixtures

```python
# tests/fixtures.py
"""__init__ module."""

import pytest


@pytest.fixture
def user_data():
    """Provide sample user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "age": 25,
    }


@pytest.fixture
def post_data():
    """Provide sample post data."""
    return {
        "title": "Test Post",
        "content": "This is a test post.",
        "author": "testuser",
    }
```

### Example: Mock Fixtures

```python
# tests/fixtures.py
"""__init__ module."""

import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_api():
    """Provide a mock API client."""
    api = Mock()
    api.get.return_value = {"status": "success"}
    api.post.return_value = {"id": 123}
    return api


@pytest.fixture
def mock_database():
    """Provide a mock database."""
    db = Mock()
    db.query.return_value = [{"id": 1, "name": "Test"}]
    return db
```

### Example: File Fixtures

```python
# tests/fixtures.py
"""__init__ module."""

import pytest
from pathlib import Path


@pytest.fixture
def temp_file(tmp_path):
    """Provide a temporary file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("Test content")
    return file_path


@pytest.fixture
def sample_json(tmp_path):
    """Provide a sample JSON file."""
    import json

    file_path = tmp_path / "data.json"
    data = {"key": "value", "number": 42}
    file_path.write_text(json.dumps(data))
    return file_path
```

### Example: Configuration Fixtures

```python
# tests/fixtures.py
"""__init__ module."""

import pytest
import os


@pytest.fixture
def test_env():
    """Set up test environment variables."""
    old_env = os.environ.copy()

    # Set test environment
    os.environ["DEBUG"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        "debug": True,
        "testing": True,
        "database": "sqlite:///:memory:",
    }
```

## Fixture Scopes

Fixtures can have different scopes:

### Function Scope (Default)

```python
@pytest.fixture  # Runs for each test function
def function_fixture():
    """Runs once per test function."""
    return "data"
```

### Module Scope

```python
@pytest.fixture(scope="module")  # Runs once per module
def module_fixture():
    """Runs once per test module."""
    return "data"
```

### Session Scope

```python
@pytest.fixture(scope="session")  # Runs once per test session
def session_fixture():
    """Runs once for entire test session."""
    return "data"
```

### Example: Database Fixture with Scope

```python
# tests/fixtures.py
"""__init__ module."""

import pytest


@pytest.fixture(scope="session")
def database_connection():
    """Create database connection once per session."""
    conn = create_connection()
    yield conn
    conn.close()


@pytest.fixture
def database_transaction(database_connection):
    """Create a transaction for each test."""
    transaction = database_connection.begin()
    yield transaction
    transaction.rollback()
```

## Autouse Fixtures

Fixtures that run automatically without being requested:

```python
# tests/fixtures.py
"""__init__ module."""

import pytest


@pytest.fixture(autouse=True)
def reset_state():
    """Reset global state before each test."""
    # Runs automatically before each test
    global_state.reset()
    yield
    global_state.reset()


@pytest.fixture(autouse=True, scope="session")
def setup_logging():
    """Configure logging for test session."""
    import logging
    logging.basicConfig(level=logging.DEBUG)
```

## Parametrized Fixtures

Fixtures that provide multiple values:

```python
# tests/fixtures.py
"""__init__ module."""

import pytest


@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database_type(request):
    """Provide different database types."""
    return request.param


@pytest.fixture(params=[1, 10, 100])
def batch_size(request):
    """Provide different batch sizes."""
    return request.param
```

## Factory Fixtures

Fixtures that return factories:

```python
# tests/fixtures.py
"""__init__ module."""

import pytest


@pytest.fixture
def user_factory():
    """Provide a factory for creating users."""
    def create_user(username="testuser", email=None):
        return {
            "username": username,
            "email": email or f"{username}@example.com",
        }
    return create_user


def test_multiple_users(user_factory):
    """Test with multiple users."""
    user1 = user_factory("alice")
    user2 = user_factory("bob")
    assert user1["username"] != user2["username"]
```

## Using Pyrig's Fixtures

Pyrig provides fixtures automatically through conftest.py:

```python
# tests/test_my_module.py
"""Test module."""


def test_config_file(config_file_factory):
    """Test using pyrig's config_file_factory."""
    from pyrig.dev.configs.pyproject import PyprojectConfigFile

    TestConfig = config_file_factory(PyprojectConfigFile)
    assert TestConfig is not None


def test_builder(builder_factory):
    """Test using pyrig's builder_factory."""
    from pyrig.dev.builders.base import Builder

    class MyBuilder(Builder):
        def build(self):
            pass

    TestBuilder = builder_factory(MyBuilder)
    assert TestBuilder is not None
```

## Customization

You can add imports or utilities:

### Example: Import Common Fixtures

```python
# tests/fixtures.py
"""__init__ module."""

import pytest
from pathlib import Path
from unittest.mock import Mock


# Re-export commonly used fixtures
__all__ = [
    "user_data",
    "mock_api",
    "temp_file",
]


@pytest.fixture
def user_data():
    """Provide user data."""
    return {"username": "test"}


@pytest.fixture
def mock_api():
    """Provide mock API."""
    return Mock()


@pytest.fixture
def temp_file(tmp_path):
    """Provide temp file."""
    return tmp_path / "test.txt"
```

## Related Files

- **`tests/conftest.py`** - Pytest configuration ([conftest.md](conftest.md))
- **`tests/test_zero.py`** - Placeholder test ([zero-test.md](zero-test.md))
- **`tests/test_main.py`** - Main test ([main-test.md](main-test.md))
- **`pyproject.toml`** - Pytest configuration ([pyproject.md](pyproject.md))

## Common Issues

### Issue: Fixture not found

**Symptom:** `fixture 'my_fixture' not found`

**Cause:** Fixture not defined or not in discoverable location

**Solution:**
```python
# Ensure fixture is in tests/fixtures.py
# tests/fixtures.py
import pytest

@pytest.fixture
def my_fixture():
    """My fixture."""
    return "value"
```

### Issue: Fixture runs too often

**Symptom:** Fixture setup runs for every test

**Cause:** Default scope is "function"

**Solution:**
```python
# Use appropriate scope
@pytest.fixture(scope="module")  # Runs once per module
def expensive_fixture():
    """Expensive setup."""
    return setup_expensive_resource()
```

### Issue: Fixture cleanup not running

**Symptom:** Resources not cleaned up after tests

**Cause:** Not using yield for teardown

**Solution:**
```python
@pytest.fixture
def resource():
    """Provide resource with cleanup."""
    res = create_resource()
    yield res  # Use yield, not return
    res.cleanup()  # This runs after test
```

### Issue: Want to use fixture in another fixture

**Symptom:** How to compose fixtures?

**Cause:** Not familiar with fixture dependencies

**Solution:**
```python
@pytest.fixture
def database():
    """Provide database."""
    return create_database()


@pytest.fixture
def user(database):
    """Create user in database."""
    return database.create_user("test")
```

## Best Practices

### ✅ DO

- **Use descriptive names** - `user_data`, not `data1`
- **Add docstrings** - Explain what the fixture provides
- **Use appropriate scopes** - Optimize performance
- **Use yield for cleanup** - Ensure resources are released
- **Keep fixtures focused** - One fixture, one responsibility

### ❌ DON'T

- **Don't remove the docstring** - Pyrig expects it
- **Don't make fixtures stateful** - Each test should be independent
- **Don't use fixtures for assertions** - Use them for setup
- **Don't create circular dependencies** - Keep fixtures independent
- **Don't overuse autouse** - Only for truly global setup

## Advanced Usage

### Fixture with Conditional Behavior

```python
# tests/fixtures.py
"""__init__ module."""

import pytest
import os


@pytest.fixture
def database():
    """Provide database based on environment."""
    if os.getenv("USE_REAL_DB") == "true":
        return create_real_database()
    else:
        return create_mock_database()
```

### Fixture with Caching

```python
# tests/fixtures.py
"""__init__ module."""

import pytest
from functools import lru_cache


@lru_cache(maxsize=1)
def _create_expensive_resource():
    """Create expensive resource once."""
    return ExpensiveResource()


@pytest.fixture(scope="session")
def expensive_resource():
    """Provide cached expensive resource."""
    return _create_expensive_resource()
```

### Fixture with Markers

```python
# tests/fixtures.py
"""__init__ module."""

import pytest


@pytest.fixture
def slow_resource(request):
    """Provide resource, skip if not running slow tests."""
    if not request.config.getoption("--run-slow"):
        pytest.skip("Slow tests not enabled")
    return create_slow_resource()
```

## See Also

- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html) - Official pytest fixture docs
- [pytest Scope](https://docs.pytest.org/en/stable/fixture.html#scope) - Fixture scopes
- [pytest Parametrize](https://docs.pytest.org/en/stable/parametrize.html) - Parametrized fixtures
- [conftest.py](conftest.md) - Pytest configuration
- [Getting Started Guide](../getting-started.md) - Initial project setup



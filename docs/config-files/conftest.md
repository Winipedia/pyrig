# ConftestConfigFile

## Overview

**File Location:** `tests/conftest.py`
**ConfigFile Class:** `ConftestConfigFile`
**File Type:** Python
**Priority:** Standard

Configures pytest plugins and fixtures for your test suite. Pyrig automatically imports its comprehensive fixture library, providing factories for testing ConfigFile and Builder classes with temporary directories.

## Purpose

The `tests/conftest.py` file sets up pytest infrastructure:

- **Fixture Discovery** - Automatically registers pyrig's test fixtures
- **Plugin Configuration** - Loads pytest plugins from pyrig and dependencies
- **Test Isolation** - Provides factories that use temporary directories
- **Consistent Testing** - All projects get the same test infrastructure
- **Extensible** - You can add your own fixtures alongside pyrig's

### Why pyrig manages this file

pyrig creates `conftest.py` to:
1. **Automatic fixtures** - Projects get powerful test utilities immediately
2. **Dependency discovery** - Finds fixtures from all packages depending on pyrig
3. **Best practices** - Follows pytest plugin conventions
4. **Minimal boilerplate** - One line imports everything you need
5. **Isolation** - Fixtures use tmp_path to avoid affecting real files

The file is created during `pyrig init`. It should not be modified manually - add custom fixtures to `tests/fixtures.py` instead.

## File Structure

### Docstring

```python
"""Pytest configuration for tests.

This module configures pytest plugins for the test suite, setting up the necessary
fixtures and hooks for the different
test scopes (function, class, module, package, session).
It also import custom plugins from tests/base/scopes.
This file should not be modified manually.
"""
```

- **Purpose:** Explains the file's role
- **Warning:** Indicates the file is auto-generated

### pytest_plugins Declaration

```python
pytest_plugins = ["pyrig.dev.tests.conftest"]
```

- **Type:** List of module paths
- **Default:** `["pyrig.dev.tests.conftest"]`
- **Required:** Yes
- **Purpose:** Imports pyrig's conftest module as a pytest plugin
- **Why pyrig sets it:** Automatically registers all pyrig fixtures

**How it works:**
1. Pytest reads `tests/conftest.py`
2. Sees `pytest_plugins = ["pyrig.dev.tests.conftest"]`
3. Imports `pyrig.dev.tests.conftest`
4. That module discovers fixtures from all packages depending on pyrig
5. All fixtures become available in your tests

## Default Configuration

For a project named `my-awesome-project`:

**File location:** `tests/conftest.py`

**File contents:**
```python
"""Pytest configuration for tests.

This module configures pytest plugins for the test suite, setting up the necessary
fixtures and hooks for the different
test scopes (function, class, module, package, session).
It also import custom plugins from tests/base/scopes.
This file should not be modified manually.
"""

pytest_plugins = ["pyrig.dev.tests.conftest"]
```

## Provided Fixtures

When you import pyrig's conftest, you get these fixtures automatically:

### config_file_factory

```python
@pytest.fixture
def config_file_factory(tmp_path: Path) -> Callable[[type[ConfigFile]], type[ConfigFile]]:
    """Create a factory for ConfigFile subclasses using temporary paths."""
```

**Purpose:** Wraps ConfigFile classes to use tmp_path instead of real paths

**Usage:**
```python
def test_my_config(config_file_factory):
    # Create a test version that uses tmp_path
    TestConfig = config_file_factory(PyprojectConfigFile)

    # Now get_path() returns a path in tmp_path
    assert "tmp" in str(TestConfig.get_path())

    # Safe to call methods without affecting real files
    TestConfig().init()
```

**Why it's useful:**
- **Isolation** - Tests don't modify real config files
- **Cleanup** - tmp_path is automatically cleaned up
- **Parallel** - Tests can run in parallel safely

### builder_factory

```python
@pytest.fixture
def builder_factory(tmp_path: Path) -> Callable[[type[Builder]], type[Builder]]:
    """Create a factory for Builder subclasses using temporary paths."""
```

**Purpose:** Wraps Builder classes to use tmp_path

**Usage:**
```python
def test_my_builder(builder_factory):
    TestBuilder = builder_factory(MyBuilder)
    TestBuilder().build()
```

### Additional Fixtures

Pyrig's conftest also discovers and registers fixtures from:
- All packages that depend on pyrig
- Their `fixtures` modules
- All Python files within those modules

This means if you create a package that depends on pyrig and has a `fixtures` module, those fixtures are automatically available.

## How Fixture Discovery Works

### Discovery Process

1. **Find dependent packages** - Identifies all packages depending on pyrig
2. **Locate fixtures modules** - Finds `fixtures` module in each package
3. **Collect Python files** - Gets all `.py` files in fixtures modules
4. **Register as plugins** - Adds them to `pytest_plugins`

### Example

If you have:
```
my-awesome-project/
├── my_awesome_project/
│   └── ...
├── tests/
│   ├── conftest.py  # Imports pyrig.dev.tests.conftest
│   └── fixtures.py  # Your custom fixtures
└── pyproject.toml
```

And `my-awesome-project` depends on `pyrig`, then:
- `pyrig.dev.tests.fixtures.*` fixtures are available
- `tests.fixtures` fixtures are available (if you create them)

## Adding Custom Fixtures

**Don't modify `tests/conftest.py`**. Instead, create `tests/fixtures.py`:

```python
# tests/fixtures.py
"""Custom fixtures for my-awesome-project tests."""

import pytest


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value"}


@pytest.fixture
def mock_api(mocker):
    """Mock external API calls."""
    return mocker.patch("my_awesome_project.api.call")
```

These fixtures are automatically available in all tests.

## Running Tests

### Using pytest directly

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_my_module.py

# Run specific test
uv run pytest tests/test_my_module.py::test_my_function
```

### Using pyrig's helper

```python
from pyrig.dev.configs.testing.conftest import ConftestConfigFile

# Run all tests
ConftestConfigFile.run_tests()

# Run without raising on failure
ConftestConfigFile.run_tests(check=False)
```

## Validation

Pyrig validates that `conftest.py` contains the required import:

```python
@classmethod
def is_correct(cls) -> bool:
    """Check if the conftest.py file is valid."""
    return 'pytest_plugins = ["pyrig.dev.tests.conftest"]' in cls.get_file_content()
```

This allows you to add additional content, but the core import must remain.

## Customization

While you shouldn't modify `tests/conftest.py`, you can extend it:

### Option 1: Add fixtures to tests/fixtures.py

```python
# tests/fixtures.py
import pytest


@pytest.fixture
def database():
    """Provide a test database."""
    db = create_test_database()
    yield db
    db.cleanup()
```

### Option 2: Create additional conftest files

```python
# tests/integration/conftest.py
"""Fixtures specific to integration tests."""

import pytest


@pytest.fixture(scope="module")
def api_client():
    """Provide an API client for integration tests."""
    return APIClient(base_url="http://localhost:8000")
```

Pytest automatically discovers conftest.py files in subdirectories.

### Option 3: Add to pytest_plugins

If you absolutely need to modify `tests/conftest.py`, you can add to the list:

```python
"""Pytest configuration for tests.

This module configures pytest plugins for the test suite, setting up the necessary
fixtures and hooks for the different
test scopes (function, class, module, package, session).
It also import custom plugins from tests/base/scopes.
This file should not be modified manually.
"""

pytest_plugins = [
    "pyrig.dev.tests.conftest",
    "tests.fixtures",  # Your custom fixtures module
    "pytest_asyncio",  # External plugin
]
```

**Note:** Pyrig will preserve this on `pyrig mkroot` as long as the required import is present.

## Related Files

- **`tests/fixtures.py`** - Your custom fixtures ([fixtures-init.md](fixtures-init.md))
- **`tests/test_zero.py`** - Placeholder test ([zero-test.md](zero-test.md))
- **`tests/test_main.py`** - Main entry point test ([main-test.md](main-test.md))
- **`pyproject.toml`** - Pytest configuration ([pyproject.toml](pyproject.md))

## Common Issues

### Issue: Fixtures not found

**Symptom:** `fixture 'config_file_factory' not found`

**Cause:** conftest.py not importing pyrig's conftest

**Solution:**
```python
# Ensure tests/conftest.py contains:
pytest_plugins = ["pyrig.dev.tests.conftest"]
```

### Issue: Custom fixtures not available

**Symptom:** Your fixtures aren't found in tests

**Cause:** Fixtures not in a discoverable location

**Solution:**
```python
# Create tests/fixtures.py
# tests/fixtures.py
import pytest

@pytest.fixture
def my_fixture():
    return "value"
```

### Issue: Fixture scope issues

**Symptom:** Fixture runs more often than expected

**Cause:** Default scope is "function"

**Solution:**
```python
# Use appropriate scope
@pytest.fixture(scope="module")  # Runs once per module
def expensive_setup():
    return setup_expensive_resource()

@pytest.fixture(scope="session")  # Runs once per test session
def database():
    return create_database()
```

### Issue: conftest.py modified but tests fail

**Symptom:** Tests fail after modifying conftest.py

**Cause:** Removed required import

**Solution:**
```python
# Ensure this line is present:
pytest_plugins = ["pyrig.dev.tests.conftest"]
```

### Issue: Want to use pytest plugins

**Symptom:** Need to add pytest-asyncio, pytest-django, etc.

**Solution:**
```bash
# Install the plugin
uv add --group dev pytest-asyncio

# Add to pytest_plugins
# tests/conftest.py
pytest_plugins = [
    "pyrig.dev.tests.conftest",
    "pytest_asyncio",
]
```

## Best Practices

### ✅ DO

- **Use config_file_factory** - For testing ConfigFile classes
- **Use builder_factory** - For testing Builder classes
- **Create tests/fixtures.py** - For custom fixtures
- **Use appropriate scopes** - function/module/session
- **Keep conftest.py minimal** - Add fixtures elsewhere

### ❌ DON'T

- **Don't remove the required import** - Tests will break
- **Don't add complex logic** - Keep conftest.py simple
- **Don't modify real files in tests** - Use tmp_path
- **Don't use global state** - Fixtures should be isolated
- **Don't skip fixture cleanup** - Use yield for teardown

## Advanced Usage

### Parametrized Fixtures

```python
# tests/fixtures.py
import pytest


@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    """Provide different database backends."""
    return create_database(request.param)
```

### Fixture Dependencies

```python
@pytest.fixture
def database():
    """Provide a database."""
    return create_database()


@pytest.fixture
def user(database):
    """Create a test user in the database."""
    return database.create_user("test@example.com")
```

### Autouse Fixtures

```python
@pytest.fixture(autouse=True)
def reset_state():
    """Reset global state before each test."""
    global_state.reset()
    yield
    global_state.reset()
```

### Factory Fixtures

```python
@pytest.fixture
def user_factory(database):
    """Provide a factory for creating users."""
    def create_user(email: str):
        return database.create_user(email)
    return create_user


def test_multiple_users(user_factory):
    user1 = user_factory("user1@example.com")
    user2 = user_factory("user2@example.com")
    assert user1.id != user2.id
```

## See Also

- [pytest Documentation](https://docs.pytest.org/) - Official pytest docs
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html) - Fixture guide
- [pytest Plugins](https://docs.pytest.org/en/stable/plugins.html) - Plugin system
- [fixtures.py](fixtures-init.md) - Custom fixtures file
- [test_zero.py](zero-test.md) - Placeholder test
- [test_main.py](main-test.md) - Main test file
- [Getting Started Guide](../getting-started.md) - Initial project setup



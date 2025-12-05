# Testing: Test Generation System

This document describes pyrig's automatic test generation system, which creates test skeletons that mirror your source code structure and validates test coverage at runtime.

## Overview

pyrig enforces a strict testing discipline: every module, class, and function in your source code must have a corresponding test. When tests are missing, pyrig automatically generates skeleton test files with `NotImplementedError` placeholders, ensuring you never forget to write tests.

The system consists of three integrated parts:
1. **Test Generation** — Creates test files mirroring source structure
2. **Coverage Validation** — Fails tests when coverage is incomplete
3. **Fixture System** — Provides scoped fixtures for setup/teardown

## Source-to-Test Mapping

pyrig follows pytest naming conventions to create a bidirectional mapping between source and test objects:

```
Source                              Test
──────────────────────────────────────────────────────────────
your_project/                   →   tests/test_your_project/
your_project/utils.py           →   tests/test_your_project/test_utils.py
your_project/utils/helpers.py   →   tests/test_your_project/test_utils/test_helpers.py

def calculate()                 →   def test_calculate()
class Calculator                →   class TestCalculator
def Calculator.add()            →   def TestCalculator.test_add()
```

### Naming Conventions

| Source Type | Test Prefix | Example |
|-------------|-------------|---------|
| Module | `test_` | `utils.py` → `test_utils.py` |
| Function | `test_` | `calculate()` → `test_calculate()` |
| Class | `Test` | `Calculator` → `TestCalculator` |
| Method | `test_` | `add()` → `test_add()` |

## When Tests Are Generated

Tests are generated in three scenarios:

### 1. During `pyrig init`

The full initialization runs `create_tests` as part of its setup steps:

```python
SETUP_STEPS = [
    ConfigFile.init_priority_config_files,
    PyprojectConfigFile.install_dependencies,
    PyprojectConfigFile.update_dependencies,
    run_create_root,
    run_create_tests,           # ← Generates test skeletons
    PreCommitConfigConfigFile.run_hooks,
    ConftestConfigFile.run_tests,
    PyprojectConfigFile.install_dependencies,
]
```

### 2. Running `pyrig create-tests`

You can manually trigger test generation:

```bash
uv run pyrig create-tests
```

### 3. Automatically During pytest

Session and module fixtures automatically detect missing tests and generate them:

```python
# Session fixture: checks all modules have test modules
@autouse_session_fixture
def assert_all_modules_tested():
    for package, modules in walk_package(src_package):
        for module in modules:
            test_module = import_module_with_default(
                make_test_obj_importpath_from_obj(module)
            )
            if test_module is None:
                create_tests()  # Auto-generate missing tests

# Module fixture: checks all functions/classes have tests
@autouse_module_fixture
def assert_all_funcs_and_classes_tested(request):
    assert_no_untested_objs(request.module)
```

## How Test Generation Works

### Step 1: Walk the Source Package

```python
def create_tests():
    create_tests_for_package(get_src_package())

def create_tests_for_package(package):
    for pkg, modules in walk_package(package):
        create_test_package(pkg)      # Create tests/test_{pkg}/__init__.py
        for module in modules:
            create_test_module(module)  # Create tests/test_{pkg}/test_{module}.py
```

### Step 2: Generate Test Module Content

For each source module, pyrig:
1. Gets existing test module content (preserves existing tests)
2. Finds all functions/classes in source module
3. Identifies which don't have corresponding tests
4. Appends skeleton tests for missing items

```python
def get_test_module_content(module):
    test_module = get_test_obj_from_obj(module)
    content = get_module_content_as_str(test_module)
    content = get_test_functions_content(module, test_module, content)
    content = get_test_classes_content(module, test_module, content)
    return content
```

### Step 3: Generate Skeleton Functions

For each untested function, a skeleton is appended:

```python
def {test_func_name}() -> None:
    """Test function."""
    raise NotImplementedError
```

### Step 4: Generate Skeleton Classes

For each untested class or method:

```python
class Test{ClassName}:
    """Test class."""

    def test_{method_name}(self) -> None:
        """Test method."""
        raise NotImplementedError
```

## Example: Source to Test

### Source File

```python
# your_project/src/calculator.py
"""Calculator module."""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

class Calculator:
    """Calculator class."""

    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    def divide(self, a: int, b: int) -> float:
        """Divide two numbers."""
        return a / b
```

### Generated Test File

```python
# tests/test_your_project/test_src/test_calculator.py
"""Tests for your_project.src.calculator module."""


def test_add() -> None:
    """Test function."""
    raise NotImplementedError


class TestCalculator:
    """Test class."""

    def test_multiply(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_divide(self) -> None:
        """Test method."""
        raise NotImplementedError
```

When you implement the tests and add a new function to the source, pyrig will detect it's untested and add a new skeleton on the next test run.

## The Fixture System

pyrig provides a structured fixture system organized by scope. Fixtures are automatically discovered and registered via `pytest_plugins` in `conftest.py`.

### Fixture Scopes

| Scope | Runs | Use Case |
|-------|------|----------|
| `function` | Before each test function | Test-specific setup, isolation |
| `class` | Before each test class | Shared state within a test class |
| `module` | Before each test module | Module-level setup (e.g., mock servers) |
| `package` | Before each test package | Package-level resources |
| `session` | Once per test session | Expensive setup (e.g., database, validation) |

### Fixture Directory Structure

```
your_project/
└── dev/
    └── tests/
        └── fixtures/
            ├── __init__.py
            ├── factories.py           # Factory fixtures for testing
            └── scopes/
                ├── __init__.py
                ├── function.py         # Function-scoped fixtures
                ├── class_.py           # Class-scoped fixtures
                ├── module.py           # Module-scoped fixtures
                ├── package.py          # Package-scoped fixtures
                └── session.py          # Session-scoped fixtures
```

### Built-in Session Fixtures

pyrig includes several session-scoped fixtures that run automatically:

| Fixture | Purpose |
|---------|---------|
| `assert_root_is_correct` | Validates all ConfigFile settings are correct |
| `assert_no_namespace_packages` | Ensures all packages have `__init__.py` |
| `assert_all_src_code_in_one_package` | Enforces single source package structure |
| `assert_src_package_correctly_named` | Verifies consistent naming across project folder, package, and pyproject.toml |
| `assert_all_modules_tested` | Creates missing test modules |
| `assert_no_unit_test_package_usage` | Enforces pytest over unittest |
| `assert_dependencies_are_up_to_date` | Updates dependencies before tests |
| `assert_pre_commit_is_installed` | Ensures pre-commit hooks are installed |
| `assert_src_runs_without_dev_deps` | Verifies source works without dev dependencies |

### Built-in Module Fixtures

```python
@autouse_module_fixture
def assert_all_funcs_and_classes_tested(request):
    """Verify all functions and classes in source have corresponding tests."""
    assert_no_untested_objs(request.module)
```

### Built-in Class Fixtures

```python
@autouse_class_fixture
def assert_all_methods_tested(request):
    """Verify all methods in source class have corresponding tests."""
    assert_no_untested_objs(request.node.cls)
```

## Creating Custom Fixtures

### Basic Scoped Fixture

```python
# your_project/dev/tests/fixtures/scopes/session.py
from pyrig.dev.tests.utils.decorators import session_fixture

@session_fixture
def database_connection():
    """Create a database connection for the test session."""
    conn = create_connection()
    yield conn
    conn.close()
```

### Autouse Fixture

```python
# your_project/dev/tests/fixtures/scopes/function.py
from pyrig.dev.tests.utils.decorators import autouse_function_fixture

@autouse_function_fixture
def reset_mocks():
    """Reset all mocks before each test."""
    yield
    mock.patch.stopall()
```

### Factory Fixtures

pyrig provides factory fixtures for testing ConfigFile and Builder classes in isolation:

```python
def test_my_config(config_file_factory):
    """Test a config file using a temporary directory."""
    TestConfig = config_file_factory(MyConfigFile)
    # TestConfig.get_path() now returns a path in tmp_path
    TestConfig()
    assert TestConfig.get_path().exists()

def test_my_builder(builder_factory):
    """Test a builder using a temporary directory."""
    TestBuilder = builder_factory(MyBuilder)
    # TestBuilder.get_artifacts_dir() now returns a path in tmp_path
    TestBuilder()
    assert TestBuilder.get_artifacts_dir().exists()
```

## Fixture Decorators Reference

pyrig provides convenience decorators in `pyrig.dev.tests.utils.decorators`:

```python
# Regular fixtures (not autouse)
function_fixture    # scope="function"
class_fixture       # scope="class"
module_fixture      # scope="module"
package_fixture     # scope="package"
session_fixture     # scope="session"

# Autouse fixtures (run automatically)
autouse_function_fixture    # scope="function", autouse=True
autouse_class_fixture       # scope="class", autouse=True
autouse_module_fixture      # scope="module", autouse=True
autouse_package_fixture     # scope="package", autouse=True
autouse_session_fixture     # scope="session", autouse=True

# Skip markers
skip_fixture_test           # Skip tests that are fixtures
skip_in_github_actions      # Skip tests that can't run in CI
```

## How Fixtures Are Discovered

The discovery mechanism in `conftest.py`:

```python
# pyrig/dev/tests/conftest.py
fixtures_pkgs = get_same_modules_from_deps_depen_on_dep(fixtures, pyrig)

pytest_plugin_paths = []
for pkg in fixtures_pkgs:
    for path in absolute_path.rglob("*.py"):
        pytest_plugin_paths.append(path)

pytest_plugins = [to_module_name(path) for path in pytest_plugin_paths]
```

This discovers fixtures from:
1. pyrig's own fixtures
2. All packages that depend on pyrig
3. All Python files in their `fixtures/` directories

## Running Tests

### Standard Test Run

```bash
uv run pytest
```

### With Verbose Output

```bash
uv run pytest -v
```

### Running Specific Tests

```bash
uv run pytest tests/test_your_project/test_src/test_calculator.py
uv run pytest -k "test_add"
```

### Test Configuration

Tests are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # Allow assert statements in tests
```

## The Zero Test

pyrig generates a special `test_zero.py` that serves as a baseline:

```python
# tests/test_zero.py
"""Contains an empty test."""

def test_zero() -> None:
    """Empty test.

    Exists so that when no tests are written yet the base fixtures are executed.
    """
```

This ensures that even with no user-written tests, the session fixtures run and validate the project structure.

## Key Design Decisions

### Why Auto-Generate Tests?

1. **No forgotten tests**: Every function and class gets a test skeleton
2. **Consistent structure**: Test files mirror source structure exactly
3. **Early detection**: Missing tests fail immediately, not in code review
4. **Low friction**: `NotImplementedError` placeholders are easy to implement

### Why Fail on Missing Tests?

pyrig's philosophy is that untested code is unfinished code. By failing tests when coverage is incomplete:

1. **CI catches gaps**: Missing tests fail the build
2. **Skeletons guide work**: Generated tests show exactly what needs implementation
3. **Structure is enforced**: Test file organization matches source organization

### Why Scope-Based Fixtures?

Different test scenarios need different setup/teardown granularity:

- **Function scope**: Maximum isolation, but slower for expensive setup
- **Module scope**: Balance of isolation and performance
- **Session scope**: Best for expensive, read-only resources (validation, connections)

pyrig's autouse fixtures at each scope ensure consistent validation without manual configuration.

## Disable a test file
Just empty the file. pytest will never invoke it and pyrigs module scoped fixture will also not be invoked and not raise an error that tests are missing.

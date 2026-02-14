# Fixture Sharing

pyrig automatically shares fixtures across all packages in the dependency chain
through a multi-package plugin architecture.

## How It Works

Every package depending on pyrig inherits all fixtures from pyrig and its
dependencies:

```mermaid
graph TD
    A[pyrig.rig.tests.fixtures] --> B[Package A fixtures]
    B --> C[Package B fixtures]
    C --> D[Package C fixtures]

    A -.->|Available in| B
    A -.->|Available in| C
    A -.->|Available in| D
    B -.->|Available in| C
    B -.->|Available in| D
    C -.->|Available in| D

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style D fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
```

## Plugin Discovery

The discovery process happens automatically in `tests/conftest.py`:

```mermaid
sequenceDiagram
    participant T as tests/conftest.py
    participant P as pyrig.rig.tests.conftest
    participant D as discover_equivalent_modules_across_dependents
    participant F as Fixture Modules

    T->>P: Import as pytest plugin
    P->>D: Discover fixtures modules across dependents
    D-->>P: [pyrig.rig.tests.fixtures, package_a.rig.tests.fixtures, ...]
    P->>F: Find all .py files in each fixtures module
    F-->>P: [pyrig.rig.tests.fixtures.__init__, ...]
    P->>P: Register all Python files as pytest plugins
    P-->>T: All fixtures available

    Note over T,F: All fixtures from entire dependency chain now available
```

### Discovery Steps

```mermaid
graph TD
    A[Start: tests/conftest.py] --> B[Import pyrig.rig.tests.conftest]
    B --> C[Call cached discover_equivalent_modules_across_dependents]
    C --> D[Find equivalent fixtures modules across dependents]
    D --> E[For each fixtures module...]

    E --> F[Get module's absolute path]
    F --> G{Module exists?}
    G -->|Yes| H[Find all .py files in module]
    G -->|No| E
    H --> I[Convert paths to module names]
    I --> J[Add to pytest_plugins list]
    J --> E

    E --> K[All packages processed]
    K --> L[pytest loads all plugins]
    L --> M[All fixtures available in tests]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style D fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style E fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style F fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style H fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style I fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style J fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style L fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style M fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

**Detailed Steps:**

1. **Discover equivalent fixtures modules**: Uses
   `discover_equivalent_modules_across_dependents` (which internally uses
   `DependencyGraph`) to find `rig.tests.fixtures` in pyrig and all dependent
   packages
2. **Collect Python files**: Recursively finds all `.py` files in each
   discovered fixtures module
3. **Convert to module names**: Converts file paths to dotted module names
4. **Register as plugins**: Adds all module names to `pytest_plugins` list

## Integration

### In Your Package

Pyrig will generate `tests/conftest.py`:

```python
"""Pytest configuration for tests."""

pytest_plugins = ["pyrig.rig.tests.conftest"]
```

This single line activates:

- All pyrig fixtures
- All fixtures from packages you depend on
- Automatic fixture discovery for your package
- All autouse fixtures from the entire chain

### Adding Custom Fixtures

Create fixtures in your package's fixtures module:

```text
myapp/
└── rig/
    └── tests/
        └── fixtures/
            ├── __init__.py
            ├── my_fixtures.py      # Custom fixtures
```

**Important**: Unlike the CLI framework (which auto-decorates functions as Typer
commands), fixtures must be explicitly decorated with `@pytest.fixture` from
pytest (or its scoped variants like `@pytest.fixture(scope="session")`).

Pyrig does not auto-decorate fixture functions.

These fixtures automatically become available to:

- Your package's tests
- All packages that depend on your package

## Built-in Fixtures

### Factory Fixtures

#### `config_file_factory`

Creates test versions of `ConfigFile` subclasses using temporary paths:

```python
def test_my_config(config_file_factory):
    TestConfig = config_file_factory(MyConfigFile)
    # TestConfig.path() returns path in tmp_path
    config = TestConfig()
    assert TestConfig.path().exists()
```

**Purpose**: Isolate config file tests from actual project files. Prevents file
generation in your project if you define custom subclasses of ConfigFile.

#### Testing BuilderConfigFile subclasses

Use `config_file_factory` to create test versions of `BuilderConfigFile`
subclasses using temporary paths:

```python
def test_my_builder(config_file_factory):
    TestBuilder = config_file_factory(MyBuilder)
    # TestBuilder.path() returns path in tmp_path
    builder = TestBuilder()
    builder.build()
    assert TestBuilder.parent_path().exists()
```

**Purpose**: Isolate artifact generation tests from actual build directories.

### Assertion Fixtures

#### `main_test_fixture`

Tests that the main entry point works correctly:

```python
def test_main(main_test_fixture: None) -> None:
    """Test main entry point."""
    assert main_test_fixture is None
```

**Purpose**: Verify CLI `--help` works and main function is callable.

## Fixture Scopes

Use pytest's built-in `scope` parameter for custom fixtures:

```python
import pytest

@pytest.fixture(scope="session")
def database_connection():
    """Shared across entire test session."""
    return create_connection()

@pytest.fixture(scope="module")
def module_setup():
    """Shared across test module."""
    return setup_module()
```

`pyrig.rig.utils.testing` provides skip markers for conditional test execution:

- `skip_fixture_test` — skip placeholder tests for fixture functions
- `skip_in_github_actions` — skip tests that cannot run in CI
- `skip_if_no_internet` — skip tests requiring internet connectivity

## Multi-Package Example

```text
pyrig (base package)
├── fixtures: config_file_factory, main_test_fixture
│
Package A (depends on pyrig)
├── fixtures: database_fixture, api_client_fixture
│   └── Inherits: All pyrig fixtures
│
Package B (depends on Package A)
├── fixtures: custom_fixture
    └── Inherits: All pyrig + Package A fixtures

When Package B tests run:
✓ config_file_factory (from pyrig)
✓ main_test_fixture (from pyrig)
✓ database_fixture (from Package A)
✓ api_client_fixture (from Package A)
✓ custom_fixture (from Package B)
```

All fixtures are automatically discovered and available without any additional
configuration.

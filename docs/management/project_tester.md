# ProjectTester (pytest)

Type-safe wrapper for [pytest](https://pytest.org/), the Python testing
framework.

## Overview

`ProjectTester` wraps pytest commands for:

- Running tests (`pytest`)
- CI-specific testing with coverage XML output

Tests are executed directly via pytest (not through uv run).

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_run_tests_in_ci_args(*args)` | `pytest --log-cli-level=INFO --cov-report=xml` | Run tests with CI flags |

## Usage

```python
from pyrig.dev.management.project_tester import ProjectTester

# Run tests in CI mode (with logging and XML coverage)
ProjectTester.L.get_run_tests_in_ci_args().run()

# Run specific tests in CI mode
ProjectTester.L.get_run_tests_in_ci_args("tests/test_core.py").run()

# Run with additional flags
ProjectTester.L.get_run_tests_in_ci_args("-v", "--tb=short").run()
```

## Subclassing Example

To add custom default flags:

```python
# myapp/dev/management/project_tester.py
from pyrig.dev.management.project_tester import ProjectTester as BasePT
from pyrig.src.processes import Args

class ProjectTester(BasePT):
    @classmethod
    def get_run_tests_in_ci_args(cls, *args: str) -> Args:
        # Add parallel execution
        return super().get_run_tests_in_ci_args("-n", "auto", *args)
```

## Related

- [Architecture](architecture.md) - How the Tool system works
- [Tooling - Pytest](../more/tooling.md#pytest) - Why pyrig uses pytest
- [pyproject.toml - Pytest](../configs/pyproject.md#pytest-test-runner) - pytest
  configuration
- [Tests Documentation](../tests/index.md) - Testing infrastructure

# ProjectTester (pytest)

Type-safe wrapper for [pytest](https://pytest.org/), the Python testing
framework.

## Subclassing Example

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

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - Pytest](../more/tooling.md#pytest) - Why pyrig uses pytest
- [Tests Documentation](../tests/index.md) - Testing infrastructure

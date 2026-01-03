# SecurityChecker (bandit)

Type-safe wrapper for [Bandit](https://bandit.readthedocs.io/), the Python
security linter.

Bandit finds common security issues in Python code like SQL injection, hardcoded
passwords, and unsafe deserialization.

## Subclassing Example

```python
# myapp/dev/management/security_checker.py
from pyrig.dev.management.security_checker import SecurityChecker as BaseSC
from pyrig.src.processes import Args

class SecurityChecker(BaseSC):
    @classmethod
    def get_run_with_config_args(cls, *args: str) -> Args:
        return super().get_run_with_config_args("-q", *args)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - Bandit](../more/tooling.md#bandit) - Why pyrig uses Bandit

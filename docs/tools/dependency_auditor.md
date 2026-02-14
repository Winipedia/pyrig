# DependencyAuditor (pip-audit)

Type-safe wrapper for [pip-audit](https://github.com/pypa/pip-audit), a tool
that checks *installed dependencies* for known vulnerabilities.

This complements Bandit:

- Bandit scans your code for insecure patterns.
- pip-audit scans your dependencies for known CVEs/advisories.

## Subclassing Example

```python
# myapp/rig/tools/dependency_auditor.py
from pyrig.rig.tools.dependency_auditor import DependencyAuditor as BaseDA
from pyrig.src.processes import Args


class DependencyAuditor(BaseDA):
    def audit_args(self, *args: str) -> Args:
        # Example: enforce a stable machine-readable output format
        return super().audit_args("--format", "json", *args)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - pip-audit](../more/tooling.md#pip-audit) - Why pyrig uses pip-audit

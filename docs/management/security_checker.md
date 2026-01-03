# SecurityChecker (bandit)

Type-safe wrapper for [Bandit](https://bandit.readthedocs.io/), the Python
security linter.

## Overview

`SecurityChecker` wraps bandit commands for:

- Security scanning (`bandit`)
- Recursive directory scanning (`bandit -r`)
- Configuration-based scanning (`bandit -c pyproject.toml`)

Bandit finds common security issues in Python code like SQL injection, hardcoded
passwords, and unsafe deserialization.

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_run_args(*args)` | `bandit` | Run bandit with arguments |
| `get_run_with_config_args(*args)` | `bandit -c pyproject.toml -r .` | Run with pyproject config |

## Usage

```python
from pyrig.dev.management.security_checker import SecurityChecker

# Run with pyproject.toml config
SecurityChecker.L.get_run_with_config_args().run()

# Scan specific directory
SecurityChecker.L.get_run_args("-r", "src/").run()

# Scan with severity filter
SecurityChecker.L.get_run_args("-r", ".", "-ll").run()  # Medium+ severity
```

## Subclassing Example

To add custom default flags:

```python
# myapp/dev/management/security_checker.py
from pyrig.dev.management.security_checker import SecurityChecker as BaseSC
from pyrig.src.processes import Args

class SecurityChecker(BaseSC):
    @classmethod
    def get_run_with_config_args(cls, *args: str) -> Args:
        # Add quiet mode
        return super().get_run_with_config_args("-q", *args)
```

## Related

- [Architecture](architecture.md) - How the Tool system works
- [Tooling - Bandit](../more/tooling.md#bandit) - Why pyrig uses Bandit
- [pyproject.toml - Bandit](../configs/pyproject.md#bandit-security-scanner) -
  Bandit configuration

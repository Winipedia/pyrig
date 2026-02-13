# TypeChecker (ty)

Type-safe wrapper for [ty](https://github.com/astral-sh/ty), Astral's fast
Python type checker.

ty is a Rust-based type checker from the creators of Ruff and uv, designed for
speed and accuracy.

## Subclassing Examples

### Extending Behavior

```python
# myapp/rig/tools/type_checker.py
from pyrig.rig.tools.type_checker import TypeChecker as BaseTC
from pyrig.src.processes import Args

class TypeChecker(BaseTC):
    @classmethod
    def check_args(cls, *args: str) -> Args:
        return super().check_args("--verbose", *args)
```

### Replacing with mypy

```python
# myapp/rig/tools/type_checker.py
from pyrig.rig.tools.type_checker import TypeChecker as BaseTC
from pyrig.src.processes import Args

class TypeChecker(BaseTC):
    @classmethod
    def name(cls) -> str:
        return "mypy"

    @classmethod
    def check_args(cls, *args: str) -> Args:
        # mypy uses different command syntax than ty
        return cls.args(*args)  # mypy doesn't need 'check' subcommand
```

Because pyrig uses `TypeChecker.I` internally (including in prek config
generation), this override automatically applies everywhere - no need to modify
prek config or other components.

**Note**: When replacing type checkers, you may need to override
`check_args()` since different tools use different command patterns. The
example above shows how mypy differs from ty (which uses `ty check`).
You might have to adjust other files as well. E.g. pyproject.toml to add mypy
as a dev dependency or to add mypy configuration.

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - ty](../more/tooling.md#ty) - Why pyrig uses ty

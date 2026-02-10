# PackageManager (uv)

Type-safe wrapper for [uv](https://github.com/astral-sh/uv), pyrig's primary
package manager.

uv is a Rust-based package manager that replaces pip, poetry, virtualenv, and
setuptools with 10-100x faster performance.

## Subclassing Example

```python
# myapp/rig/tools/package_manager.py
from pyrig.rig.tools.package_manager import PackageManager as BasePM
from pyrig.src.processes import Args

class PackageManager(BasePM):
    @classmethod
    def get_install_dependencies_args(cls, *args: str) -> Args:
        return super().get_install_dependencies_args("--frozen", *args)
```

## Replacing uv

**Not recommended.** uv is deeply integrated into pyrig - it's used for running
commands, installing packages, building, publishing, and version management.
Replacing it would require subclassing nearly every component.

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - uv](../more/tooling.md#uv) - Why pyrig uses uv

# PackageManager (uv)

Type-safe wrapper for [uv](https://github.com/astral-sh/uv), pyrig's primary
package manager.

## Overview

`PackageManager` wraps uv commands for:

- Project initialization (`uv init`)
- Dependency management (`uv add`, `uv sync`, `uv lock`)
- Command execution (`uv run`)
- Building and publishing (`uv build`, `uv publish`)
- Version management (`uv version`)

uv is a Rust-based package manager that replaces pip, poetry, virtualenv, and
setuptools with 10-100x faster performance.

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_init_project_args()` | `uv init` | Initialize a new project |
| `get_run_args(*args)` | `uv run` | Run a command in the venv |
| `get_add_dependencies_args(*pkgs)` | `uv add` | Add runtime dependencies |
| `get_add_dev_dependencies_args(*pkgs)` | `uv add --group dev` | Add dev dependencies |
| `get_install_dependencies_args()` | `uv sync` | Install all dependencies |
| `get_update_dependencies_args()` | `uv lock --upgrade` | Update lock file |
| `get_update_self_args()` | `uv self update` | Update uv itself |
| `get_patch_version_args()` | `uv version --bump patch` | Bump patch version |
| `get_build_args()` | `uv build` | Build the package |
| `get_publish_args(token=...)` | `uv publish --token` | Publish to PyPI |
| `get_version_args()` | `uv version` | Show version |
| `get_version_short_args()` | `uv version --short` | Show version (short) |

## Usage

```python
from pyrig.dev.management.package_manager import PackageManager

# Install dependencies
PackageManager.L.get_install_dependencies_args().run()

# Add a package
PackageManager.L.get_add_dependencies_args("requests").run()

# Add a dev package
PackageManager.L.get_add_dev_dependencies_args("pytest-cov").run()

# Run a command
PackageManager.L.get_run_args("pytest", "-v").run()

# Get version string
result = PackageManager.L.get_version_short_args().run()
version = result.stdout.decode().strip()
```

## Subclassing Example

To customize package manager behavior (e.g., add default flags):

```python
# myapp/dev/management/package_manager.py
from pyrig.dev.management.package_manager import PackageManager as BasePM
from pyrig.src.processes import Args

class PackageManager(BasePM):
    @classmethod
    def get_install_dependencies_args(cls, *args: str) -> Args:
        # Always use frozen lockfile
        return super().get_install_dependencies_args("--frozen", *args)
```

## Replacing uv

**Not recommended.** uv is deeply integrated into pyrig - it's used for running
commands, installing packages, building, publishing, and version management.
Replacing it would require subclassing nearly every component.

See [Replacing Tools](architecture.md#replacing-tools) for details.

## Related

- [Architecture](architecture.md) - How the Tool system works
- [Tooling - uv](../more/tooling.md#uv) - Why pyrig uses uv

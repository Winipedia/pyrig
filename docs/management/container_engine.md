# ContainerEngine (podman)

Type-safe wrapper for [Podman](https://podman.io/), the daemonless container
engine.

## Overview

`ContainerEngine` wraps podman commands for:

- Building images (`podman build`)
- Saving images (`podman save`)

Podman is used primarily for creating containerized builds, particularly
PyInstaller executables in a reproducible Linux environment.

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_build_args(*args, project_name)` | `podman build -t <name> .` | Build container image |
| `get_save_args(*args, image_file, image_path)` | `podman save -o <path> <name>` | Save image to file |

## Usage

```python
from pathlib import Path
from pyrig.dev.management.container_engine import ContainerEngine

# Build an image
ContainerEngine.L.get_build_args(project_name="myapp").run()

# Build with custom Dockerfile
ContainerEngine.L.get_build_args(
    "-f", "Dockerfile.prod",
    project_name="myapp"
).run()

# Save image to file
ContainerEngine.L.get_save_args(
    image_file=Path("myapp"),
    image_path=Path("dist/myapp.tar")
).run()
```

## Subclassing Example

To switch to Docker:

```python
# myapp/dev/management/container_engine.py
from pyrig.dev.management.container_engine import ContainerEngine as BaseCE

class ContainerEngine(BaseCE):
    @classmethod
    def name(cls) -> str:
        return "docker"
```

Note: You also need to subclass any other methods that might do `podman`
-specific things, like `get_save_args()` which uses `image_file.stem` as the
image name.

See [Replacing Tools](architecture.md#replacing-tools) for the full Docker
migration example including workflow changes.

## Related

- [Architecture](architecture.md) - How the Tool system works
- [Tooling - Podman](../more/tooling.md#podman) - Why pyrig uses Podman
- [Build Documentation](../configs/workflows/build.md) - Container build workflow

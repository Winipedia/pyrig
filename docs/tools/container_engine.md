# ContainerEngine (podman)

Type-safe wrapper for [Podman](https://podman.io/), the daemonless container
engine.

Podman is used for creating containerized builds, particularly PyInstaller
executables in a reproducible Linux environment.

## Replacing with Docker

Switching to Docker requires **two changes** because workflow steps use
hardcoded GitHub Actions (not the `.I` pattern):

### 1. Subclass the Tool

```python
# myapp/rig/tools/container_engine.py
from pyrig.rig.tools.container_engine import ContainerEngine as BaseCE

class ContainerEngine(BaseCE):
    def name(self) -> str:
        return "docker"
```

### 2. Override WorkflowConfigFile Steps

The workflow uses a hardcoded GitHub Action to install Podman. You must also
override this:

```python
# myapp/rig/configs/base/workflow.py
from pyrig.rig.configs.base.workflow import WorkflowConfigFile as BaseWorkflowConfigFile

class WorkflowConfigFile(BaseWorkflowConfigFile):
    @classmethod
    def step_install_container_engine(cls, *, step=None):
        return cls.step(
            step_func=cls.step_install_container_engine,
            uses="docker/setup-buildx-action@v3",
            step=step,
        )
```

This is an example of **static vs dynamic** - see
[Architecture](architecture.md#dynamic-vs-static-when-each-applies) for why some
components require explicit overrides.

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - Podman](../more/tooling.md#podman) - Why pyrig uses Podman

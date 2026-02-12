# RemoteVersionController (GitHub)

Constructs GitHub-related URLs for repository, documentation, CI/CD, and badges.

Unlike other Tool wrappers that wrap external CLI tools, RemoteVersionController
generates URLs dynamically from your git remote configuration. It's used
internally by pyrig to populate `[project.urls]` in pyproject.toml and badge
links in README files.

## Subclassing Example

```python
# myapp/rig/tools/remote_version_controller.py
from pyrig.rig.tools.remote_version_controller import (
    RemoteVersionController as BaseRVC,
)
from pyrig.rig.tools.version_controller import VersionController

class RemoteVersionController(BaseRVC):
    @classmethod
    def issues_url(cls) -> str:
        # Use custom issues domain instead of GitHub
        return f"https://issues.example.com
```

## Related

- [Architecture](architecture.md) - Design philosophy and the `.L` pattern
- [VersionController](version_controller.md) - Local git operations wrapper

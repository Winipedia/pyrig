# RemoteVersionController (GitHub)

Constructs GitHub-related URLs and badge Markdown for repository, CI/CD, and badges.

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

class RemoteVersionController(BaseRVC):
    def issues_url(self) -> str:
        # Use custom issues domain instead of GitHub
        return f"https://issues.example.com/{self.name()}"
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [VersionController](version_controller.md) - Local git operations wrapper

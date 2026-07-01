# Tools

Every external CLI tool pyrig interacts with is wrapped in a `Tool` subclass.
`Tool` is a `DependencySubclass`, so the same override and discovery rules
apply — see [Architecture](architecture.md) for the conceptual overview.

---

## Implementing a New Tool

Subclass `Tool` and implement the required members:

| Member | Purpose |
|--------|---------|
| `name()` | Executable name (e.g. `"git"`) |
| `group()` | Badge category — use a `Group` constant |
| `image_url()` | Badge image URL |
| `link_url()` | Badge link URL |

Add `*_args()` methods that return `Args` for each command the tool supports:

```python
from pyrig.rig.tools.base.tool import Tool, Group
from pyrig.core.subprocesses import Args

class MyTool(Tool):
    def name(self) -> str:
        return "mytool"

    def group(self) -> str:
        return Group.TOOLING

    def image_url(self) -> str:
        return "https://img.shields.io/badge/my-badge"

    def link_url(self) -> str:
        return "https://mytool.io"

    def build_args(self, *extra: str) -> Args:
        return self.args("build", *extra)
```

Place the class anywhere under `<your_package>.rig.tools` and it will be
discovered automatically — no registration needed.

### Optional Overrides

- **`version_control_ignore_paths()`** — Paths (relative to project root) this
  tool writes that should be added to `.gitignore` automatically.
- **`dev_dependencies()`** — Package names to add to the project's dev
  dependency group.

---

## Overriding an Existing Tool

Run `pyrig mk subcls`, search for the tool class you want to change, and select
it. A correctly placed subclass skeleton is generated for you. Override
whichever methods need changing — the rest of the behaviour is inherited.

---

## Using a Tool

Every `Tool` subclass is a `DependencySubclass`, so use `.I` to get a cached
instance of the leaf subclass (respecting any downstream override):

```python
PackageManager.I.install_dependencies_args().run()  # → uv sync
VersionController.I.commit_with_msg_args("init").run()  # → git commit -m init
```

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

    def build_args(self, *args: str) -> Args:
        return self.args("build", *args)
```

Place the class anywhere under `<your_package>.rig.tools` and it will be
discovered automatically — no registration needed.

For `image_url()`, prefer the tool's own standard badge if it publishes one
— `ruff` and `ty` each maintain a shields.io endpoint badge in their own repo
(`img.shields.io/endpoint?url=...`), and pointing at that is best practice,
since it's the badge people already recognize for that tool. Only fall back
to defining a plain shields.io static badge,
`https://img.shields.io/badge/LABEL-VALUE-COLOR`, when no standard badge
exists: LABEL a short category noun for what it represents (e.g. `shell`,
`JSON`, `secrets`) rather than the tool's own name, VALUE built from
`self.shield_name()` (which escapes hyphens the way shields.io's URL
segments require), and COLOR a plain CSS color name or hex code. For
`link_url()`, point wherever is most useful to the reader — `DocsBuilder`'s
badge links to this project's own built documentation site, not zensical's
homepage — and only fall back to the tool's own repository when there's no
more useful destination. `group()` decides which section the badge is
grouped under in the generated `README.md` and docs home page; badges within
a group are then sorted automatically, alphabetically by class name.

### Optional Overrides

- **`version_control_ignore_patterns()`** — Paths (relative to project root) this
  tool writes that should be added to `.gitignore` automatically.
- **`dev_dependencies()`** — Package names to add to the project's dev
  dependency group.

---

## Configuring a Tool

A tool's settings live in the highest-precedence place it can actually be
driven from:

1. **`pyproject.toml`**, under `[tool.<name>]`, if the tool reads its
   settings from there at all (e.g. `[tool.ruff]`, `[tool.pytest]`).
2. Otherwise, **its own dedicated `ConfigFile`**, if it doesn't read from
   `pyproject.toml` but has a rich enough format to warrant one (e.g.
   `zensical.toml` for `zensical`).
3. Otherwise, **CLI flags**, passed via the hook's `args` in `prek.toml`, for
   a tool that's really just a hook with no config-file convention of its
   own (e.g. `check-merge-conflict`).

Whichever of these is primary, if it can't reach the [strictest, most
best-practice](philosophy.md) setting on its own, supplement it with the
other. The same goes in reverse — reach for a config file instead of
(or in addition to) flags whenever it can express something the CLI can't.

Whenever a CLI flag is the right channel, write it in its long form (`--flag`
or `--flag=value`) for clarity.

---

## Overriding an Existing Tool

Run `pyrig mk subcls`, search for the tool class you want to change, and select
it. A correctly placed subclass skeleton is generated for you. If you already
know the module and class, skip the prompt with `pyrig mk subcls <module>
<class>`. Override whichever methods need changing — the rest of the behavior
is inherited.

See the [plugin example](plugins.md#example) for a full walkthrough of
overriding a tool from scratch.

---

## Using a Tool

Every `Tool` subclass is a `DependencySubclass`, so use `.I` to get a cached
instance of the leaf subclass (respecting any downstream override):

```python
# uv sync
PackageManager.I.install_dependencies_args().run()
# git commit --message="my commit message"
VersionController.I.commit_with_msg_args(msg="my commit message").run()
```

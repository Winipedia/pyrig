# Architecture Overview

pyrig is organized into two layers: a **generic `core/` layer** of reusable Python
utilities and a **domain-specific `rig/` layer** that builds on `core/` to implement
all scaffolding logic.

```text
src/pyrig/
├── core/               # Generic, project-agnostic utilities
│   └── introspection/  # Runtime inspection of modules, classes, packages, deps
└── rig/                # pyrig domain logic
    ├── cli/            # Entry point + subcommand registration
    ├── configs/        # Declarative config file generators
    ├── tools/          # CLI tool wrappers (git, uv, pytest, ruff …)
    ├── tests/          # Mirror test framework + pytest fixtures
    ├── resources/      # Static resource files bundled with the package
    └── utils/          # Rig-layer helpers (paths, versions, GitHub API)
```

---

## Plugin System — `DependencySubclass`

The foundation of pyrig's extensibility is `DependencySubclass`, an abstract base
class that provides **zero-registration cross-package subclass discovery**.

When `ConfigFile.subclasses()` (or `Tool.subclasses()`, etc.) is called, it:

1. Builds a directed graph of all installed packages rooted at `pyrig` using
   `importlib.metadata`.
2. For every package in that dependent set it locates the equivalent sub-package
   (e.g. `myproject.rig.configs` mirrors `pyrig.rig.configs`).
3. Imports every module in that sub-package and collects all leaf subclasses
(discarding intermediate parent classes).

This means any installed package that depends on `pyrig` automatically contributes
its `ConfigFile` and `Tool` subclasses — no entry-point
declaration or explicit registration needed.

```text
pyrig
 └── installed dependent A
      └── installed dependent B   ← B's rig/configs/** is searched automatically
```

`dependency_package()` is abstract: every subsystem base (`Tool`,
`ConfigFile`, ...) must implement it to declare its own sub-package of
`pyrig.rig`. `DependencySubclass` implements it to return `pyrig.rig`
itself, so that discovery run directly from the base — as `pyrig mk subcls`
does — spans the whole rig layer; subclasses can but should not not defer to that
value via `super()`, they always should define their own sub-package.
The root dependency is inferred automatically from the root package of
`dependency_package()`, so no separate `base_dependency` hook is needed. `Tool`
and `ConfigFile` implement
`dependency_package` with a more specific sub-package, so that only relevant
modules are imported and searched for further subclasses. This is just for discovery
efficiency and speed — the system would work even if all subclasses were defined
directly under `pyrig.rig`. However, it is recommended to follow the established
structure to be specific and avoid ambiguity.

The `.L` classproperty returns the cached **leaf subclass** — the single
outermost override across all dependencies (returns the class type, which may
be abstract or concrete). `.I` returns a cached instance of that leaf class.
These two shortcuts are used throughout the codebase for all usages of
subclasses of `DependencySubclass` to allow downstream projects to override
any part of the system by simply defining a new subclass in the right place. :

```python
PackageManager.I.install_dependencies_args().run()
MirrorTestConfigFile.L.validate_all_subclasses()
```

---

## Config Files — `ConfigFile`

`ConfigFile` is the central abstraction for **declarative, idempotent file
management**. A subclass declares:

- `parent_path()` — where the file lives
- `stem()` / `extension()` — the filename
- `_configs()` — the minimum required content (a dict or list)
- `_load()` / `_dump()` — format-specific I/O

Do not override the public methods:

- `configs()` — public cached version of `_configs()`
- `load()` — public cached version of `_load()`
- `dump()` — public version of `_dump()` that clears the cache of `load()`

`validate()` then enforces the invariant:

```text
file missing?           → create it, write required content
file present but incorrect? → merge missing keys/lines, write
file correct?           → no-op
```

User-added content is always preserved; only absent required content is enforced.
This also means that content that you change manually without overriding the right
`ConfigFile` subclass is overwritten if it changes one of the content defined
in `_configs()`, only additions like additional keys in a dict or items in a
list are preserved.

A class hierarchy of format-specific bases builds on top of `ConfigFile`:

```text
ConfigFile
 ├── DictConfigFile
 │    └── TOMLConfigFile       → pyproject.toml, prek.toml …
 ├── YAMLConfigFile
 │    └── YMLConfigFile
 │         └── YMLDictConfigFile    → GitHub Actions workflows
 ├── JSONConfigFile
 │    └── JSONListConfigFile   → branch-protection.json
 └── ListConfigFile
      └── StringConfigFile
           └── MarkdownConfigFile  → README.md, CONTRIBUTING.md …
```

---

## Tools — `Tool` and `Args`

Every external tool is wrapped in a `Tool` subclass. A `Tool` exposes methods
that return `Args` objects. `Args` is an immutable
`tuple[str, ...]` subclass with `.run()` and `.run_cached()` that run the command
via `subprocess`. This allows tools to be used in a declarative, composable way:

```python
class PackageManager(Tool):
    def install_dependencies_args(self) -> Args:
        return self.args("sync")

PackageManager.I.install_dependencies_args().run()
# → subprocess: uv sync
```

Any usages of tools by pyrig works through these `Tool` subclasses, so
downstream projects can override any command or method that provides information
about the tool by overriding the relevant method in the relevant `Tool` subclass.

---

## Mirror Tests — `MirrorTestConfigFile`

`MirrorTestConfigFile` is a `ConfigFile` subclass that treats test files as
configuration: `_configs()` returns the complete expected test file content
(existing tests merged with new stubs) and `_load()` reads the existing test file.
`validate()` appends only the missing stubs, never touching existing implementations.

At test-run time a session-scoped autouse fixture (`all_modules_tested`) enforces
that every source module has a corresponding fully-mirrored test file, failing the
session if any are absent or have missing test coverage. Combined with
`all_config_files_correct` (which checks all version-controlled `ConfigFile`
subclasses), the test suite acts as a **continuous conformance check** for the whole
project structure.

---

## CLI Dispatch

The single entry point `pyrig.rig.cli.main:main` is shared by pyrig and every
downstream project. On startup it:

1. Derives the calling package name from `sys.argv[0]` (the console-script path).
2. Imports `<package>.rig.cli.subcommands` and registers all its functions as Typer
   commands — these are project-specific commands.
3. Starts with `pyrig.rig.cli.shared_subcommands` itself, then walks the full
   dependency chain of every package that depends on `pyrig`, importing
   `<package>.rig.cli.shared_subcommands` from each, and registers those functions
   as shared commands available in every project.

This means `pyrig`'s shared `version` command is available in every
downstream project without any explicit registration because it is defined in
`pyrig.rig.cli.shared_subcommands`. Any project can define its own commands in
`<package>.rig.cli.subcommands` and they will be available in that project
without any explicit registration.
A project can also define its own shared commands in `<package>.rig.cli.shared_subcommands`
and they will be available in every pyrig-based project that depends on it
(directly or transitively).

---

## CI/CD Pipeline

The three generated GitHub Actions workflows are chained via `workflow_run` triggers:

```text
Health Check ──► Release ──► Deploy
```

Each workflow is a `WorkflowConfigFile` subclass (`YMLDictConfigFile`) that
assembles the YAML structure from composable building-block methods.
The generated YAML is checked into the repository and kept in sync by `pyrig sync`.

## How to subclass and override

To subclass a `DependencySubclass` like
`ConfigFile` or `Tool` it must be defined under the same package path as the
base class from the package root, meaning a subclass defined in a module under
`some_pyrig_project.rig.configs.some_module` must be defined under the same package
respectively as defined in the method `dependency_package()` of the base class,
which is `pyrig.rig.configs` for `ConfigFile`.
So your override must be defined a module like: `my_project.rig.configs.my_config_file.py`.
As can be seen the initial part that is the project's name is the only part that
can be different, the rest of the path must be the same as the base class's
definition package. Each module under that path is searched for subclasses and
they are registered as plugins, so in this case what the name of the final module
is doesn't matter as long as it is under the correct path, so it could be
`my_project.rig.configs.my_config_file.py` or `my_project.rig.configs.some_folder.my_other_config_file.py`.

Now this sounds all a bit complicated and can get difficult to understand, especially
if you then need to look up what config files you need to override to change a
specific part of the system.

To make this process easier there is the `pyrig mk subcls` CLI command that opens
a fuzzy search interface in the terminal where you can search for any class
that you want to override and after you select it will generate a skeleton of
the subclass for you in the correct path with the correct imports and everything,
so you can just fill in the logic that you want to change without worrying about
where to define it and how to import it and all that.

## Usage Recommendations

Our suggestion is that you use pyrig only once to create your own personal
package, so that you can customize it once with all behaviour you want for your
projects, and after that you can simply use your package to start new projects
by running:

```bash
uv init my-new-project
cd my-new-project
uv add my-pyrig-package
uv run my-pyrig-package init
```

All your customizations to pyrig will be in your package and you can keep
improving and customizing it as much as you want, and all your projects that
depend on it will automatically get all the benefits of your customizations
without you needing to make customizations in each of your projects.

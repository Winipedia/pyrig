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
    ├── builders/       # Artifact builders (executables, archives)
    ├── tools/          # CLI tool wrappers (git, uv, pytest, ruff …)
    ├── tests/          # Mirror test framework + pytest fixtures
    └── utils/          # Rig-layer helpers (paths, versions, GitHub API)
```

---

## Plugin System — `DependencySubclass`

The foundation of pyrig's extensibility is `DependencySubclass`, an abstract base
class that provides **zero-registration cross-package subclass discovery**.

When `ConfigFile.subclasses()` (or `Tool.subclasses()`, etc.) is called, it:

1. Builds a directed graph of all installed packages rooted at `pyrig` using
   `importlib.metadata`.
2. For every package in that ancestor set it locates the equivalent sub-package
   (e.g. `myproject.rig.configs` mirrors `pyrig.rig.configs`).
3. Imports every module in that sub-package and collects all non-abstract subclasses.

This means any installed package that depends on `pyrig` automatically contributes
its `ConfigFile`, `Tool`, and `BuilderConfigFile` subclasses — no entry-point
declaration or explicit registration needed.

```text
pyrig
 └── installed dependent A
      └── installed dependent B   ← B's rig/configs/** is searched automatically
```

The `RigDependencySubclass` intermediate base pre-configures the two required hooks
(`definition_package → pyrig.rig`, `base_dependency → pyrig`) so that concrete
subsystem classes (`Tool`, `ConfigFile`, `BuilderConfigFile`) inherit discovery
for free. Further BaseSubclasses like `Tool` and `ConfigFile` override
`definition_package` to a more specific sub-package, so that only relevant
modules are imported and searched for further subclasses. This is just for
efficiency — the system would work even if all subclasses were defined
directly under `pyrig.rig`.

The `.L` (used for abstract final leafs) classproperty returns the cached
**leaf subclass** — the single outermost override across all dependencies.
`.I` (used for concrete final leafs) returns a cached instance of that leaf.
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
file missing?  → create it, merge required content, write
file present but incomplete? → merge missing keys/lines, write
file correct?  → no-op
```

User-added content is always preserved; only absent required content is enforced.
This also means that content that you change manually without overriding the right
`ConfigFile` subclass is overwritten if it chnages one of the content defined
in `_configs()`, only additions like additional keys in a dict or items in a
list are preserved.

A class hierarchy of format-specific bases builds on top of `ConfigFile`:

```text
ConfigFile
 ├── DictConfigFile
 │    ├── TomlConfigFile       → pyproject.toml, prek.toml …
 │    ├── DictYmlConfigFile    → GitHub Actions workflows
 │    └── DictJsonConfigFile   → branch-protection.json
 └── ListConfigFile
      ├── StringConfigFile
      │    └── MarkdownConfigFile  → README.md, CONTRIBUTING.md …
      └── BuilderConfigFile        → artifact builders (repurposes the interface)
```

---

## Tools — `Tool` and `Args`

Every external tool is wrapped in a `Tool` subclass. A `Tool` exposes methods
that return `Args` objects. `Args` is an immutable
`tuple[str]` subclass with `.run()` and `.run_cached()` that run the command
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
configuration: `_configs()` returns the expected list of test stubs and `_load()`
reads the existing test file. `validate()` appends only the missing stubs, never
touching existing implementations.

At test-run time a session-scoped autouse fixture (`all_modules_tested`) enforces
that every source module has a corresponding test file, failing the session if any
are absent. Combined with `all_config_files_correct` (which checks all other
`ConfigFile` subclasses), the test suite acts as a **continuous conformance check**
for the whole project structure.

---

## CLI Dispatch

The single entry point `pyrig.rig.cli.cli:main` is shared by pyrig and every
downstream project. On startup it:

1. Derives the calling package name from `sys.argv[0]` (the console-script path).
2. Imports `<package>.rig.cli.subcommands` and registers all its functions as Typer
   commands — these are project-specific commands.
3. Walks the full dependency chain from `pyrig` to the calling package, importing
   `<package>.rig.cli.shared_subcommands` from each, and registers those functions
   as shared commands available in every project.

This means `pyrig`'s shared `version` command is available in every
downstream project without any explicit registration because it is defined in
`pyrig.rig.cli.shared_subcommands`. Any project can define its own commands in
`<package>.rig.cli.subcommands` and they will be available in that project
without any explicit registration.
A project can also define its own shared commands in `<package>.rig.cli.shared_subcommands`
and they will be available in every project downstream of it, not including
upstream dependencies like `pyrig` itself.

---

## CI/CD Pipeline

The four generated GitHub Actions workflows are chained via `workflow_run` triggers:

```text
Health Check ──► Build ──► Release ──► Deploy
```

Each workflow is a `WorkflowConfigFile` subclass (`DictYmlConfigFile`) that
assembles the YAML structure from composable building-block methods (`job()`,
`step_run_tests()`, `steps_core_installed_setup()`, etc.). The generated YAML is
checked into the repository and kept in sync by `pyrig mkroot`.

## How to subclass and override

To subclass a `DependencySubclass` (or `RigDependencySubclass` specifically) like
`ConfigFile` or `Tool` it must be defined under the same package path as the
base class from the package root, meaning a subclass defined in a module under
`some_pyrig_project.rig.configs.some_mdoule` must be defined under the same package
respectively as defined in the method `definition_package()` of the base class,
which is `pyrig.rig.configs` for `ConfigFile`.
So your ovveride must be defined a module like: `my_project.rig.configs.my_config_file.py`.
As can be seen the initial part that is the project's name is the only part that
can be different, the rest of the path must be the same as the base class's
definition package. Each module under that path is searched for subclasses and
they are registered as plugins, so in this case what the name of the final module
is doesn't matter as long as it is under the correct path, so it could be
`my_project.rig.configs.my_config_file.py` or `my_project.rig.configs.some_folder.my_other_config_file.py`.

Now this sounds all a bit complicated and can get difficult to understand, especially
if you then need to look up what config files you need to override to change a
specific part of the system.

To make this process easier there is the `pyrig subcls` CLI command that opens
a fuzzy search interafce in the terminal where you can search for any class
that you want to override and after you select it will generate a skeleton of
the subclass for you in the correct path with the correct imports and everything,
so you can just fill in the logic that you want to change without worrying about
where to define it and how to import it and all that.

Together with the [CodeWiki](https://codewiki.google/github.com/winipedia/pyrig)
where you can ask the AI about the codebase and get explanations about how
everything works and where to look to change specific parts of the system,
this makes it very easy to understand how to customize pyrig for your project
and what parts of the system you need to override to change specific behaviors.

## Usage Recommendations

Our suggestions is that you use pyrig only once to create your own personal
package and publish it to PyPI, so that you can customize it once with all
behaviour you want for your projects, and after that you can simply use your
package to start new projects by running:

```bash
uv init my-new-project
cd my-new-project
uv add my-pyrig-package
uv run pyrig init
```

All your customizations to pyrig will be in your package and you can keep
improving and customizing it as much as you want, and all your projects that
depend on it will automatically get all the benefits of your customizations
without you needing to make customizations in each of your projects.

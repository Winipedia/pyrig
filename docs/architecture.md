# Architecture

pyrig is organized into two layers:

```text
src/pyrig/
├── core/          # Generic, reusable Python utilities
│   └── introspection/
└── rig/           # pyrig domain logic
    ├── cli/       # CLI commands
    ├── configs/   # Config file generators
    ├── tools/     # External tool wrappers
    ├── tests/     # Mirror test framework
    └── resources/ # Bundled static files
```

---

## pyrig vs. pyrig-runtime as Dependencies

At the core of pyrig is pyrig-runtime, the runtime dependency that pyrig
itself, and every project scaffolded or managed with pyrig, depends on.

- **For pyrig**, pyrig-runtime enables both the plugin/discovery system
  (described below) and the CLI, built with Typer and exposed to the command
  line via the standard packaging entry-point mechanism.
- **For a project built with pyrig**, pyrig-runtime only enables that
  project's own CLI, and can be removed at the cost of that CLI — every
  other part of the project is otherwise completely independent of
  pyrig-runtime.
- **pyrig itself** is a development tool and is therefore only ever added to
  a project as a development dependency, never as a runtime dependency. You
  add it yourself with `uv add pyrig --dev` before running `pyrig init` to
  scaffold the initial project. `pyrig rm pyrig` removes it and its footprint
  entirely — it does not remove pyrig-runtime, which isn't a dev dependency —
  and everything pyrig already generated keeps working standalone afterward.

This split is also why pyrig can't be installed once, globally, the way a
templating tool like Cookiecutter can (e.g. via `uv tool install`): discovery
(see below) works by building a directed graph of the packages installed in
the *current* Python environment and finding which ones depend on
pyrig-runtime, so pyrig has to be installed alongside a project to discover
it — an isolated global install would never find that project's code at all.

---

## Extensibility — `DependencySubclass`

All major pyrig classes (`ConfigFile`, `Tool`, etc.) inherit from
`DependencySubclass`, which is defined and documented in
[pyrig-runtime](https://Winipedia.github.io/pyrig-runtime).

In short: any installed package that depends on pyrig can override any of its
classes simply by subclassing them in the right place — no registration needed.
Run `pyrig mk subcls` to generate a correctly placed subclass skeleton for any
pyrig class.

---

## Config Files — `ConfigFile`

`ConfigFile` is the abstraction for **declarative, idempotent file management**.
A subclass declares what a file should contain; `validate()` enforces it:

```text
file missing?      → create with required content
file incorrect?    → merge in missing content, preserve user additions
file correct?      → no-op
```

Format-specific bases handle serialization:

```text
ConfigFile
 ├── DictConfigFile → TOMLConfigFile (pyproject.toml, prek.toml …)
 ├── YAMLConfigFile → YMLConfigFile → YMLDictConfigFile (GitHub Actions workflows)
 └── ListConfigFile → StringConfigFile → MarkdownConfigFile (README.md …)
```

---

## Tools — `Tool` and `Args`

Every external tool (uv, git, pytest, ruff, …) is wrapped in a `Tool` subclass.
Methods return `Args` — an immutable `tuple[str, ...]` that can execute itself:

```python
PackageManager.I.install_dependencies_args().run()  # → uv sync
```

Because every tool interaction goes through a `Tool` subclass, any command or
behavior can be overridden downstream without touching pyrig itself.

---

## Mirror Tests — `MirrorTestConfigFile`

`MirrorTestConfigFile` is a `ConfigFile` that treats test files as managed
configuration. It inspects every source module and ensures a corresponding test
stub exists for every function and method. `validate()` only appends missing
stubs — existing test code is never touched.

Conformance is enforced by the `pyrig sync` pre-commit hook, which runs before
every commit and fails if any test stubs are missing or out of date.

---

## Usage Recommendation

The recommended way to use pyrig is to create your own personal package that
extends it once with all the customizations you want, and then use that package
as the base for all your projects:

```bash
uv init my-new-project --python 3.12
cd my-new-project
uv add my-pyrig-package --dev
uv run pyrig init
```

All your projects that depend on your package automatically inherit your
customizations without any per-project configuration.

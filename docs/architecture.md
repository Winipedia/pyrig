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
 ├── YMLDictConfigFile (GitHub Actions workflows)
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
behaviour can be overridden downstream without touching pyrig itself.

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

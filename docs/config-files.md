# Config Files

Pyrig uses a declarative, idempotent system for managing all configuration
files in a project. Rather than templating files once at project creation,
this system continuously owns the *required* structure of every managed file
and keeps it up to date throughout the life of the project.

---

## Core Concept

The central idea is that every configuration file in a pyrig-managed project
has an associated `ConfigFile` subclass. That class declares the minimum
required content for the file via `_configs()`. The system then enforces that
this content is always present on disk — creating files that are missing,
merging in values that have been removed, and leaving alone any content the
user has added beyond what is required.

This makes the system **non-destructive by default**: user customizations are
preserved as long as they do not conflict with the required structure.

---

## The `ConfigFile` Abstract Base Class

All managed files inherit from `ConfigFile`, which is parameterized over
either a `dict` or a `list` as the configuration data type
(`ConfigDict` or `ConfigList`). Subclasses declare the file by implementing
the abstract members:

| Member | Purpose |
|--------|---------|
| `parent_path()` | Directory where the file lives |
| `stem()` | Filename without extension |
| `extension()` | Extension without the leading dot |
| `_configs()` | The minimum required structure |
| `_load()` | Parse the file from disk |
| `_dump(configs)` | Write configuration to disk |

Optional overrides tune behavior:

- **`priority()`** — Controls validation order. Higher values are validated
earlier. Uses `Priority` constants: `DEFAULT` (0), `LOW` (10), `MEDIUM` (20),
`HIGH` (30) or just any float or int.
- **`version_control_ignored()`** — Marks files that should not be tracked by
git (defaults to `False`).

### The Validation Lifecycle

Calling `validate()` on a config file follows this sequence:

1. If the file does not exist, create it (including any missing parent directories),
then write `configs()` as the initial content.
2. If the file is already correct — meaning it already contains all required
keys and values — return immediately.
3. Merge `configs()` into the current file content, filling any missing keys
while leaving all existing content intact, then write the result.
4. If the file is still not correct after merging, raise a `RuntimeError`.

**Correctness** is evaluated by `is_correct()`, which checks whether `configs()`
is a recursive subset of `load()`. For dict configs this means every required
key must be present with the correct value; for list configs every required
item must be present.

### Caching

`configs()` and `load()` are cached class-level results. `dump()` is a
cache-invalidating wrapper: it clears the `load()` cache after writing,
so that subsequent loads always see the current state.

---

### Other Base Classes

`ConfigFile` is the core base class, but there are many base classes
build on top of it that provide additional shared functionality for specific types
of config files that already implement some of the abstract members.
Every final concrete file class inherits from one of these bases.

Some examples:

- `TomlConfigFile` — for config files in TOML format.
- `MarkdownConfigFile` — for Markdown files
- `YamlConfigFile` — for YAML files
- `PythonConfigFile` — for Python files

If you need more specific information check out the [CodeWiki](https://codewiki.google/github.com/winipedia/pyrig)
for AI-generated documentation about pyrig's codebase, where you can also ask
questions and get code explanations from the AI.

## Subclass Discovery, Validation & Customization

The `pyrig.rig.configs` package is the **discovery root** for all config files.
`ConfigFile.dependency_package()` returns this module, and `ConfigFile.validate_all_subclasses()`
— called by `pyrig mkroot` — discovers every concrete subclass defined inside
the package and in dependent packages, sorts by priority (higher first), and
validates each one in order.

Projects that use pyrig can also define their own config files by subclassing `ConfigFile`
or overriding existing config file classes. The system will automatically
discover and validate these subclasses as well, so custom project-specific
config files can be added without any additional configuration or setup.

To subclass an existing config file, simply run `pyrig subcls`. This will
open a fuzzy search prompt listing all `RigDependencySubclass` leaf subclasses
found in pyrig and its dependents. Simply search for the class name or the file
path to find the class you want to subclass, and select it. This will generate
a file with a subclass of the selected class where you can add or override any
configuration you want. The new subclass will automatically be discovered and
used by the system when `pyrig mkroot` is run.

If you want to create a new config file from scratch, simply create a new
subclass of `ConfigFile` or one of its base classes anywhere under the same
`dependency_package()`, and it will be automatically discovered and validated
as well.

If you want to exclude a file from validation, simply override `validate()`
to do nothing, then delete the file and you will see that the system will not
recreate it since validation is effectively disabled.

# Config Files

Every managed file in a pyrig project is backed by a `ConfigFile` subclass that
declares what the file must contain. `pyrig sync` validates all of them —
creating missing files, merging in absent required content, and leaving
everything else untouched.

---

## Implementing a New Config File

Subclass one of the format-specific bases and implement the required members:

| Member | Purpose |
|--------|---------|
| `parent_path()` | Directory where the file lives |
| `stem()` | Filename without extension |
| `extension()` | Extension without the leading dot |
| `_configs()` | Minimum required content (`dict` or `list`) |
| `_load()` | Parse the file from disk |
| `_dump(configs)` | Write configuration to disk |

Format-specific bases already implement `_load()` and `_dump()`
and other methods for you and possibly define other abstract members to implement.
Some examples are:

- `TOMLConfigFile` — TOML files
- `YMLDictConfigFile` — YAML files
- `MarkdownConfigFile` — Markdown files
- `PythonConfigFile` — Python source files

Place the class anywhere under `<your_package>.rig.configs` and it will be
discovered and validated automatically by `pyrig sync` — no registration needed.

### Optional Overrides

- **`priority()`** — Validation order. Higher values run first. Use
  `Priority.increase()` / `Priority.decrease()` relative to another file's
  priority, or return any `int` or `float`.
- **`version_control_ignored()`** — Set to `True` for files that should not be
  committed (e.g. `.env`). These are also validated by `pyrig mk local`.

---

## Overriding an Existing Config File

Run `pyrig mk subcls`, search for the class you want to change, and select it.
A correctly placed subclass skeleton is generated for you. Override whichever
methods need changing — the rest of the behaviour is inherited.

---

## Disabling Validation for a File

Override `validate()` to do nothing. The file will no longer be created or
updated by `pyrig sync`.

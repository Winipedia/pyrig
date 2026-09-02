# Config Files

Every managed file in a pyrig project is backed by a `ConfigFile` subclass that
declares what the file must contain. `pyrig sync` validates all of them —
creating missing files, merging in absent required content, and leaving
everything else untouched.

---

## How Merging Works

`validate()` decides what to do with three checks:

- **Missing file** — created and dumped with `_configs()` verbatim.
- **`is_correct()`** — `True` if every key/item declared by `_configs()` is
  already present in the file on disk, recursively. Extra keys, extra list
  items, or whole extra sections you've added are ignored by this check and
  never make a file "incorrect" on their own.
- **Otherwise** — `_configs()` is deep-merged into whatever the file already
  contains, and the merged result is written back.

The merge itself follows a few rules:

- **Dicts** — for each key `_configs()` requires, if it's missing on disk it's
  inserted at the position `_configs()` declares it; if the key already
  exists, the value on disk is kept and merging recurses into it, so nested
  keys you've added survive too. A required key you've hand-edited to a
  *different* value doesn't count as "already there" (the values differ), so
  it's treated as missing and reset back to what `_configs()` declares.
- **Lists** — items are matched by content, not position, so reordering an
  existing list doesn't cause spurious changes. A required item without a
  match is inserted; everything else already in the list — duplicates and
  items pyrig doesn't require included — is left as is.
- **Everything else** (strings, numbers, …) — compared with plain equality.

At its simplest, for a plain list of lines: if a file's current content is
`["line 1", "line 2", "line 3"]` but its declared content is
`["line 1", "line 2", "line 4"]`, pyrig merges the two into
`["line 1", "line 2", "line 4", "line 3"]` — declared content is always
present, `"line 3"` is kept because it's already there, and nothing is ever
removed or overridden.

### Example

Say a fictional `ExampleConfigFile` declares this as `_configs()`:

```json
{
  "version": 2,
  "tags": ["stable"]
}
```

`example.json`, before `pyrig sync`:

```json
{
  "version": 1,
  "tags": ["beta"],
  "owner": "me"
}
```

`example.json`, after `pyrig sync`:

```json
{
  "version": 2,
  "tags": ["beta", "stable"],
  "owner": "me"
}
```

- `"owner"` isn't part of the required structure, so it survives untouched.
- `"version"` is required, so the hand-edited `1` is reset back to `2`.
- `"tags"` is a required list: `"beta"` wasn't required, so it's left alone;
  `"stable"` is required and wasn't already present, so it gets added.

In short: anything you add on top of the required structure is permanent,
pyrig never removes it. The required structure itself is enforced — if you
change one of the values pyrig declares as required, `pyrig sync` puts it
back on the next run. To change a value pyrig manages, override the
`ConfigFile` subclass instead of hand-editing the file (see below).

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
  committed (e.g. `.scratch.py`). These are also validated by `pyrig sync`.
- **`removable()`** — Set to `False` for files that must survive `pyrig init`'s
  cleanup of existing config files (e.g. `pyproject.toml`). Defaults to `True`.

---

## Overriding an Existing Config File

Run `pyrig mk subcls`, search for the class you want to change, and select it.
A correctly placed subclass skeleton is generated for you. Override whichever
methods need changing — the rest of the behavior is inherited.

See the [plugin example](plugins.md#example) for a full walkthrough of
overriding a config file from scratch.

---

## Disabling Validation for a File

Override `validate()` to do nothing. The file will no longer be created or
updated by `pyrig sync`.

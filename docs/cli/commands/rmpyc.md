# rmpyc

Remove all **\_\_pycache\_\_** directories and their contents from the project.

## Usage

```bash
uv run pyrig rmpyc

# With verbose output
uv run pyrig -v rmpyc
```

## What It Does

The `rmpyc` command recursively searches the project for Python
``__pycache__`` directories and deletes them along with their contents.
This helps free disk space and avoids stale compiled files interfering with
development or tests.

The command targets the repository's `tests` package and the project's
main package (the package name is determined from the current working
directory / `pyproject.toml`). It only removes existing ``__pycache__``
directories and is safe to run multiple times.

## Behavior

- **Recursively deletes** any ``__pycache__`` directories found under the
  tests package and the project's package.
- **Idempotent**: running it again has no effect if there are no
  ``__pycache__`` directories present.
- **Permanent deletion**: files are removed with no recycle bin.

## When to Use

Use `rmpyc` when you need to ensure that compiled Python bytecode is
removed across the repository, for example when debugging import or
test-cache issues, or before packaging a clean source distribution.

## Notes

- This command deletes files from disk. Be cautious when running it in
  directories with important build artifacts that are not tracked elsewhere.
- Typical CI workflows do not need this command, but it can be useful for
  local cleanup.

## Related

- [Subcommands](../subcommands.md) - How `rmpyc` is exposed as a subcommand

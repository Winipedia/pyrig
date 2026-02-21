# scratch

Execute the project's `.scratch` file for temporary, ad-hoc code.

## Usage

```bash
uv run pyrig scratch

# Execute with verbose output
uv run pyrig -v scratch
```

## What It Does

The `scratch` command locates the `.scratch` file at the project root and
executes it as a Python script in a clean namespace. The `.scratch` file is
intended for short-lived, experimental code, debugging, or one-off scripts
that don't belong in the main source tree.

When executed, `scratch` uses `DotScratchConfigFile` to resolve the path and
runs the file using Python's `runpy.run_path()` to avoid polluting the current
module namespace.

## Behavior

- **Runs the `.scratch` script** if present
- **Raises** the same exceptions that the script would raise (not caught)
- **Idempotent** in the sense that running multiple times has no side effects
  from the documentation tooling perspective

## When to Use

Use `scratch` when you need to run small experiments, reproduce a quick bug,
or execute temporary scripts related to the project without adding them to the
main codebase.

## Notes

- The `.scratch` file is typically not tracked by version control.
- Keep `.scratch` small and temporary; consider moving useful code into the
  source package for long-term use.

## Related

- [Subcommands](../subcommands.md) - How to define project-specific commands

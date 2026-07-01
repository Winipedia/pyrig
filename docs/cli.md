# CLI

Every project built with pyrig gets a working CLI out of the box. The underlying
CLI system — command discovery, the `CLI` class, shared commands, and the entry
point — is provided by [pyrig-runtime](https://Winipedia.github.io/pyrig-runtime)
and documented there.

---

## Your Project's CLI

After `pyrig init`, your project already has a working CLI entry point wired up
in `pyproject.toml` and a `version` command inherited from pyrig-runtime:

```bash
uv run my-project --help
uv run my-project version   # prints: my-project 1.0.0
```

---

## Adding Commands

Run `pyrig mk cmd <name>` to scaffold a new command stub in your project's
`src/<project_name>/rig/cli/subcommands.py`. The function is wired up
automatically — no registration needed.

```bash
uv run pyrig mk cmd my-command
```

To add a **shared command** — one that will be available in every pyrig-runtime-based
project in the same environment where your package is installed — pass `--shared`:

```bash
uv run pyrig mk cmd my-command --shared
```

Shared commands are added to `src/<project_name>/rig/cli/shared_subcommands.py`.
At runtime, the CLI scans all installed packages that depend on pyrig-runtime
and registers their shared commands. So a shared command from your package is
available in every pyrig-runtime-based project in the environment, not just
projects that explicitly depend on your package. The `version` command is a good
example of this: it is defined in pyrig-runtime's own `shared_subcommands`
and is therefore available in every project built on pyrig-runtime.

---

## pyrig's Own Commands

pyrig registers its own commands the same way. They are available whenever
pyrig is installed as a dependency:

| Command | Description |
|---------|-------------|
| `pyrig init` | Full project initialization |
| `pyrig sync` | Synchronize all managed project files |
| `pyrig mk cmd <name>` | Scaffold a new CLI command stub |
| `pyrig mk cmd <name> --shared` | Scaffold a shared CLI command stub |
| `pyrig mk subcls` | Interactively scaffold a subclass of any pyrig class |
| `pyrig mk local` | Create or update version-control-ignored config files |

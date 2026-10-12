# CLI

Every project built with pyrig gets a working CLI out of the box. The underlying
CLI system — command discovery, the `CLI` class, and the entry
point — is provided by [pyrig-runtime](https://Winipedia.github.io/pyrig-runtime)
and documented there.

---

## Your Project's CLI

After `pyrig init`, your project already has a working CLI entry point wired up
in `pyproject.toml` and a `--version` option provided by pyrig-runtime:

```bash
uv run my-project --help
uv run my-project --version   # prints: 0.1.0
```

---

## Adding Commands

Run `pyrig mk cmd <name>` to scaffold a new command stub in your project's
`src/<project_name>/rig/cli/subcommands.py`. The function is wired up
automatically — no registration needed.

```bash
uv run pyrig mk cmd my-command
```

At runtime, the CLI scans that module and registers every function defined in
it as a command of your project's CLI.

---

## pyrig's Own Commands

pyrig registers its own commands the same way. They are available whenever
pyrig is installed as a dependency:

| Command | Description |
|---------|-------------|
| `pyrig init` | Full project initialization |
| `pyrig sync` | Synchronize all managed project files |
| `pyrig scratch` | Run the project's `.scratch.py` file |
| `pyrig rm pyc` | Remove all `__pycache__` directories from the project |
| `pyrig rm pyrig` | Remove pyrig and its footprint from the project entirely |
| `pyrig mk cmd <name>` | Scaffold a new CLI command stub |
| `pyrig mk inits` | Create all missing `__init__.py` files |
| `pyrig mk subcls` | Interactively scaffold a subclass of any pyrig class |
| `pyrig mk subcls <module> <class>` | Scaffold a subclass without prompting |

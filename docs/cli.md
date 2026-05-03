# CLI System

pyrig provides a **fully inheritable, automatically extensible CLI** that every
project built on pyrig gets for free. The system is built on
[Typer](https://typer.tiangolo.com) but adds a dynamic command-discovery layer on
top, so projects never need to touch pyrig's source code to gain or override CLI
commands.

---

## How the CLI is Inherited

When a project declares `pyrig` as a dependency it gets a working CLI entry point
automatically. The only thing required is registering a console-script in
`pyproject.toml` that points to the same `main` function pyrig uses.
This is also handled automatically by pyrig via its PyprojectConfigFile
and `pyrig mkroot`:

```toml
[project.scripts]
my-project = "pyrig.rig.cli.cli:main"
```

From that point on, `uv run my-project <command>` delegates to pyrig's entry
point, which discovers and registers the right commands for the calling project
automatically at runtime.

---

## The Typer App

A `typer.Typer` instance (`app`) is defined in `pyrig.rig.cli.cli`.
It is fully configured and working from the start and registers
every function defined in `my_project.rig.cli.subcommands` as a command.
The same applies to every `my_project.rig.cli.shared_subcommands`

---

## Command Discovery

When the CLI is invoked, pyrig discovers every function defined in
`my_project.rig.cli.subcommands` and `my_project.rig.cli.shared_subcommands`
and registers them as CLI commands. This means that to add a new command, simply
define a new function in one of those modules, and it will be automatically
available as a CLI command the next time the CLI is run.
Simply run `pyrig mkcmd <command-name>` to append a new command function skeleton
to `my_project.rig.cli.subcommands` (creating the file if it does not exist).

`my_project.rig.cli.shared_subcommands` is a bit special: it is intended for
commands that should be shared across multiple projects. If a project defines a
function in `shared_subcommands`, that command will also be available in any
other project that has your project as a dependency.
An example of this is pyrig's own `version` command, which is defined in `pyrig.rig.cli.shared_subcommands`
so that it is available in every project that uses pyrig.
So your project has already one command from the start that you can run:

```bash
uv run my-project version
# This will print smth like: my-project version 1.2.3
```

But if you run pyrig's `version` command directly,
you get the version of pyrig instead:

```bash
uv run pyrig version
# This will print smth like: pyrig version 12.3.4
```

To add a shared command, simply run `pyrig mkcmd <command-name> --shared` and
it will append the command skeleton to `shared_subcommands` (creating the
file if it does not exist).

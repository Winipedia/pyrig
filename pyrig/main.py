"""Main function template for pyrig projects.

This module serves as a template that gets copied to consuming projects by
the MainConfigFile configuration generator. It provides an empty main()
function that can be customized with application-specific logic.

The main() function is automatically discovered and registered as a CLI
command by pyrig's command discovery system in pyrig.dev.cli.cli.

Note:
    This is a template file. The actual pyrig CLI entry point is
    pyrig.dev.cli.cli:main, not this file.
"""


def main() -> None:
    """Main function template for the project.

    This function is automatically registered as a CLI command when the
    project's CLI is invoked. Customize this function with your application's
    main logic.

    The function is discovered and registered by pyrig.dev.cli.cli.add_subcommands()
    which dynamically loads this module and registers the main() function as
    a Typer command.

    Example:
        After customization, run via CLI::

            $ uv run myproject main
            $ uv run myproject main --help
    """


if __name__ == "__main__":
    main()

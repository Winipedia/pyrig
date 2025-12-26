"""Shared CLI commands available across all pyrig-based projects.

This module defines CLI commands that are automatically available in all
projects that depend on pyrig. These commands are discovered through pyrig's
multi-package architecture and registered in each project's CLI with
project-specific behavior.

The shared commands system enables creating commands that work consistently
across an ecosystem of related packages while adapting to each project's
context. For example, the `version` command displays the version of whichever
project is being run, not pyrig's version.

Discovery Mechanism:
    The shared commands discovery process (implemented in
    `pyrig.dev.cli.cli.add_shared_subcommands`) works as follows:

    1. **Extract package name**: Gets the current package name from `sys.argv[0]`
    2. **Build dependency chain**: Finds all packages from pyrig to the current
       package (e.g., [pyrig, intermediate_pkg, current_pkg])
    3. **Find shared_subcommands modules**: For each package in the chain, looks
       for a `dev.cli.shared_subcommands` module
    4. **Extract functions**: Gets all public functions from each module
    5. **Register commands**: Registers each function as a Typer command

    This enables intermediate packages to define their own shared commands that
    are automatically available in all dependent projects.

Commands:
    - `version`: Display the project's version from package metadata

Extensibility:
    To add shared commands to your own pyrig-based package, create a
    `<package>/dev/cli/shared_subcommands.py` module with public functions.
    These will be automatically discovered and added to all projects that
    depend on your package.

Example:
    Running the version command in different projects::

        $ uv run pyrig version
        pyrig version 3.1.5

        $ uv run myproject version
        myproject version 1.2.3

    Creating custom shared commands::

        # mypackage/dev/cli/shared_subcommands.py
        from pyrig.src.cli import get_project_name_from_argv
        import typer

        def status() -> None:
            '''Display project status.'''
            project_name = get_project_name_from_argv()
            typer.echo(f"Status for {project_name}: OK")

    Then in any project that depends on mypackage::

        $ uv run dependent_project status
        Status for dependent_project: OK

Note:
    - Functions are registered in dependency order (pyrig first, then dependent
      packages)
    - If multiple packages define the same command name, the last one registered
      (from the most dependent package) takes precedence
    - Use context utilities like `get_project_name_from_argv()` to make commands
      adapt to the calling project

See Also:
    pyrig.dev.cli.cli.add_shared_subcommands: Discovery and registration mechanism
    pyrig.src.cli.get_project_name_from_argv: Extract project name from argv
    pyrig.dev.cli.subcommands: Project-specific commands
"""

from importlib.metadata import version as get_version

import typer

from pyrig.src.cli import get_project_name_from_argv


def version() -> None:
    """Display the current project's version from package metadata.

    Retrieves and displays the version of the project being run, not pyrig's
    version. The version is read from the installed package metadata via
    `importlib.metadata.version()`, which gets the version from the project's
    `pyproject.toml` or package metadata.

    The project name is automatically determined from `sys.argv[0]`, enabling
    this command to work correctly in any pyrig-based project without
    modification.

    Output Format:
        The command outputs a single line in the format::

            <project_name> version <version_number>

    Example:
        Running in different projects::

            $ uv run pyrig version
            pyrig version 3.1.5

            $ uv run myproject version
            myproject version 1.2.3

    Note:
        - The project name is extracted from `sys.argv[0]` (e.g., "myproject"
          from "uv run myproject version")
        - The version is retrieved from the installed package metadata, so the
          package must be installed (even in editable mode) for this to work
        - If the package is not installed, `importlib.metadata.version()` will
          raise `PackageNotFoundError`

    See Also:
        pyrig.src.cli.get_project_name_from_argv: Project name extraction
        importlib.metadata.version: Version retrieval from package metadata
    """
    project_name = get_project_name_from_argv()
    typer.echo(f"{project_name} version {get_version(project_name)}")

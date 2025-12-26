"""Tool wrappers for project management and development workflows.

This package provides Python wrappers for common development tools used in
pyrig projects. Each tool is represented by a class that constructs command-line
arguments in a type-safe, composable way.

The package follows a consistent pattern:
    - Each tool is a subclass of `Tool` (from `base.base`)
    - Tools provide methods that return `Args` objects (command argument tuples)
    - `Args` objects can be executed directly via their `.run()` method
    - All command construction is centralized and testable

Supported Tools:
    - **PackageManager** (uv): Package installation, dependency management, building
    - **VersionController** (git): Version control operations
    - **PreCommitter** (pre-commit): Code quality hooks
    - **ProjectTester** (pytest): Test execution
    - **ContainerEngine** (podman): Container building
    - **Pyrigger** (pyrig): Pyrig CLI commands

Example:
    >>> from pyrig.src.management.package_manager import PackageManager
    >>> from pyrig.src.management.version_controller import VersionController
    >>>
    >>> # Construct command arguments
    >>> install_args = PackageManager.get_install_dependencies_args()
    >>> print(install_args)
    ('uv', 'sync')
    >>>
    >>> # Execute the command
    >>> install_args.run()
    CompletedProcess(...)
    >>>
    >>> # Chain operations
    >>> commit_args = VersionController.get_commit_no_verify_args("Update deps")
    >>> commit_args.run()

See Also:
    pyrig.src.management.base.base: Base classes (Tool, Args)
    pyrig.src.os.os.run_subprocess: Subprocess execution wrapper
"""

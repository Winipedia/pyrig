"""Tool wrappers for project management and development workflows.

Provides Python wrappers for common development tools.
Each tool constructs command-line arguments in a type-safe, composable way via `Args`
objects that can be executed directly.

Pattern:
    - Each tool is a subclass of `Tool` (from `base.base`)
    - Tools provide methods returning `Args` objects (command argument tuples)
    - `Args` objects execute via `.run()` method

Supported Tools:
    PackageManager (uv): Package installation, dependency management, building
    VersionController (git): Version control operations
    PreCommitter (pre-commit): Code quality hooks
    ProjectTester (pytest): Test execution
    ContainerEngine (podman): Container building
    Pyrigger (pyrig): Pyrig CLI commands
"""

"""Operating system utilities for subprocess execution and command discovery.

This package provides utilities for interacting with the operating system,
including subprocess execution with enhanced error logging and command path
discovery. These utilities are used throughout pyrig for running external
tools like git, uv, pytest, and pre-commit.

The main features:
    - **Subprocess execution**: Enhanced `subprocess.run()` with detailed error logging
    - **Command discovery**: Find executable paths with optional error raising

Example:
    >>> from pyrig.src.os.os import run_subprocess, which_with_raise
    >>> # Find command path
    >>> uv_path = which_with_raise("uv")
    >>> print(uv_path)
    '/usr/bin/uv'
    >>>
    >>> # Run command with error logging
    >>> result = run_subprocess(["uv", "sync"])
    >>> result.returncode
    0

See Also:
    pyrig.src.management: Tool wrappers that use these utilities
    pyrig.src.management.base.base.Args: Uses run_subprocess for execution
"""

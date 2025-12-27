"""Operating system utilities for subprocess execution and command discovery.

Provides utilities for subprocess execution with enhanced error logging and command
path discovery. Used throughout pyrig for running external tools (git, uv, pytest).

Features:
    - Subprocess execution: Enhanced `subprocess.run()` with detailed error logging
    - Command discovery: Find executable paths with optional error raising
"""

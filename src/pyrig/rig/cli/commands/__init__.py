"""CLI command implementation functions.

Contains the core implementation logic for pyrig's CLI commands. Each module
implements a single command and is intentionally separated from the CLI
interface layer in `pyrig.rig.cli.subcommands`. This separation allows each
command to be tested and called programmatically without any CLI framework
overhead, and allows the CLI layer to use local (lazy) imports, preventing
import errors in environments where optional dev dependencies are not installed.
"""

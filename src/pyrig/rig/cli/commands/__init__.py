"""Backend implementations for every pyrig CLI command.

Each module implements exactly one command as a plain callable, decoupled from
the CLI registration layer. This separation lets the registration layer import
commands lazily, loading each module only when its command is invoked.
"""

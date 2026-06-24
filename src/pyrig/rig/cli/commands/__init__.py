"""Backend implementations for every pyrig CLI command.

Each module implements exactly one command as a plain callable, decoupled from
the CLI registration layer. This separation keeps commands testable without any
CLI framework and lets the registration layer use lazy imports, so optional
dev-only dependencies do not need to be installed in every environment.
"""

"""Wrappers for external CLI tools used in development and CI workflows.

Each tool is a `Tool` subclass whose methods return `Args` objects that
encapsulate command-line arguments for type-safe construction and execution.
"""

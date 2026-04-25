"""Package for defining custom artifact builders.

Add `BuilderConfigFile` subclasses here to create project-specific build artifacts.
Each subclass must implement `create_artifacts()` to define its build logic.
Non-abstract subclasses are automatically discovered and executed when running
`pyrig build`.
"""

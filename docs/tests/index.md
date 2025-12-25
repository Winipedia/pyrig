# Testing Documentation

pyrig provides a comprehensive testing framework that automatically enforces structure, shares fixtures across packages, and validates project health.

## Documentation Pages

### [Test Structure](structure.md)

Learn about pyrig's mirrored test structure convention:

- Naming conventions for tests, modules, and classes
- Directory structure requirements
- Automatic test skeleton generation
- Coverage requirements

### [Fixture Sharing](fixtures.md)

Understand how fixtures are shared across packages:

- Multi-package plugin architecture
- Automatic fixture discovery
- Dependency graph integration
- Factory fixtures for testing

### [Autouse Fixtures](autouse.md)

Explore fixtures that run automatically in all packages:

- Session-level validation fixtures
- Module and class-level test coverage fixtures
- Project health checks
- Dependency verification

## Quick Overview

pyrig's testing system ensures:

- **90% minimum code coverage** across all packages
- **Strict structure mirroring** between source and tests
- **Automatic fixture sharing** across package dependencies
- **Self-healing tests** with automatic skeleton generation
- **Parallel test generation** - Test skeletons are created concurrently for improved performance
- **Project health validation** on every test run

Run tests:

```bash
uv run pytest                    # Run all tests
uv run pytest --cov-report=html  # Generate HTML coverage report
uv run pyrig mktests             # Generate missing test skeletons
```

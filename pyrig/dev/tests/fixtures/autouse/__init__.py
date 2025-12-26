"""Scope-specific autouse pytest fixtures for automatic test validation.

This package contains autouse fixtures organized by pytest scope. Autouse
fixtures run automatically for all tests at their respective scope levels
without requiring explicit fixture requests in test signatures.

The fixtures in this package enforce test coverage, project structure, and
code quality standards automatically. They are organized by scope to optimize
performance and ensure validations run at the appropriate level.

Modules:
    session: Session-scoped autouse fixtures that run once per test session.
        These validate project-wide concerns like:
        - No unstaged git changes (CI only)
        - Project structure correctness
        - No namespace packages
        - Source package naming conventions
        - All modules have test modules
        - Dependencies are up to date
        - Pre-commit hooks installed
        - Source code runs without dev dependencies
        - Source code doesn't import dev code
        - Project management tools installed

    module: Module-scoped autouse fixtures that run once per test module.
        These validate module-level concerns like:
        - All functions and classes in module have corresponding tests

    class_: Class-scoped autouse fixtures that run once per test class.
        These validate class-level concerns like:
        - All methods in class have corresponding test methods

Scope Hierarchy:
    Pytest scopes run in this order (from broadest to narrowest):
    1. **session**: Once per entire test session (all tests)
    2. **package**: Once per package (not used in pyrig)
    3. **module**: Once per test module file
    4. **class**: Once per test class
    5. **function**: Once per test function (not used for autouse in pyrig)

    Autouse fixtures at each scope run automatically before any tests at that
    scope level. This ensures validations happen at the right granularity.

Autouse Mechanism:
    Fixtures in this package use the `@autouse_*_fixture` decorators from
    `pyrig.dev.utils.testing` or pytest's `@pytest.fixture(autouse=True)`.
    This makes them run automatically without being explicitly requested in
    test function signatures.

    Example of autouse fixture::

        @autouse_session_fixture
        def validate_project_structure():
            '''Runs once per session automatically.'''
            assert project_is_valid()

    This fixture runs automatically for every test session without needing to
    add it to any test function signature.

Performance Considerations:
    - **Session fixtures**: Run once per session, so they can be expensive
      (e.g., checking dependencies, running builds)
    - **Module fixtures**: Run once per module, so they should be reasonably fast
      (e.g., checking test coverage for that module)
    - **Class fixtures**: Run once per class, so they should be very fast
      (e.g., checking method coverage for that class)

See Also:
    pyrig.dev.utils.testing: Autouse fixture decorators
    pyrig.dev.tests.fixtures.assertions: Non-autouse assertion fixtures
    pytest.fixture: Pytest's fixture mechanism
"""

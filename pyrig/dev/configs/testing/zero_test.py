"""Configuration for the test_zero.py placeholder test.

This module provides the ZeroTestConfigFile class for creating a minimal
placeholder test file that ensures pytest runs successfully even when no
other tests exist.

The generated test:
    - Contains an empty test_zero() function
    - Ensures pytest doesn't fail with "no tests collected"
    - Triggers execution of pyrig's scoped fixtures
    - Provides a starting point for test development

This is useful for new projects where tests haven't been written yet but
CI/CD pipelines expect pytest to run successfully.

See Also:
    pyrig.dev.tests.fixtures
        Scoped fixtures that get executed when this test runs
"""

from pyrig.dev.configs.base.py_tests import PythonTestsConfigFile


class ZeroTestConfigFile(PythonTestsConfigFile):
    '''Configuration file manager for test_zero.py.

    Generates a test_zero.py file with an empty test function that ensures
    pytest runs successfully even when no other tests have been written.

    The test file:
        - Contains a single empty test_zero() function
        - Prevents "no tests collected" errors
        - Triggers execution of pyrig's scoped fixtures (function, class,
          module, package, session)
        - Provides a placeholder until real tests are written

    Benefits:
        - CI/CD pipelines don't fail on new projects
        - Scoped fixtures are tested even without real tests
        - Provides a template for writing actual tests
        - Easy to remove once real tests are added

    Examples:
        Generate test_zero.py::

            from pyrig.dev.configs.testing.zero_test import ZeroTestConfigFile

            # Creates tests/test_zero.py
            ZeroTestConfigFile()

        The generated test looks like::

            """Contains an empty test."""

            def test_zero() -> None:
                """Empty test.

                Exists so that when no tests are written yet the base
                fixtures are executed.
                """

    See Also:
        pyrig.dev.tests.fixtures
            Scoped fixtures executed when this test runs
        pyrig.dev.configs.testing.main_test.MainTestConfigFile
            Another basic test file for CLI testing
    '''

    @classmethod
    def get_filename(cls) -> str:
        """Get the test filename with reversed prefix.

        Reverses the class name parts to convert "zero_test" to "test_zero"
        following pytest naming conventions.

        Returns:
            str: The string "test_zero" (extension .py is added by parent class).

        Examples:
            >>> ZeroTestConfigFile.get_filename()
            'test_zero'
        """
        filename = super().get_filename()
        return "_".join(reversed(filename.split("_")))

    @classmethod
    def get_content_str(cls) -> str:
        '''Get the placeholder test content.

        Generates Python code with an empty test_zero() function that serves
        as a placeholder to ensure pytest runs successfully.

        Returns:
            str: Python code with an empty test function.

        Examples:
            Returns::

                """Contains an empty test."""

                def test_zero() -> None:
                    """Empty test.

                    Exists so that when no tests are written yet the base
                    fixtures are executed.
                    """
        '''
        return '''"""Contains an empty test."""


def test_zero() -> None:
    """Empty test.

    Exists so that when no tests are written yet the base fixtures are executed.
    """
'''

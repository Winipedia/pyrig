"""Configuration for test_zero.py placeholder test.

Generates test_zero.py with empty test_zero() function to ensure pytest runs
successfully even when no other tests exist. Triggers pyrig's scoped fixtures.

See Also:
    pyrig.dev.tests.fixtures
"""

from pyrig.dev.configs.base.py_tests import PythonTestsConfigFile


class ZeroTestConfigFile(PythonTestsConfigFile):
    '''Manages test_zero.py.

    Generates test_zero.py with empty test_zero() function to ensure pytest runs
    successfully even when no other tests exist. Triggers pyrig's scoped fixtures.

    Examples:
        Generate test_zero.py::

            ZeroTestConfigFile()

        Generated test::

            """Contains an empty test."""

            def test_zero() -> None:
                """Empty test.

                Exists so that when no tests are written yet the base
                fixtures are executed.
                """

    See Also:
        pyrig.dev.tests.fixtures
        pyrig.dev.configs.testing.main_test.MainTestConfigFile
    '''

    @classmethod
    def get_filename(cls) -> str:
        """Get the test filename with reversed prefix.

        Returns:
            str: "test_zero" (extension .py added by parent class).

        Note:
            Reverses class name parts to convert "zero_test" to "test_zero".
        """
        filename = super().get_filename()
        return "_".join(reversed(filename.split("_")))

    @classmethod
    def get_lines(cls) -> list[str]:
        """Get the placeholder test content.

        Returns:
            List of lines with empty test function.
        """
        return [
            '"""Contains an empty test."""',
            "",
            "",
            "def test_zero() -> None:",
            '    """Empty test.',
            "",
            "    Exists so that when no tests are written yet the base fixtures are executed.",  # noqa: E501
            '    """',
            "",
        ]

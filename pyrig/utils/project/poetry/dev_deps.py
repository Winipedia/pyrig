"""Contains a dict with the dev dependencies.

For poetry when pyrig is a dependency.
pyrigwill add these automatically to the pyproject.toml file.
pyrig's PyprojectConfigFile will auto dump the config here so it can access it
when being a dependency in another project.
"""

DEV_DEPENDENCIES: dict[str, str | dict[str, str]] = {
    "ruff": "*",
    "pre-commit": "*",
    "mypy": "*",
    "pytest": "*",
    "bandit": "*",
    "types-setuptools": "*",
    "types-tqdm": "*",
    "types-defusedxml": "*",
    "types-pyyaml": "*",
    "pytest-mock": "*",
    "types-networkx": "*",
    "types-pyinstaller": "*",
    "pyinstaller": {"version": "*", "python": "<3.15"},
}

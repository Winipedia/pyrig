"""Main entrypoint for the project."""

import pyrig


def main() -> None:
    """Main entrypoint for the project."""
    msg = f"""Add your projects entrypoint code to this function.
This function is automatically added to your cli by {pyrig.__name__}.
You can call it with
`poetry run your-pkg-name main`
or via
`python -m your-pkg-name`.
"""
    raise NotImplementedError(msg)


if __name__ == "__main__":
    main()

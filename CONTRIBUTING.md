# Contributing

Thanks for considering a contribution to pyrig! Following
these guidelines respects the time of the people who maintain and review
this project, and helps them address your issue or pull request quickly.

> **Found a security vulnerability?**
> Please follow [SECURITY.md](SECURITY.md).

## Code of Conduct

By participating in this project, you agree to abide by its
[Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to Contribute

Contributions aren't limited to code — reporting bugs, improving
documentation, and answering questions are just as valuable. Before
opening a new issue, search [existing issues](https://github.com/Winipedia/pyrig/issues)
to avoid duplicates.

- **Bugs** — describe what you expected, what happened instead, and the
  steps to reproduce it.
- **Features** — describe the problem before proposing a solution, and
  open an issue before starting a large pull request so the approach can
  be discussed first.
- **Questions** — open an issue if nothing else already answers it.

## Development Workflow

1. Fork and clone the repository.
2. Install the dependencies: `uv sync`
3. Install the git hooks: `uv run prek install`
4. Create a branch for your change.
5. Make your change.
6. Commit your change.
7. Push your branch and open a pull request.

## Pull Requests

- Reference related issues in the description.
- Keep changes focused and atomic.
- Update documentation.
- All checks in [CI](https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml) must pass before merge.

# Philosophy

pyrig provides **as modern as possible**, **as best practice as possible**,
**as strict as possible**, **as complete as possible**, and **as simple as possible**,
defaults and automations for everything any Python project **should** have.

This includes but is not limited to:

- Standardized project structure and file layout
(src/my_project, tests/, docs/, etc.)
- Standardized configuration files and formats
(pyproject.toml, .gitignore, README.md, etc.)
- Standardized development and maintenance tooling
(prek, ruff, pytest, etc...)
- Standardized CI/CD pipelines and repository protection
(GitHub Actions, branch protection, etc.)

---

The five principles above are listed in priority order: when two of them
would pull in different directions, the earlier one wins. Best practice and
strictness reinforce each other far more often than they conflict; on the
rare occasion a specific best practice would leave real issues uncaught,
strictness takes priority instead.

Every principle below governs `Tool` and `ConfigFile` equally. A `Tool`
wraps an external CLI tool; a `ConfigFile` is a generated file, and it often
exists to configure a `Tool` — `pyproject.toml` for `ruff`, `zensical.toml`
for `zensical` — but plenty don't correspond to any tool at all: `README.md`,
`LICENSE`, `CODEOWNERS`, and issue templates have no tool behind them, yet
the same five principles still decide their content, and how their
`ConfigFile` subclass is implemented, exactly as they would for one that
does.

## As Modern as Possible

Always prefer the newest, most actively maintained option over the
historically popular one — for a tool, for a config file's own format
(whether or not a tool reads it), and for how pyrig implements either
internally. Once a genuinely better option exists, pyrig should move to it,
even if the older one still works fine. For example: `ruff` instead of
`black`, `ty` instead of `mypy`, `zensical` instead of `mkdocs`, `ryl`
instead of a generic YAML formatter — and, just as much, a more modern
format (e.g. TOML over YAML) for any config file that has a choice.

## As Best Practice as Possible

Every tool and every config file should be set up the way its own community
considers correct, not however happens to work. This covers indentation
style, file layout, naming, and anything else an authoritative style guide or
established convention would call out — and it applies equally to tools, to
config files in their own right (whether or not a specific tool reads them),
and to how pyrig implements both.

## As Strict as Possible

Once a tool is chosen and set up to best practice, push it to catch as much
as it possibly can: enable every optional check it offers, use its most
inclusive severity level, and never silently skip something it's capable of
looking at. A config file gets the same treatment — its content should be as
complete and unambiguous as its format allows. But never override a setting
that is already correct by default, whether it's a tool's CLI flag or a
value inside a config file — only override a default to make it *more*
strict or more correct, never to restate the same value it already has.

## As Complete as Possible

Everything pyrig sets up should be fully configured and ready to use
immediately, with nothing left for the user to finish by hand. This is also
the line between pyrig's core and its plugins: core covers everything
*every* project should have, fully configured; anything only *some* projects
need — building an executable, publishing to a package index — lives in a
plugin instead (`pyrig-executables`, `pyrig-pypi`), so core never ends up
half-configuring something not every project wants.

## As Simple as Possible

Reach all of the above with the fewest moving parts. Never restate a value
that is already correct — for example, `ty` already treats warnings as
errors by default, so pyrig doesn't set that explicitly; doing so would only
repeat something already true, not change anything. The same rule applies
everywhere: one owner for a shared value, no configuration toggles, no
duplicated source of truth.

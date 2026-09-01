# Comparisons

See below how pyrig compares to other tools.

Legend: ✅ yes · ➖ partial (see cell for how) · ❌ no · — not applicable
(no such mechanism exists at all)

<!-- rumdl-disable MD013 -->

| Feature | pyrig | Cookiecutter | Copier | cruft | PyScaffold | Nitpick | projen |
|---|---|---|---|---|---|---|---|
| Keeps itself in sync automatically — no manifest or template file to maintain, nothing to remember to re-run | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Never overwrites or removes what you've already changed | ➖ resets values it declares as required if you hand-edit them | — | ➖ 3-way merge; unresolved conflicts need manual fixing | ➖ diff-merge with `skip` globs; leftovers become `.rej` files | ➖ untouched files only; can't remove a feature once added | ➖ only touches keys declared in the style file | ➖ direct edits are disallowed by design, not preserved |
| Ships linting, formatting, type checking, and tests configured out of the box | ✅ | ➖ only if the chosen template includes it | ➖ only if the chosen template includes it | ➖ inherits whatever the underlying Cookiecutter template includes | ➖ ships tox/pre-commit scaffolding, not preconfigured linters | ➖ via opt-in presets (black, flake8, isort, mypy, …) | ➖ depends on the project type and components chosen |
| Generates CI/CD pipelines | ✅ | ➖ only if the chosen template includes it | ➖ only if the chosen template includes it | ➖ inherits whatever the underlying Cookiecutter template includes | ➖ via an opt-in extension (e.g. `--cirrus`), not by default | ➖ has a GitHub Actions preset, but only enforces declared keys | ➖ for supported project types only |
| Generates GitHub repo protection rules | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Gives your project a working CLI, maintained automatically | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Generates and maintains test-file skeletons that mirror your source code | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Customized by writing code, not flags, prompts, or template edits | ✅ | ➖ hook scripts run at generation time, not ongoing | ➖ hook/migration scripts run at generation time, not ongoing | ➖ inherits Cookiecutter's hook scripts, still one-shot | ❌ | ❌ | ✅ |
| Has a plugin/extension ecosystem for adding new capabilities, not just per-project tweaks | ✅ | ➖ custom Jinja extensions only, no formal package ecosystem | ➖ custom Jinja extensions only, no formal package ecosystem | ❌ | ✅ | ❌ | ✅ |
| Takes input (prompts or flags) to customize content at generation time | ❌ | ✅ | ✅ | ✅ | ✅ | — | ❌ |
| Shows what changed as part of updating an existing project | ❌ | — | ✅ | ➖ as a git-style merge diff, not a structured 3-way summary | ❌ | ✅ | ❌ |
| Removes settings that become obsolete between versions | ❌ | — | ✅ | ➖ via diff/merge, unless the file is in the `skip` list | ❌ | ❌ | ✅ |

<!-- rumdl-enable MD013 -->

Ratings reflect each tool's built-in, documented mechanisms — a template
author using a first-class feature like a hook script or preset counts —
not a hypothetical amount of custom scripting layered on top to route
around a tool's actual limits.

For the full story behind pyrig's own "➖", see
[How Merging Works](config-files.md#how-merging-works).

For pyrig's own trade-offs, see [Drawbacks](drawbacks.md).

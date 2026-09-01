# Comparisons

See below how pyrig compares to other tools.

Legend: ✅ yes · ➖ partial, or only in some cases · ❌ no · — not
applicable (no such mechanism exists at all)

<!-- rumdl-disable MD013 -->

| Feature | pyrig | Cookiecutter | Copier | cruft | PyScaffold | Nitpick | projen |
|---|---|---|---|---|---|---|---|
| Keeps itself in sync automatically — no manifest or template file to maintain, nothing to remember to re-run | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Never overwrites or removes what you've already changed | ➖ | — | ➖ | ➖ | ➖ | ➖ | ➖ |
| Ships linting, formatting, type checking, and tests configured out of the box | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ➖ |
| Generates CI/CD pipelines | ✅ | ➖ | ➖ | ➖ | ➖ | ❌ | ➖ |
| Generates GitHub repo protection rules | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Gives your project a working CLI, maintained automatically | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Generates and maintains test-file skeletons that mirror your source code | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Customized by writing code, not flags, prompts, or template edits | ✅ | ❌ | ❌ | ❌ | ❌ | ➖ | ✅ |
| Has a plugin/extension ecosystem for adding new capabilities, not just per-project tweaks | ✅ | ➖ | ➖ | ❌ | ✅ | ❌ | ✅ |
| Takes input (prompts or flags) to customize content at generation time | ❌ | ✅ | ✅ | ✅ | ✅ | — | ❌ |
| Shows what changed as part of updating an existing project | ❌ | — | ✅ | ➖ | ❌ | ✅ | ❌ |
| Removes settings that become obsolete between versions | ❌ | — | ✅ | ➖ | ❌ | ❌ | ✅ |

<!-- rumdl-enable MD013 -->

Ratings reflect each tool's default, out-of-the-box behavior, not what a
sufficiently customized template or config could theoretically be made to do.

pyrig's own "➖" on *"Never overwrites or removes what you've already
changed"* means: anything you add on top of what pyrig requires is never
touched, but a value you hand-edit that pyrig itself declares as required
gets reset back on the next `pyrig sync`. See
[How Merging Works](config-files.md#how-merging-works) for the full
explanation and examples.

For pyrig's own trade-offs, see [Drawbacks](drawbacks.md).

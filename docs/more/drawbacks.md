# Trade-offs

pyrig makes deliberate trade-offs to provide a standardized, automated
development experience. This document explains what you sacrifice and what you
gain.

## Opinionated Tooling

**Trade-off**: pyrig chooses tools for you (uv, ruff, ty, pytest, etc.)

**What You Sacrifice**:

- Freedom to choose alternative tools (poetry, black, flake8, unittest)
- Ability to customize tool configurations extensively
- Control over when tools are updated

**What You Gain**:

- **Zero configuration time** - Start coding immediately
- **Best-in-class tools** - Carefully selected for speed and quality (ruff is
  10-100x faster than alternatives)
- **Consistent experience** - Same tools across all pyrig projects
- **Automatic updates** - Tool improvements without manual migration
- **Proven stack** - Battle-tested combinations that work well together
- **Tool evolution** - pyrig switches to better alternatives as they emerge
  (poetry → uv for package management, mypy → ty for type checking)
- **No decision fatigue** - Skip hours of research and comparison

**Bottom Line**: Sacrifice tool choice for instant, optimized setup and
continuous improvement.

**Note**: While not recommended, it is technically possible to replace any tool
by subclassing the Tool wrapper classes. pyrig uses the `.L` (leaf) property
internally, so your subclasses automatically apply everywhere. However, this
requires significant additional work as tools are interconnected with configs,
workflows, and CI/CD pipelines. See
[Replacing Tools](../management/architecture.md#replacing-tools) for details.

## Runtime Dev Folder

**Trade-off**: The `dev/` folder is included in the package at runtime

**What You Sacrifice**:

- Minimal package size increase (mostly empty folders and `__init__.py` files
  when unused)
- Perception of shipping "development code" with production

**What You Gain**:

- **Multi-package architecture** - Downstream packages can extend your
  infrastructure
- **CLI extensibility** - Other packages can add commands to your CLI
  automatically
- **Builder inheritance** - Share build processes across packages
- **Config reusability** - Extend configuration systems
- **Shared infrastructure** - Test fixtures, utilities, and patterns propagate
- **Simplified packaging** - No complex build exclusions or dual package
  structures
- **Ecosystem power** - Build interconnected package families

**Reality Check**: The `dev/` folder is extremely lightweight when unused (just
empty directories). When used, it enables powerful multi-package ecosystems.

See: [Multi-Package Architecture](../cli/architecture.md) |
[CLI Documentation](../cli/index.md)

**Bottom Line**: Sacrifice a few KB for architectural flexibility and ecosystem
benefits.

## Strict Requirements

**Trade-off**: Enforces strict standards automatically

**What You Sacrifice**:

- Ability to commit code that doesn't meet quality standards
- Freedom to skip tests or type hints
- Option to disable linting rules easily

**What You Gain**:

- **High code quality** - 90% coverage, all linting rules, strict typing
- **Catch bugs early** - Pre-commit hooks prevent issues from entering codebase
- **Consistent style** - No debates about formatting or conventions
- **Better refactoring** - Type safety makes large changes safer
- **Documentation through types** - Code is self-documenting
- **Team alignment** - Everyone follows the same standards
- **Reduced technical debt** - Quality enforced from day one

**Bottom Line**: Sacrifice flexibility for guaranteed code quality and
consistency.

## Python Version Constraint

**Trade-off**: Requires Python >=3.12

**What You Sacrifice**:

- Compatibility with Python 3.11 or earlier
- Support for older systems
- Ability to use with legacy projects

**What You Gain**:

- **Modern type hints** - PEP 695 (type parameters), PEP 698 (override
  decorator)
- **Better performance** - Python 3.12+ is significantly faster
- **Latest features** - Pattern matching, structural pattern matching, etc.
- **Future-proof** - Already using current best practices
- **Simpler code** - Modern syntax is more concise and readable

**Reality Check**: Python 3.12 was released in October 2023 and is widely
available. Python 3.13 and 3.14 are also supported.

**Bottom Line**: Sacrifice legacy compatibility for modern features and
performance.

## Learning Curve

**Trade-off**: Requires understanding pyrig's conventions

**What You Sacrifice**:

- Immediate familiarity (if coming from different frameworks)
- Ability to "just wing it" without reading docs

**What You Gain**:

- **Transferable knowledge** - Same patterns across all pyrig projects
- **Comprehensive docs** - Every feature documented with examples
- **Automatic discovery** - ConfigFiles, CLI commands, tests auto-discovered
- **Consistent patterns** - Once learned, applies everywhere
- **Less decision-making** - Clear conventions reduce cognitive load
- **Faster onboarding** - New team members learn once, apply everywhere

**Bottom Line**: Sacrifice initial learning time for long-term productivity and
consistency.

## Structured Conventions

**Trade-off**: Must follow pyrig's structure and naming conventions

**What You Sacrifice**:

- Freedom to organize files however you want
- Ability to use custom naming schemes
- Option to skip certain directories

**What You Gain**:

- **Automation** - Tools know where to find everything
- **Predictability** - Every pyrig project has the same structure
- **Faster navigation** - Know exactly where files are located
- **Tool integration** - Everything works together seamlessly
- **Reduced setup** - No configuration needed for standard structure
- **Team efficiency** - No debates about project organization

**Bottom Line**: Sacrifice organizational freedom for automation and
predictability.

## GitHub-Centric

**Trade-off**: Optimized for GitHub workflows

**What You Sacrifice**:

- Native support for GitLab, Bitbucket, etc.
- Flexibility in CI/CD platform choice

**What You Gain**:

- **Complete CI/CD** - Health check, build, release, publish workflows ready
- **Repository protection** - Automated branch protection and rulesets
- **Matrix builds** - Test across OS (Ubuntu, Windows, macOS) and Python
  versions (3.12, 3.13, 3.14)
- **Automated releases** - Version bumping, changelog, GitHub releases
- **GitHub Pages** - Documentation auto-deployed
- **Zero CI/CD config** - Workflows generated and maintained automatically

**Reality Check**: GitHub is the industry standard for open source. Workflows
can be adapted for other platforms if needed.

**Bottom Line**: Sacrifice platform flexibility for complete, automated GitHub
integration.

## Autouse Fixtures

**Trade-off**: Validation fixtures run automatically on every test session

**What You Sacrifice**:

- Slightly slower test startup (typically <1 second)
- Cannot skip validation for quick tests

**What You Gain**:

- **Continuous validation** - Project health checked automatically
- **Catch issues early** - Missing tests, namespace packages, incorrect configs
  detected immediately
- **No manual checks** - Never forget to run validation
- **Consistent quality** - Every test run ensures project integrity
- **Automatic test generation** - Missing test files created automatically
- **Zero maintenance** - Validation happens without thinking about it

**Bottom Line**: Sacrifice a fraction of a second for automatic project health
monitoring.

## Configuration Management

**Trade-off**: Config files are regenerated/validated automatically

**What You Sacrifice**:

- Complete control over config file contents
- Ability to remove pyrig-required settings

**What You Gain**:

- **Always up-to-date** - Configs stay current with pyrig updates
- **Subset validation** - Can add your own settings, pyrig won't remove them
- **Opt-out markers** - Can disable regeneration for specific files
- **No config drift** - All projects stay consistent
- **Automatic fixes** - Broken configs repaired automatically
- **Less maintenance** - Don't manually update configs across projects

**Bottom Line**: Sacrifice full config control for automatic maintenance and
consistency.

## When to Use pyrig

pyrig excels when you want:

- **Rapid project setup** - Complete structure in minutes
- **Enforced standards** - Consistent quality across projects
- **Modern tooling** - Latest Python and tool versions
- **Automation** - CI/CD, testing, building, documentation
- **Ecosystem benefits** - Shared infrastructure across packages
- **Zero configuration** - Start coding immediately
- **Best practices** - Proven patterns and tools

## When NOT to Use pyrig

Consider alternatives if you need:

- **Maximum flexibility** - Custom project structures and tooling
- **Legacy Python** - Python <3.12 support
- **Non-GitHub workflows** - GitLab CI, Jenkins, etc. as primary platform
- **Gradual adoption** - Incremental tooling changes
- **Minimal conventions** - Freedom to organize however you want

## Philosophy

pyrig's core philosophy is to provide **minimal best practices fully working
defaults for everything a project needs**. This means:

- **Complete out-of-the-box**: Every configuration, workflow, and tool is
  pre-configured and working from day one
- **Best practices by default**: Opinionated choices based on industry standards
  and modern Python development
- **Minimal configuration**: Zero setup required - sensible defaults that work
  for most projects
- **Fully functional**: Not just templates or boilerplate, but a complete,
  tested, production-ready setup

This philosophy drives pyrig's intentional trade-offs. It prioritizes:

- **Consistency** over flexibility
- **Automation** over manual control
- **Quality** over convenience
- **Standards** over customization
- **Working defaults** over endless configuration options

If these priorities align with your goals, pyrig's benefits far outweigh its
trade-offs.

## Partial Opt-Out: Use pyrig Without the Automation

You can use pyrig for initial setup and CLI framework while opting out of
automation features.

### What You Keep

**Initial Setup**:

- Complete project structure from `pyrig init`
- All tool configurations (ruff, ty, pytest, bandit, rumdl, etc.)
- Pre-commit hooks configuration
- GitHub Actions workflows
- Documentation setup

**CLI Framework**:

- Typer-based CLI system (keep `pyproject.toml` entry point)
- Command discovery mechanism (keep `dev/cli/` folder)
- Multi-package command support

### What You Disable

**Automatic Validation**:

- Remove pyrig plugin from `conftest.py`
- Autouse fixtures won't run
- No automatic config regeneration
- No automatic test generation

**Workflow Automation**:

- Remove `pyrig` commands from GitHub Actions workflows
- Remove `pyrig protect-repo` from health check
- Remove `pyrig build` from build workflow
- Workflows still run, just without pyrig automation

**Manual Config Management**:

- Never call `pyrig mkroot` manually
- Config files won't be regenerated
- You maintain configs yourself

You can also disable the cli by removing the entry point from `pyproject.toml`.
If you disable that too you can also just delete the `dev/` folder. You will
still be left with a nice initial project structure and tooling.

### How to Opt Out

**1. Remove from conftest.py**:

```python
# Remove or comment out:
# pytest_plugins = ["pyrig.dev.tests.conftest"]
```

**2. Remove from workflows**:

```yaml
# In .github/workflows/*.yaml, remove lines like:
# - run: uv run pyrig protect-repo
# - run: uv run pyrig build
```

**3. Don't call pyrig mkroot**:

```bash
# Never run:
# uv run pyrig mkroot
```

### What Happens

**pyrig becomes passive**:

- No automatic validation
- No config regeneration
- No autouse fixtures
- No workflow automation

**You still benefit from**:

- Initial project structure
- Tool configurations (you maintain them)
- CLI framework (command discovery still works)
- Pre-commit hooks (if you keep them)
- Workflows (if you keep them)

### When to Use Partial Opt-Out

This approach works well if you:

- Want the initial setup but prefer manual control
- Need to customize configs extensively
- Have existing workflows you want to keep
- Want the CLI framework without automation
- Are migrating an existing project gradually

### Limitations

**You lose**:

- Automatic config updates when pyrig evolves
- Autouse fixture validation (missing tests, namespace packages, etc.)
- Automatic test skeleton generation
- Config consistency across pyrig updates
- Workflow automation benefits

**You maintain**:

- All config files manually
- Test structure manually
- Workflow updates manually
- Pre-commit hook updates manually

### Re-enabling pyrig

You can re-enable pyrig automation at any time:

**1. Add back to conftest.py**:

```python
pytest_plugins = ["pyrig.dev.tests.conftest"]
```

**2. Add back to workflows**:

```yaml
- run: uv run pyrig protect-repo
- run: uv run pyrig build
```

**3. Run pyrig mkroot**:

```bash
uv run pyrig mkroot
```

pyrig will validate and update configs to current standards.

### Bottom Line

pyrig is flexible enough to use as a **one-time setup tool** with an optional
CLI framework, or as a **full automation system**. You choose how much
automation you want.

The partial opt-out approach gives you the best of both worlds: excellent
initial setup with the option to take full manual control afterward.

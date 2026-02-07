# Additional Information

This section contains supplementary documentation about pyrig's design decisions
and technical details.

## [Getting Started](getting-started.md)

Complete guide to setting up a new pyrig project from scratch:

- **Prerequisites**: Git, uv, Podman (optional)
- **Required Tokens**: GitHub (REPO_TOKEN), PyPI (optional), Codecov account
  (recommended), CODECOV_TOKEN (recommended)
- **Setup Steps**: Create repo, clone, uv init, add pyrig, configure .env, run
  init
- **What You Get**: Complete project structure, configs, CI/CD workflows, dev
  tools
- **Next Steps**: Start coding, make changes, release

Step-by-step instructions from zero to fully configured project.

## [Tooling](tooling.md)

Understand pyrig's opinionated tooling choices and why they were selected:

- **Package Management**: uv for fast dependency management
- **Code Quality**: ruff, ty, bandit, rumdl for comprehensive code checking
- **Testing**: pytest with 90% coverage requirement
- **Documentation**: MkDocs with Material theme and Mermaid diagrams
- **Containerization**: Podman for secure, daemonless containers
- **CI/CD**: GitHub Actions with matrix builds
- **Philosophy**: Speed, strictness, simplicity, security, automation, and
  modernity

Learn about tool evolution and how pyrig adapts to better alternatives as they
emerge.

## [Trade-offs](drawbacks.md)

Understand pyrig's philosophy and what you sacrifice and what you gain:

- **Philosophy**: Minimal best practices fully working defaults for everything a
  project needs
- **Opinionated Tooling**: Sacrifice tool choice → Gain zero-config,
  best-in-class tools
- **Runtime Dev Folder**: Sacrifice a few KB → Gain multi-package architecture
  and CLI extensibility
- **Strict Requirements**: Sacrifice flexibility → Gain guaranteed code quality
- **Python >=3.12**: Sacrifice legacy compatibility → Gain modern features and
  performance
- **Learning Curve**: Sacrifice immediate familiarity → Gain long-term
  productivity
- **Structured Conventions**: Sacrifice organizational freedom → Gain automation
  and predictability
- **GitHub-Centric**: Sacrifice platform flexibility → Gain complete automated
  CI/CD
- **Autouse Fixtures**: Sacrifice <1s startup → Gain automatic project health
  monitoring
- **Config Management**: Sacrifice full control → Gain automatic maintenance

Balanced assessment of pyrig's intentional philosophy, trade-offs and what you
get in return.

## [Example Usage: Microservices Ecosystem](example-usage.md)

Real-world example of using pyrig to build and maintain a standardized
microservices ecosystem:

- **Scenario**: Organization with multiple Python microservices needing
  consistent standards
- **Architecture**: Base package extending pyrig, multiple services depending on
  it
- **Custom Configs**: Add shared logging, monitoring, security
  configurations
- **Override Configs**: Customize MkDocs theme, pyproject.toml settings across
  all services
- **Auto-Synchronization**: Update base package → all services heal themselves
  via autouse fixtures
- **Discovery Mechanism**: How dependency graph + ConfigFile discovery enables
  multi-package architecture
- **Propagation Flow**: Step-by-step breakdown of how changes flow through the
  ecosystem
- **Real Benefits**: Security audits, rebranding, new services - all solved in
  minutes

Complete walkthrough showing pyrig's power in production environments with
microservices.

# Drawbacks

pyrig can be really frustrating if you do not think the trade offs are
worth it. Pyrig will force or at least encourage you to do all the things
you do not want to do, but definitely **should** be doing, like using proper
typing, writing tests, and then some more stuff.

pyrig is deliberately opinionated, strict and complete with its setup.
However pyrig is 100% customizable through its plugin architecture,
so if you do not like the defaults, you can always write your own plugin to
override them via subclassing. That process is simple and complicated at the
same time and if you do not want to do that, you can run `pyrig rm pyrig` to
remove pyrig from your project entirely, as described below.

---

## Known Drawbacks

- **No opt-outs.** Every concern gets exactly one opinionated default. If you
  disagree with a specific choice, your only options are overriding the
  responsible class (`pyrig mk subcls`) or leaving pyrig entirely — there is
  no config flag to just turn something off.
- **Assumes GitHub as the remote.** Repository settings and branch protection
  are pushed directly to GitHub via `gh api`, and the release/deploy pipeline
  is GitHub Actions. Anything else needs its own substitution plugin.
- **Needs an elevated access token.** The default `GITHUB_TOKEN` can't change
  repository settings or enable Pages, so the deploy workflow needs a
  personal access token with broader permissions, stored as a `REPO_TOKEN`
  secret.
- **Mandatory signed commits and linear history.** The generated branch
  protection ruleset requires signed commits, blocks force-pushes, and
  enforces a linear history. Contributors need commit signing already set up.
- **Fast-moving tool choices.** "As modern as possible" means newer, less
  battle-tested tools get adopted quickly (`ty`, `zensical`, `tombi`, `ryl`,
  `rumdl`, …). You get the newest and best option, but also more exposure to rough
  edges than a conservative, best-practice-only setup would have.
- **All or nothing.** Because there are no toggles, adopting pyrig for one
  concern means adopting all of them.

---

## Removing pyrig From Your Project

Only a few things in a pyrig-managed project actually **require** pyrig to
be installed. Everything else it generated is plain, standalone output that
keeps working fine without pyrig and can simply be left in place. Running
`pyrig rm pyrig` takes care of all of it in one step.
This command will remove anything that uses pyrig itself, like the
`pyrig sync` pre-commit hook in the `prek.toml` file.
After you ran the command, you can now do whatever you like with your project
and just enjoy the complete setup pyrig has given you and customize it manually.

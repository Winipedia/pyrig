#!/usr/bin/env bash
set -euo pipefail

repo="Winipedia/pyrig"

repository() {
  jq '.repository' .github/settings.json | gh api "repos/${repo}" --method=PATCH --input=-
}

rulesets() {
  local endpoint="repos/${repo}/rulesets"
  jq --compact-output '.rulesets[]' .github/settings.json | while read -r ruleset; do
    id=$(gh api "${endpoint}" \
      | jq --raw-output --argjson r "${ruleset}" '.[] | select(.name==$r.name) | .id')
    if [[ -z ${id} ]]; then method="POST"; else method="PUT"; fi
    url="${endpoint}${id:+/${id}}"
    gh api "${url}" --method="${method}" --input=- <<<"${ruleset}"
  done
}

vulnerability_reporting() {
  gh api "repos/${repo}/private-vulnerability-reporting" --method=PUT
}

release_immutability() {
  gh api "repos/${repo}/immutable-releases" --method=PUT
}

fork_pr_contributor_approval() {
  jq '.fork_pr_contributor_approval' .github/settings.json | gh api "repos/${repo}/actions/permissions/fork-pr-contributor-approval" --method=PUT --input=-
}

topics() {
  jq '{names: .topics}' .github/settings.json | gh api "repos/${repo}/topics" --method=PUT --input=-
}

for step in $(declare -F | awk '{print $3}'); do
  "${step}"
done

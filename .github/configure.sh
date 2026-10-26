#!/usr/bin/env bash
set -euo pipefail

: "${GH_TOKEN:?}"
: "${GITHUB_REPOSITORY:?}"

dependency_alerts() {
  gh api "repos/${GITHUB_REPOSITORY}/vulnerability-alerts" --method=PUT
}

dependency_security_updates() {
  gh api "repos/${GITHUB_REPOSITORY}/automated-security-fixes" --method=PUT
}

fork_pr_contributor_approval() {
  jq '.fork_pr_contributor_approval' .github/settings.json | gh api "repos/${GITHUB_REPOSITORY}/actions/permissions/fork-pr-contributor-approval" --method=PUT --input=-
}

release_immutability() {
  gh api "repos/${GITHUB_REPOSITORY}/immutable-releases" --method=PUT
}

repository() {
  jq '.repository' .github/settings.json | gh api "repos/${GITHUB_REPOSITORY}" --method=PATCH --input=-
}

rulesets() {
  local endpoint="repos/${GITHUB_REPOSITORY}/rulesets"
  jq --compact-output '.rulesets[]' .github/settings.json | while read -r ruleset; do
    id=$(gh api "${endpoint}" \
      | jq --raw-output --argjson r "${ruleset}" '.[] | select(.name==$r.name) | .id')
    if [[ -z ${id} ]]; then method="POST"; else method="PUT"; fi
    url="${endpoint}${id:+/${id}}"
    gh api "${url}" --method="${method}" --input=- <<<"${ruleset}"
  done
}

topics() {
  jq '{names: .topics}' .github/settings.json | gh api "repos/${GITHUB_REPOSITORY}/topics" --method=PUT --input=-
}

vulnerability_reporting() {
  gh api "repos/${GITHUB_REPOSITORY}/private-vulnerability-reporting" --method=PUT
}

for step in $(declare -F | awk '{print $3}'); do
  "${step}"
done

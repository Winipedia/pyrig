repo="Winipedia/pyrig"

settings() {
  jq '.repository' .github/settings.json | gh api "repos/$repo" -X PATCH --input -
}

rulesets() {
  local endpoint="repos/$repo/rulesets"
  jq -c '.rulesets[]' .github/settings.json | while read -r ruleset; do
    id=$(gh api "$endpoint" |
      jq -r --argjson r "$ruleset" '.[] | select(.name==$r.name) | .id')
    if [ -z "$id" ]; then method="POST"; else method="PUT"; fi
    gh api "$endpoint${id:+/$id}" -X "$method" --input - <<<"$ruleset"
  done
}


"$@"
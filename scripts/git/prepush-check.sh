#!/usr/bin/env sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$repo_root"

echo "Running pre-push checks in $repo_root"

fail=0

check_pattern() {
  pattern=$1
  label=$2

  if git grep -nI -E "$pattern" -- . >/tmp/prepush-check.$$ 2>/dev/null; then
    echo
    echo "[FAIL] $label"
    cat /tmp/prepush-check.$$
    fail=1
  fi
  rm -f /tmp/prepush-check.$$
}

# Common secret classes that routinely trigger GitHub push protection.
check_pattern 'gsk_[A-Za-z0-9]+' 'Possible Groq API key'
check_pattern 'sk-[A-Za-z0-9]{20,}' 'Possible generic API key / token'
check_pattern 'AIza[0-9A-Za-z\-_]{35}' 'Possible Google API key'
check_pattern '-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----' 'Private key material'

# Notebook outputs and copied docs are common secret carriers in this repo.
if git ls-files '*.ipynb' >/tmp/prepush-ipynb.$$ 2>/dev/null && [ -s /tmp/prepush-ipynb.$$ ]; then
  while IFS= read -r notebook; do
    if grep -aEn 'gsk_[A-Za-z0-9]+|sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z\-_]{35}' "$notebook" >/tmp/prepush-notebook.$$ 2>/dev/null; then
      echo
      echo "[FAIL] Notebook output contains possible secret: $notebook"
      cat /tmp/prepush-notebook.$$
      fail=1
    fi
    rm -f /tmp/prepush-notebook.$$
  done </tmp/prepush-ipynb.$$
fi
rm -f /tmp/prepush-ipynb.$$

if [ "$fail" -ne 0 ]; then
  echo
  echo "Pre-push checks failed."
  echo "Remove or sanitize the matched content before pushing."
  exit 1
fi

echo "Pre-push checks passed."

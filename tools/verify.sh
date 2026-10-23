#!/usr/bin/env bash
# Local mirror of .github/workflows/quality.yml. Run from the repo root:
#   bash tools/verify.sh          # fast checks only
#   bash tools/verify.sh --full   # adds axe-core and Lighthouse (needs Chrome)
set -euo pipefail
cd "$(dirname "$0")/.."

FAVICON_SHA="4a95fe99473fd1711d5fd1735387e67d9abb046d5f8fbdc1bff983b24198379f"

echo "== favicon hash =="
echo "$FAVICON_SHA  favicon.png" | shasum -a 256 -c -

echo "== no deleted files vs main =="
if git rev-parse --verify main >/dev/null 2>&1; then
  if git diff --name-status main...HEAD | grep -q '^D'; then
    git diff --name-status main...HEAD | grep '^D'; exit 1
  fi
  echo "no deletions"
else
  echo "main branch not found locally, skipping"
fi

echo "== html-validate =="
(cd .tools/e2e && npx html-validate "../../**/*.html")

echo "== internal links =="
python3 .tools/check_links.py

echo "== titles and descriptions =="
python3 .tools/phase3_titles.py

echo "== JSON-LD =="
python3 .tools/validate_jsonld.py

echo "== og:image rule =="
python3 .tools/check_og_image.py

if [ "${1:-}" = "--full" ]; then
  echo "== axe-core =="
  (cd .tools/e2e && node axe-sweep.js)
  echo "== Lighthouse budgets =="
  (cd .tools/e2e && node lh-ci.js)
fi

echo "ALL CHECKS PASSED"

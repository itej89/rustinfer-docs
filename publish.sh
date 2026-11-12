#!/bin/sh
# Build the site and publish it to Codeberg Pages.
# Codeberg serves the `pages` branch of a public repository at
# https://<user>.codeberg.page/<repo>/ ; this script rebuilds out/,
# writes its contents as one commit on an orphan `pages` branch and pushes it.
set -eu
cd "$(dirname "$0")"
.venv/bin/python build.py
.venv/bin/python scripts/check_links.py
rev=$(git rev-parse --short HEAD)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
git worktree add --quiet --detach "$work"
(
	cd "$work"
	git checkout --quiet --orphan pages-build
	git rm -rfq . >/dev/null 2>&1 || true
	cp -r "$OLDPWD"/out/. .
	touch .nojekyll
	git add -A
	git -c user.name="$(git -C "$OLDPWD" config user.name)" \
	    -c user.email="$(git -C "$OLDPWD" config user.email)" \
	    commit --quiet -m "publish site built from $rev"
	git push --quiet --force origin HEAD:refs/heads/pages
)
git worktree remove --force "$work"
git branch -D -q pages-build
echo "published $rev to https://itej89.codeberg.page/rustinfer-docs/"

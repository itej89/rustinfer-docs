#!/bin/sh
# Build the site and publish it to GitHub Pages.
# GitHub Pages serves the `pages` branch of this repository (root path) at
# https://itej89.github.io/rustinfer-docs/ ; this script rebuilds out/,
# writes its contents as one commit on an orphan `pages` branch and pushes it
# to `origin` (github.com/itej89/rustinfer-docs). The `.nojekyll` file keeps
# Jekyll from skipping files whose names start with an underscore.
# Moved from Codeberg Pages on 2026-11-12 (ADR-008).
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
echo "published $rev to https://itej89.github.io/rustinfer-docs/"

#!/bin/sh
# Build and serve the site. PORT=8099 ./serve.sh to move it.
cd "$(dirname "$0")" || exit 1
[ -x .venv/bin/python ] || {
	echo "no virtualenv yet; run:"
	echo "  python3 -m venv .venv && .venv/bin/pip install markdown pygments"
	exit 1
}
exec .venv/bin/python build.py --serve

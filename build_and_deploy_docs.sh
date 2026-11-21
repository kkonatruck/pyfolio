#!/bin/bash
# Build the docs (strict: any warning fails), verify every internal
# link resolves, then deploy to GitHub Pages.
# For a local build without deploying, run `make docs` instead.
set -e

mkdocs build --clean --strict
python docs/check_links.py site
mkdocs gh-deploy

.PHONY: docs docs-serve

# Build the documentation site and verify every internal link.
# Fails on any MkDocs warning (--strict) or broken internal link.
docs:
	pip install -e ".[docs]"
	mkdocs build --strict
	python docs/check_links.py site

docs-serve:
	mkdocs serve

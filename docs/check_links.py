#!/usr/bin/env python
"""Fail if any internal link in the built site does not resolve.

Walks ``site_dir`` (default ``site/``), parses every HTML file, and
checks that each internal ``href``/``src`` target exists on disk
(anchors are checked against the target file's ``id`` attributes).
External links (``http:``, ``https:``, ``mailto:``) and pure fragments
are skipped; MkDocs itself validates Markdown-level links, this covers
the generated HTML. Exits 1 and prints every broken link if any fail.

Usage: python docs/check_links.py [site_dir]
"""
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.refs.append(attrs[key])


def main(site_dir):
    site = Path(site_dir)
    if not site.is_dir():
        print(f"check_links: {site} does not exist; run mkdocs build first")
        return 1
    pages = sorted(site.rglob("*.html"))
    parsed, ids_by_page = {}, {}
    for page in pages:
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8", errors="ignore"))
        parsed[page] = parser.refs
        ids_by_page[page] = parser.ids

    broken = []
    for page, refs in parsed.items():
        for ref in refs:
            parsed_ref = urlparse(ref)
            if parsed_ref.scheme or ref.startswith(("//", "#")):
                continue
            ref_path = unquote(parsed_ref.path)
            if ref_path.startswith("/"):
                # Site-root-absolute link (e.g. from 404.html).
                target = (site / ref_path.lstrip("/")).resolve()
            else:
                target = (page.parent / ref_path).resolve()
            if not parsed_ref.path:
                target_page = page
            elif target.is_dir():
                target_page = target / "index.html"
            else:
                target_page = target
            if not target_page.exists():
                broken.append(f"{page.relative_to(site)}: {ref}")
            elif parsed_ref.fragment and target_page.suffix == ".html" \
                    and unquote(parsed_ref.fragment) not in ids_by_page.get(
                        target_page, set()):
                broken.append(f"{page.relative_to(site)}: {ref} "
                              "(missing anchor)")

    if broken:
        print(f"check_links: {len(broken)} broken internal link(s):")
        for link in broken:
            print(f"  {link}")
        return 1
    print(f"check_links: all internal links resolve "
          f"({len(pages)} pages checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "site"))

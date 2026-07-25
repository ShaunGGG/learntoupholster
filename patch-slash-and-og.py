#!/usr/bin/env python3
"""
patch-slash-and-og.py  —  learntoupholster.com

Fixes two things found in the Ahrefs site audit:

1. /projects had no trailing slash in the nav (66 pages), in its own
   canonical, and in the sitemap. The server 308-redirects /projects to
   /projects/, so every one of those pointed at a redirect. This is the
   single cause behind "65 links to redirect", "canonical points to
   redirect" and "3XX redirect in sitemap".

2. Ten pages declared og:url as the site root instead of themselves —
   including /buy-the-book. Shares of those pages were being attributed
   to the homepage. og:url is set to match each page's own canonical.

Order matters: canonical is corrected BEFORE og:url is synced to it,
so the projects page doesn't inherit the old slashless value.

Safe to run twice.
"""

import os
import re
import sys

BASE = "https://www.learntoupholster.com"
SKIP_DIRS = {".git", "node_modules", ".wrangler", "functions", "project-sources"}


def html_files():
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in sorted(files):
            if f.endswith(".html"):
                yield os.path.join(root, f)


def main() -> int:
    if not os.path.exists("index.html"):
        print(f"✘ No index.html in {os.getcwd()} — run from ~/learntoupholster.")
        return 1

    nav_fixed = canon_fixed = og_fixed = 0

    for path in html_files():
        original = open(path, encoding="utf-8").read()
        html = original

        # --- 1a. canonical: /projects -> /projects/ (exact, not children)
        html, n = re.subn(
            r'(rel="canonical" href="' + re.escape(BASE) + r'/projects)(")',
            r"\1/\2",
            html,
        )
        canon_fixed += n

        # --- 1b. nav href="/projects" -> "/projects/"
        #     The closing quote immediately after guarantees we never touch
        #     /projects/parker-knoll-wing-chair and friends.
        html, n = re.subn(r'href="/projects"', 'href="/projects/"', html)
        nav_fixed += n

        # --- 2. og:url := this page's canonical
        c = re.search(r'rel="canonical" href="([^"]+)"', html)
        if c:
            canonical = c.group(1)
            o = re.search(r'(property="og:url" content=")([^"]+)(")', html)
            if o and o.group(2).rstrip("/") != canonical.rstrip("/"):
                html = html[: o.start(2)] + canonical + html[o.end(2):]
                og_fixed += 1

        if html != original:
            open(path, "w", encoding="utf-8").write(html)

    # --- 1c. sitemap
    sm_fixed = 0
    if os.path.exists("sitemap.xml"):
        s = open("sitemap.xml", encoding="utf-8").read()
        s2, sm_fixed = re.subn(
            r"(<loc>" + re.escape(BASE) + r"/projects)(</loc>)", r"\1/\2", s
        )
        if sm_fixed:
            open("sitemap.xml", "w", encoding="utf-8").write(s2)

    print(f"✔ nav links      /projects -> /projects/   : {nav_fixed}")
    print(f"✔ canonicals     /projects -> /projects/   : {canon_fixed}")
    print(f"✔ sitemap <loc>  /projects -> /projects/   : {sm_fixed}")
    print(f"✔ og:url synced to canonical               : {og_fixed}")
    if nav_fixed == canon_fixed == sm_fixed == og_fixed == 0:
        print("\n  Nothing to change — already patched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

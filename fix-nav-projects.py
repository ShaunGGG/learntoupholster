#!/usr/bin/env python3
"""fix-nav-projects.py — remove the duplicate 'Projects' nav item.

patch-projects-nav.py tested for the exact string '/projects">Projects</a>'.
The nav already carried '/projects/">Projects</a>' (trailing slash), so the
test missed and a second, slash-less item was inserted on every page.

This removes the slash-less duplicate wherever a trailing-slash one exists,
keeping the version that matches the canonical /projects/. Idempotent.

    python3 fix-nav-projects.py [--dry-run]
"""
import glob, re, sys

DRY = "--dry-run" in sys.argv
DUP  = '<li><a href="/projects">Projects</a></li>'
KEEP = '<li><a href="/projects/">Projects</a></li>'

fixed = single = 0
for f in sorted(glob.glob("*.html") + glob.glob("projects/*.html")):
    t = open(f, encoding="utf-8").read()
    nav = re.search(r'<ul id="site-menu".*?</ul>', t, re.S)
    if not nav:
        continue
    n = nav.group(0)
    if n.count(">Projects</a>") < 2:
        single += 1
        continue
    if DUP not in n:
        print(f"  ! {f}: two Projects items but not the expected pair — left alone")
        continue
    # drop the duplicate (and the whitespace that came with it)
    n2 = re.sub(r"\s*" + re.escape(DUP), "", n, count=1)
    if KEEP not in n2:                      # never leave the page with none
        n2 = n.replace(DUP, KEEP, 1)
        n2 = re.sub(r"\s*" + re.escape(KEEP), "", n2, count=1)
    t = t.replace(n, n2, 1)
    if not DRY:
        open(f, "w", encoding="utf-8").write(t)
    fixed += 1

print(f"{'DRY RUN — ' if DRY else ''}{fixed} page(s) de-duplicated, "
      f"{single} already had a single Projects item.")

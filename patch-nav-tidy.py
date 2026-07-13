#!/usr/bin/env python3
"""Nav tidy-up:
  1. Removes the redundant 'Search' nav item (it points to the same page as
     'Ask the book').
  2. Repoints 'Ask the book' at /search (top of page) rather than the #ask
     anchor, so the search box and the Ask box are both visible on arrival.
  3. Removes the duplicated 'Find an upholsterer' link in the footer.
Idempotent. Run from repo root:  python3 patch-nav-tidy.py"""
import glob

SEARCH_LI = '<li><a href="/search">Search</a></li>'
ASK_OLD   = '<li><a href="/search#ask">Ask the book</a></li>'
ASK_NEW   = '<li><a href="/search">Ask the book</a></li>'
FOOT_DUPE = ('<p class="foot-small"><a href="/find-an-upholsterer">Find an upholsterer</a></p>\n'
             '        <p class="foot-small"><a href="/find-an-upholsterer">Find an upholsterer</a></p>')
FOOT_ONE  = '<p class="foot-small"><a href="/find-an-upholsterer">Find an upholsterer</a></p>'

nav_n = foot_n = 0
for f in glob.glob('*.html'):
    t = open(f, encoding='utf-8').read()
    o = t

    # 1 + 2: nav
    if SEARCH_LI in t:
        # remove the Search item (and the whitespace line it sits on)
        t = t.replace('\n      ' + SEARCH_LI, '', 1)
        t = t.replace(SEARCH_LI, '', 1)          # fallback if indentation differs
    if ASK_OLD in t:
        t = t.replace(ASK_OLD, ASK_NEW, 1)

    # 3: footer duplicate
    if FOOT_DUPE in t:
        t = t.replace(FOOT_DUPE, FOOT_ONE, 1)
        foot_n += 1

    if t != o:
        open(f, 'w', encoding='utf-8').write(t)
        nav_n += 1

print(f"pages updated: {nav_n} (footer duplicate fixed on {foot_n})")

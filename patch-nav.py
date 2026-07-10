#!/usr/bin/env python3
"""Adds 'Buy the Book' and 'Use in AI' to the nav on every page, and
/buy-the-book to sitemap.xml. Idempotent — safe to run twice.
Run from the repo root:  python3 patch-nav.py"""
import glob, re

CTA = '<li><a class="nav-cta" href="/contents">Contents</a></li>'
BUY = '<li><a href="/buy-the-book">Buy the Book</a></li>'
ASK = '<li><a href="/search#ask">Ask the book</a></li>'
AI  = '<li><a href="/use-in-ai">Use in AI</a></li>'

patched = skipped = 0
for f in glob.glob('*.html'):
    t = open(f, encoding='utf-8').read()
    o = t
    if '/buy-the-book"' not in t and CTA in t:
        t = t.replace(CTA, CTA + '\n      ' + BUY, 1)
    if '/use-in-ai"' not in t and ASK in t:
        t = t.replace(ASK, ASK + '\n      ' + AI, 1)
    if t != o:
        open(f, 'w', encoding='utf-8').write(t)
        patched += 1
    else:
        skipped += 1
print(f"nav: {patched} pages patched, {skipped} unchanged")

# sitemap
try:
    s = open('sitemap.xml', encoding='utf-8').read()
    if '/buy-the-book' not in s:
        entry = ('  <url><loc>https://www.learntoupholster.com/buy-the-book</loc>'
                 '<changefreq>monthly</changefreq><priority>0.9</priority></url>\n')
        s = s.replace('</urlset>', entry + '</urlset>')
        open('sitemap.xml', 'w', encoding='utf-8').write(s)
        print("sitemap: /buy-the-book added")
    else:
        print("sitemap: already present")
except FileNotFoundError:
    print("sitemap.xml not found — skipped")

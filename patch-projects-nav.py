#!/usr/bin/env python3
"""Adds 'Projects' to the nav on every page, and keeps the raw project source
files out of Google's index. Idempotent. Run from repo root AFTER
build-projects.py:   python3 patch-projects-nav.py"""
import glob

BUY = '<li><a href="/buy-the-book">Buy the Book</a></li>'
NEW = BUY + '\n      <li><a href="/projects">Projects</a></li>'

n = 0
for f in glob.glob('*.html') + glob.glob('projects/*.html'):
    t = open(f, encoding='utf-8').read()
    if '/projects">Projects</a>' in t or BUY not in t:
        continue
    t = t.replace(BUY, NEW, 1)
    open(f, 'w', encoding='utf-8').write(t)
    n += 1
print(f"nav: Projects added to {n} pages")

# keep the raw .txt sources and unoptimised photos out of the index
try:
    r = open('robots.txt', encoding='utf-8').read()
    added = []
    for rule in ['Disallow: /project-sources/']:
        if rule not in r:
            r = r.replace('Allow: /\n', 'Allow: /\n' + rule + '\n', 1)
            added.append(rule)
    if added:
        open('robots.txt', 'w', encoding='utf-8').write(r)
    print("robots.txt:", ", ".join(added) if added else "already set")
except FileNotFoundError:
    print("robots.txt not found - skipped")

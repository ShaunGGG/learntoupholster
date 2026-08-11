#!/usr/bin/env python3
"""
seo-prune.py — learntoupholster.com

Runs AFTER build-blog.py and fix-sitemap.py, because both regenerate the files
this touches. Idempotent: safe to run on every build.

Three jobs:

  1. NOINDEX the thin, near-duplicate pages. The six blog category pages are
     ~92% identical to each other (777 shared unique words vs ~30 unique).
     Google will not index near-duplicate taxonomy pages, and having them in
     the sitemap drags down the submitted-vs-indexed ratio, which is itself a
     quality signal on a young domain. They stay crawlable and linked
     (noindex,FOLLOW) so link equity still flows through to the posts.

  2. PRUNE those same URLs from sitemap.xml, so the sitemap only contains
     pages we actually want ranking.

  3. CLAMP future-dated <lastmod> values to today. Google distrusts sitemaps
     containing future dates and can start ignoring lastmod entirely, which
     costs you recrawl priority.

Usage:
    python3 seo-prune.py            # apply
    python3 seo-prune.py --dry-run  # report only, change nothing
"""

import glob
import os
import re
import sys
from datetime import date

# ---------------------------------------------------------------- config

# Glob patterns — picks up new categories automatically as build-blog.py
# creates them, so you never have to edit this list.
NOINDEX_GLOBS = [
    'blog/category/*.html',
]

# Individual files. Legal boilerplate: no search value, and thin.
# NOTE: contact.html is deliberately NOT here. It carries ContactPage schema
# and supports your local/E-E-A-T signals, so it stays indexable.
NOINDEX_FILES = [
    'privacy-policy.html',
    'terms-of-use.html',
    'disclaimer.html',
]

SITEMAP = 'sitemap.xml'
BASE = 'https://www.learntoupholster.com'
ROBOTS_TAG = '<meta name="robots" content="noindex,follow">'

DRY = '--dry-run' in sys.argv


# ---------------------------------------------------------------- helpers

def targets():
    """Resolve globs + explicit files into a sorted, deduplicated list."""
    found = []
    for pattern in NOINDEX_GLOBS:
        found.extend(glob.glob(pattern))
    for f in NOINDEX_FILES:
        if os.path.exists(f):
            found.append(f)
        else:
            print(f'  ! missing, skipped: {f}')
    return sorted(set(found))


def to_url(path):
    """blog/category/fabrics.html -> https://www.learntoupholster.com/blog/category/fabrics"""
    slug = path[:-5] if path.endswith('.html') else path
    if slug.endswith('/index'):
        slug = slug[:-6] + '/'
    return f'{BASE}/{slug}'


def add_noindex(path):
    """Insert the robots meta after the canonical link. Idempotent."""
    html = open(path, encoding='utf-8').read()

    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', html, re.I):
        return 'already'

    # Preferred anchor: straight after the canonical tag.
    canonical = re.search(r'(<link[^>]+rel=["\']canonical["\'][^>]*>)', html, re.I)
    if canonical:
        new = html.replace(canonical.group(1),
                           canonical.group(1) + '\n' + ROBOTS_TAG, 1)
    elif '</head>' in html:
        new = html.replace('</head>', ROBOTS_TAG + '\n</head>', 1)
    else:
        return 'no-anchor'

    if not DRY:
        open(path, 'w', encoding='utf-8').write(new)
    return 'added'


def prune_sitemap(drop_urls):
    """Remove <url> blocks whose <loc> is in drop_urls. Clamp future lastmods."""
    if not os.path.exists(SITEMAP):
        print(f'  ! {SITEMAP} not found — run fix-sitemap.py first')
        return 0, 0, 0

    xml = open(SITEMAP, encoding='utf-8').read()
    blocks = re.findall(r'[ \t]*<url>.*?</url>\s*', xml, re.S)
    if not blocks:
        print('  ! no <url> blocks parsed — sitemap format unexpected, aborting')
        return 0, 0, 0

    today = date.today().isoformat()
    kept, dropped, clamped = [], 0, 0

    for block in blocks:
        loc = re.search(r'<loc>(.*?)</loc>', block, re.S)
        if loc and loc.group(1).strip() in drop_urls:
            dropped += 1
            continue

        def fix_date(m):
            nonlocal clamped
            if m.group(1).strip() > today:
                clamped += 1
                return f'<lastmod>{today}</lastmod>'
            return m.group(0)

        kept.append(re.sub(r'<lastmod>(.*?)</lastmod>', fix_date, block))

    body = ''.join(kept).rstrip()
    out = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f'{body}\n</urlset>\n')

    if not DRY:
        open(SITEMAP, 'w', encoding='utf-8').write(out)

    return len(kept), dropped, clamped


# ---------------------------------------------------------------- main

def main():
    print('seo-prune' + ('  [DRY RUN — nothing written]' if DRY else ''))

    files = targets()
    if not files:
        print('  ! no target files found — are you in the repo root?')
        sys.exit(1)

    print(f'\n  noindexing {len(files)} pages:')
    counts = {'added': 0, 'already': 0, 'no-anchor': 0}
    for f in files:
        result = add_noindex(f)
        counts[result] += 1
        mark = {'added': '+', 'already': '=', 'no-anchor': '!'}[result]
        print(f'    {mark} {f}')

    drop = {to_url(f) for f in files}
    total, dropped, clamped = prune_sitemap(drop)

    print(f'\n  sitemap: {total} URLs  ({dropped} removed, {clamped} future dates clamped)')
    print(f'  noindex: {counts["added"]} added, {counts["already"]} already set', end='')
    if counts['no-anchor']:
        print(f', {counts["no-anchor"]} FAILED (no canonical or </head>)', end='')
    print('\n  done.')


if __name__ == '__main__':
    main()

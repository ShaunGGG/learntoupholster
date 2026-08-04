#!/usr/bin/env python3
"""
prune-sitemap.py — take dead URLs out of sitemap.xml.

update-sitemap.py adds pages it finds. It does not remove pages that have gone,
so the sitemap accumulates entries for deleted and redirected URLs. Right now it
lists /our-work, which 301s to /projects/, and /outreach/supplier-outreach, which
the middleware blocks.

Neither belongs there. A sitemap is a statement that these URLs are canonical and
worth indexing, and listing a redirect or a 404 wastes crawl budget and reads as
a site nobody is maintaining.

This checks each entry against the files on disk and removes the ones with
nothing behind them. It does not add anything \u2014 update-sitemap.py does that.
Run after it.

    python3 update-sitemap.py && python3 prune-sitemap.py
"""

import os, re, sys, shutil, datetime

SITEMAP = 'sitemap.xml'
SITE = 'https://www.learntoupholster.com'

# Paths served by a Function rather than a file on disk. Keep them.
FUNCTION_ROUTES = {'/mcp', '/search'}


def path_for(url):
    """Candidate files on disk for a site URL."""
    rel = url.replace(SITE, '').split('#')[0].split('?')[0]
    if rel in ('', '/'):
        return ['index.html']
    rel = rel.strip('/')
    return [rel + '.html', os.path.join(rel, 'index.html')]


def main():
    if not os.path.exists(SITEMAP):
        sys.exit('No %s here. Run this from ~/learntoupholster.' % SITEMAP)

    xml = open(SITEMAP, encoding='utf-8').read()
    entries = re.findall(r'<url>.*?</url>', xml, re.S)
    if not entries:
        sys.exit('No <url> entries found in %s. Nothing written.' % SITEMAP)

    keep, drop = [], []
    for e in entries:
        m = re.search(r'<loc>\s*([^<\s]+)\s*</loc>', e)
        if not m:
            keep.append(e)
            continue
        url = m.group(1)
        rel = url.replace(SITE, '').split('#')[0] or '/'
        if rel in FUNCTION_ROUTES:
            keep.append(e)
            continue
        if any(os.path.exists(p) for p in path_for(url)):
            keep.append(e)
        else:
            drop.append((rel, e))

    if not drop:
        print('%d URLs, nothing stale. Sitemap unchanged.' % len(entries))
        return

    out = xml
    for _rel, e in drop:
        out = out.replace(e, '', 1)
    out = re.sub(r'\n\s*\n+', '\n', out)

    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    bdir = os.path.join(os.path.expanduser('~'), 'ltu-backups', stamp)
    os.makedirs(bdir, exist_ok=True)
    shutil.copy2(SITEMAP, os.path.join(bdir, SITEMAP))
    open(SITEMAP, 'w', encoding='utf-8').write(out)

    print('%d URLs in, %d out' % (len(entries), len(keep)))
    print('\nRemoved \u2014 no page on disk:')
    for rel, _e in drop:
        print('   ' + rel)
    print('\nBackup: ~/ltu-backups/%s/%s' % (stamp, SITEMAP))


if __name__ == '__main__':
    main()

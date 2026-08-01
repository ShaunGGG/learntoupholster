#!/usr/bin/env python3
"""
update-sitemap.py — add published pages that are missing from sitemap.xml.

The Business Hub went live invisible: nine pages plus the hub, none of them in
the sitemap. Rather than hand-maintaining the list, this walks the site, works
out which pages are publicly served, and adds anything absent.

Conservative by design. It only adds; it never removes an existing entry, so
anything you have deliberately listed stays listed.

Run before deploying.
"""

import os, re, sys, glob, datetime

SITE = 'https://www.learntoupholster.com'
SITEMAP = 'sitemap.xml'

# Not indexable, or deliberately kept out.
EXCLUDE_DIRS = {'node_modules', '.git', 'functions', 'md', 'assets', 'images',
                'business-sources', 'project-sources', 'photos'}
EXCLUDE_SLUGS = {'404', '500', 'press-pack'}


def url_for(path):
    rel = os.path.splitext(path)[0].replace(os.sep, '/')
    if rel == 'index':
        return SITE + '/'
    if rel.endswith('/index'):
        return SITE + '/' + rel[:-len('/index')] + '/'
    return SITE + '/' + rel


def is_noindex(src):
    return bool(re.search(r'<meta[^>]+name="robots"[^>]+content="[^"]*noindex', src, re.I))


def main():
    if not os.path.exists('index.html'):
        sys.exit('Run this from ~/learntoupholster.')
    if not os.path.exists(SITEMAP):
        sys.exit('No %s found. This script updates an existing sitemap rather than '
                 'creating one, so you do not lose any hand-set entries.' % SITEMAP)

    sm = open(SITEMAP, encoding='utf-8').read()
    existing = set(re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', sm))

    found, skipped = {}, []
    for path in glob.glob('**/*.html', recursive=True):
        parts = path.split(os.sep)
        if any(p in EXCLUDE_DIRS for p in parts):
            continue
        slug = os.path.splitext(os.path.basename(path))[0]
        if slug in EXCLUDE_SLUGS:
            continue
        src = open(path, encoding='utf-8').read()
        if is_noindex(src):
            skipped.append(path + ' (noindex)')
            continue
        cm = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', src, re.I)
        url = cm.group(1).strip() if cm else url_for(path)
        found[url] = path

    missing = [u for u in sorted(found) if u not in existing]

    print('%d pages on disk, %d already in the sitemap' % (len(found), len(found) - len(missing)))
    if not missing:
        print('Nothing to add.')
        return

    print('Adding %d:' % len(missing))
    for u in missing:
        print('   + ' + u.replace(SITE, ''))

    today = datetime.date.today().isoformat()
    block = ''.join('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>\n'
                    % (u, today) for u in missing)

    m = re.search(r'\n?\s*</urlset>\s*$', sm)
    if not m:
        sys.exit('Could not find the closing </urlset> tag. Sitemap left untouched.')

    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    bdir = os.path.join(os.path.expanduser('~'), 'ltu-backups', stamp)
    os.makedirs(bdir, exist_ok=True)
    open(os.path.join(bdir, SITEMAP), 'w', encoding='utf-8').write(sm)

    open(SITEMAP, 'w', encoding='utf-8').write(sm[:m.start()] + '\n' + block + '</urlset>\n')
    print('\n%s updated. Backup: ~/ltu-backups/%s/' % (SITEMAP, stamp))
    if skipped:
        print('Left out (noindex): ' + ', '.join(skipped))


if __name__ == '__main__':
    main()

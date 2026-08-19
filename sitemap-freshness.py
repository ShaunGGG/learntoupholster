#!/usr/bin/env python3
"""
sitemap-freshness.py — honest <lastmod> dates based on content, not git.

The problem with git dates: your workflow is bulk patch scripts, so one run
rewrites every HTML file and `git log -1` then claims all 119 pages changed
that day. That is a worse signal than a stale date -- it looks like a bulk
regeneration, which is exactly what Google discounts.

This instead stores a hash of each page's MEANINGFUL content in
.sitemap-hashes.json. A page's date only moves when its visible text actually
changes. Patch scripts that touch the nav, footer, scripts or head do not
count, because those are stripped before hashing.

FIRST RUN IS A SEED. It reads the dates already in sitemap.xml, records them
against current hashes, and changes nothing. That preserves the varied dates
you have now. From the second run onward it only updates pages whose content
genuinely differs.

  python3 sitemap-freshness.py            # dry run, shows what would change
  python3 sitemap-freshness.py --apply

Run it AFTER update-sitemap.py and fix-sitemap.py, as the last step before
deploy. Commit .sitemap-hashes.json -- without it every clone re-seeds.
"""

import os
import re
import sys
import json
import hashlib
import shutil
import datetime

BASE = 'https://www.learntoupholster.com'
SM = 'sitemap.xml'
MANIFEST = '.sitemap-hashes.json'
APPLY = '--apply' in sys.argv
TODAY = datetime.date.today().isoformat()

# Everything that a bulk patch script is likely to rewrite across all pages at
# once. Stripped before hashing so nav/footer/schema churn does not count as a
# content change.
STRIP = re.compile(
    r'<head\b.*?</head>|<nav\b.*?</nav>|<footer\b.*?</footer>'
    r'|<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->',
    re.S | re.I)


def url_to_path(loc):
    """Map a canonical URL back to the file that serves it. Mirrors fix-sitemap.py."""
    p = loc.replace(BASE, '').split('#')[0].split('?')[0]
    if p in ('', '/'):
        return 'index.html'
    p = p.lstrip('/')
    if p.endswith('/'):
        return p + 'index.html'
    if os.path.exists(p + '.html'):
        return p + '.html'
    if os.path.exists(os.path.join(p, 'index.html')):
        return os.path.join(p, 'index.html')
    return p + '.html'


def content_hash(path):
    """Hash of the visible body text, whitespace-normalised."""
    try:
        src = open(path, encoding='utf-8').read()
    except Exception:
        return None
    body = STRIP.sub(' ', src)
    text = re.sub(r'<[^>]+>', ' ', body)
    text = re.sub(r'\s+', ' ', text).strip()
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def main():
    if not os.path.exists(SM):
        sys.exit('ABORT: sitemap.xml not found -- run from ~/learntoupholster')

    xml = open(SM, encoding='utf-8').read()
    blocks = re.findall(r'[ \t]*<url>.*?</url>\s*\n?', xml, re.S)
    if not blocks:
        sys.exit('ABORT: no <url> blocks parsed, sitemap left untouched')

    manifest = {}
    seeding = not os.path.exists(MANIFEST)
    if not seeding:
        try:
            manifest = json.load(open(MANIFEST, encoding='utf-8'))
        except Exception as e:
            sys.exit(f'ABORT: {MANIFEST} unreadable ({e}). Fix or delete it to re-seed.')

    out, changed, unchanged, new, missing = [], [], 0, [], []

    for b in blocks:
        m = re.search(r'<loc>(.*?)</loc>', b, re.S)
        if not m:
            out.append(b.rstrip('\n'))
            continue
        loc = m.group(1).strip()
        path = url_to_path(loc)
        h = content_hash(path)

        lm = re.search(r'<lastmod>(.*?)</lastmod>', b)
        current = lm.group(1).strip() if lm else None

        if h is None:
            missing.append((loc, path))
            out.append(b.rstrip('\n'))
            continue

        rec = manifest.get(loc)

        if rec is None:
            # Unknown page: trust the date already in the sitemap, else today.
            date = current or TODAY
            manifest[loc] = {'hash': h, 'date': date}
            if not seeding:
                new.append((loc, date))
        elif rec.get('hash') == h:
            date = rec.get('date', current or TODAY)
            unchanged += 1
        else:
            date = TODAY
            changed.append((loc, rec.get('date'), date))
            manifest[loc] = {'hash': h, 'date': date}

        if lm:
            b = re.sub(r'<lastmod>.*?</lastmod>', f'<lastmod>{date}</lastmod>', b, count=1)
        else:
            b = b.replace('</loc>', f'</loc><lastmod>{date}</lastmod>', 1)
        out.append(b.rstrip('\n'))

    # Drop manifest entries for URLs no longer in the sitemap.
    live = {re.search(r'<loc>(.*?)</loc>', b, re.S).group(1).strip()
            for b in blocks if re.search(r'<loc>(.*?)</loc>', b, re.S)}
    dropped = [u for u in list(manifest) if u not in live]
    for u in dropped:
        del manifest[u]

    new_xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + '\n'.join('  ' + k.strip() for k in out)
               + '\n</urlset>\n')

    print('=' * 62)
    print('sitemap-freshness.py — ' + ('SEEDING' if seeding else
                                       ('APPLYING' if APPLY else 'DRY RUN')))
    print('=' * 62)

    if seeding:
        print(f'First run. Recording hashes for {len(manifest)} pages against the')
        print('dates already in sitemap.xml. No dates change.')
    else:
        print(f'unchanged content : {unchanged}')
        print(f'content changed   : {len(changed)}')
        for loc, was, now in changed:
            print(f'    * {loc.replace(BASE, "")}  {was} -> {now}')
        if new:
            print(f'new to manifest   : {len(new)}')
            for loc, d in new:
                print(f'    + {loc.replace(BASE, "")}  ({d})')
    if dropped:
        print(f'dropped from manifest (no longer in sitemap): {len(dropped)}')
    if missing:
        print(f'!! {len(missing)} sitemap entries have no file on disk:')
        for loc, path in missing:
            print(f'    ? {loc}  ({path})')
        print('   Their dates were left exactly as they were.')

    if not APPLY:
        print('\nDRY RUN — nothing written. Re-run with --apply.')
        return 0

    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    bdir = os.path.join(os.path.expanduser('~'), 'ltu-backups', stamp)
    os.makedirs(bdir, exist_ok=True)
    shutil.copy2(SM, os.path.join(bdir, SM))
    if os.path.exists(MANIFEST):
        shutil.copy2(MANIFEST, os.path.join(bdir, MANIFEST))

    open(SM, 'w', encoding='utf-8').write(new_xml)
    json.dump(manifest, open(MANIFEST, 'w', encoding='utf-8'),
              indent=1, sort_keys=True)

    print(f'\nWritten. Backup: ~/ltu-backups/{stamp}/')
    print(f'Commit {MANIFEST} alongside sitemap.xml.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

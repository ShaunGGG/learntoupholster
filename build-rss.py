#!/usr/bin/env python3
"""Generate /rss.xml from sitemap.xml + each page's own title/description/date,
and add the RSS autodiscovery <link> to every page head.

Run AFTER fix-sitemap.py so the feed inherits the cleaned URL list and dates.
Idempotent.
"""
import re, os, html, datetime, glob

BASE = 'https://www.learntoupholster.com'
SM = 'sitemap.xml'
OUT = 'rss.xml'
LIMIT = 40

# Utility/legal pages don't belong in a content feed.
EXCLUDE = {
    '/privacy-policy', '/terms-of-use', '/disclaimer', '/cookie-policy',
    '/contact', '/use-in-ai', '/search', '/press-pack',
}

ALT = ('<link rel="alternate" type="application/rss+xml" '
       f'title="Learn to Upholster" href="{BASE}/rss.xml">')


def url_to_path(loc):
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


def meta(h, pat):
    m = re.search(pat, h, re.S | re.I)
    return html.unescape(m.group(1).strip()) if m else None


def rfc822(datestr):
    try:
        d = datetime.date.fromisoformat(datestr)
    except Exception:
        d = datetime.date.today()
    return datetime.datetime(d.year, d.month, d.day, 9, 0, 0).strftime(
        '%a, %d %b %Y %H:%M:%S +0000')


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def build_feed():
    if not os.path.exists(SM):
        print('!! sitemap.xml not found - run from ~/learntoupholster')
        raise SystemExit(1)

    xml = open(SM, encoding='utf-8').read()
    entries = []
    for b in re.findall(r'<url>.*?</url>', xml, re.S):
        loc = re.search(r'<loc>(.*?)</loc>', b, re.S)
        if not loc:
            continue
        loc = loc.group(1).strip()
        slug = loc.replace(BASE, '').rstrip('/') or '/'
        if slug in EXCLUDE:
            continue
        lm = re.search(r'<lastmod>(.*?)</lastmod>', b, re.S)
        lastmod = lm.group(1).strip() if lm else datetime.date.today().isoformat()
        path = url_to_path(loc)
        if not os.path.exists(path):
            continue
        h = open(path, encoding='utf-8', errors='ignore').read()
        title = meta(h, r'<title[^>]*>(.*?)</title>') or slug
        title = re.sub(r'\s*\|\s*Learn to Upholster\s*$', '', title).strip()
        desc = meta(h, r'<meta name="description" content="(.*?)"') or ''
        entries.append((lastmod, loc, title, desc))

    entries.sort(key=lambda e: e[0], reverse=True)
    entries = entries[:LIMIT]

    now = datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    items = []
    for lastmod, loc, title, desc in entries:
        items.append(
            '    <item>\n'
            f'      <title>{esc(title)}</title>\n'
            f'      <link>{esc(loc)}</link>\n'
            f'      <guid isPermaLink="true">{esc(loc)}</guid>\n'
            f'      <description>{esc(desc)}</description>\n'
            f'      <pubDate>{rfc822(lastmod)}</pubDate>\n'
            '    </item>'
        )

    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '  <channel>\n'
        '    <title>Learn to Upholster</title>\n'
        f'    <link>{BASE}/</link>\n'
        '    <description>The Working Upholsterer&#8217;s Bible by Shaun Greenwood '
        '&#8212; traditional and modern upholstery, free to read.</description>\n'
        '    <language>en-GB</language>\n'
        f'    <lastBuildDate>{now}</lastBuildDate>\n'
        f'    <atom:link href="{BASE}/rss.xml" rel="self" type="application/rss+xml"/>\n'
        + '\n'.join(items) + '\n'
        '  </channel>\n'
        '</rss>\n'
    )
    open(OUT, 'w', encoding='utf-8').write(feed)
    print(f'{OUT}: built with {len(entries)} items (newest: {entries[0][2] if entries else "none"})')


def add_autodiscovery():
    files = sorted(glob.glob('*.html') + glob.glob('*/*.html'))
    added = 0
    for f in files:
        if os.path.basename(f) == '404.html':
            continue
        h = open(f, encoding='utf-8', errors='ignore').read()
        if 'application/rss+xml' in h or '</head>' not in h:
            continue
        h = h.replace('</head>', ALT + '\n</head>', 1)
        open(f, 'w', encoding='utf-8').write(h)
        added += 1
    print(f'RSS autodiscovery link added to {added} page(s)'
          + (' (all pages already had it)' if added == 0 else ''))


if __name__ == '__main__':
    build_feed()
    add_autodiscovery()

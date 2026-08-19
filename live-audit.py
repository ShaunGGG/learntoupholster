#!/usr/bin/env python3
"""
live-audit.py — compare the LIVE site against the local repo.

Why this exists: the repo is clean, but Cloudflare's edge has served stale
pages before. A clean repo does not prove a clean live site. This fetches
every sitemap URL from the real origin and reports drift.

Run from ~/learntoupholster.  No writes. Safe to run any time.
    python3 live-audit.py
    python3 live-audit.py --slow     (1s between requests)
"""
import re, os, sys, glob, socket, time, urllib.request, urllib.error

# Crostini: force IPv4, same reason wrangler needs --dns-result-order=ipv4first
_orig = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _orig(*a, **k) if r[0] == socket.AF_INET] or _orig(*a, **k)

SLOW = '--slow' in sys.argv
UA = 'Mozilla/5.0 (compatible; LTUAudit/1.0)'

def fetch(url):
    req = urllib.request.Request(url + ('&' if '?' in url else '?') + 'cb=%d' % time.time(),
                                 headers={'User-Agent': UA, 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, dict(r.headers), r.read().decode('utf-8', 'replace'), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), '', url
    except Exception as e:
        return 0, {}, str(e), url

def local_path(url):
    p = url.replace('https://www.learntoupholster.com/', '')
    if p in ('', '/'): return 'index.html'
    p = p.rstrip('/')
    for cand in (p + '.html', p + '/index.html'):
        if os.path.exists(cand): return cand
    return None

sm = open('sitemap.xml', encoding='utf-8').read()
urls = re.findall(r'<loc>(.*?)</loc>', sm)
print("Auditing %d sitemap URLs against the live origin...\n" % len(urls))

bad_status, redirected, noindexed, canon_drift, size_drift, missing_local = [], [], [], [], [], []

for i, u in enumerate(urls, 1):
    st, hdr, body, final = fetch(u)
    tag = ''
    if st != 200:
        bad_status.append((u, st)); tag = 'STATUS %s' % st
    else:
        if final.split('?')[0].rstrip('/') != u.rstrip('/'):
            redirected.append((u, final.split('?')[0])); tag = 'REDIRECT'
        xr = hdr.get('X-Robots-Tag', '')
        meta_noidx = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*noindex', body, re.I)
        if 'noindex' in xr.lower() or meta_noidx:
            noindexed.append((u, xr or 'meta tag')); tag = (tag + ' NOINDEX').strip()
        m = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', body)
        if m and m.group(1).rstrip('/') != u.rstrip('/'):
            canon_drift.append((u, m.group(1))); tag = (tag + ' CANON').strip()
        lp = local_path(u)
        if lp is None:
            missing_local.append(u); tag = (tag + ' NO-LOCAL').strip()
        else:
            lsize = len(open(lp, encoding='utf-8', errors='replace').read())
            if lsize and abs(len(body) - lsize) / lsize > 0.08:
                size_drift.append((u, lp, lsize, len(body))); tag = (tag + ' DRIFT').strip()
    print("  [%3d/%d] %-4s %s %s" % (i, len(urls), st, u.replace('https://www.learntoupholster.com', ''), tag))
    if SLOW: time.sleep(1)

def block(title, rows, fmt):
    print("\n=== %s: %d ===" % (title, len(rows)))
    for r in rows: print("   " + fmt(r))

block("NON-200 STATUS", bad_status, lambda r: "%s -> HTTP %s" % (r[0], r[1]))
block("SITEMAP URLS THAT REDIRECT", redirected, lambda r: "%s -> %s" % (r[0], r[1]))
block("NOINDEXED BUT IN SITEMAP", noindexed, lambda r: "%s (%s)" % (r[0], r[1]))
block("CANONICAL POINTS ELSEWHERE", canon_drift, lambda r: "%s -> %s" % (r[0], r[1]))
block("LIVE/REPO SIZE DRIFT >8% (stale edge cache?)", size_drift,
      lambda r: "%s  repo=%d live=%d  (%s)" % (r[0], r[2], r[3], r[1]))
block("NO LOCAL FILE FOR SITEMAP URL", missing_local, lambda r: r)

total = sum(map(len, (bad_status, redirected, noindexed, canon_drift, size_drift, missing_local)))
print("\n%s" % ("CLEAN - live site matches repo, nothing to fix." if total == 0
                else "%d issue(s) found above." % total))

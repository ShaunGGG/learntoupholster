#!/usr/bin/env python3
"""Repair sitemap.xml:
   1. Remove any <url> whose page no longer exists on disk (dead entries -> 404s in sitemap).
   2. Add a <lastmod> to any entry missing one, taken from git history, falling back to file mtime.
   Idempotent. Safe to run repeatedly.
"""
import re, os, subprocess, datetime, fnmatch

BASE = 'https://www.learntoupholster.com'
SM = 'sitemap.xml'


def load_assetsignore():
    """Cloudflare Pages will not serve anything matched by .assetsignore.
    A file can exist on disk and still 404, so existence alone is not enough."""
    pats = []
    if os.path.exists('.assetsignore'):
        for line in open('.assetsignore', encoding='utf-8'):
            line = line.strip()
            if line and not line.startswith('#'):
                pats.append(line)
    return pats


def is_ignored(path, pats):
    parts = path.split('/')
    for pat in pats:
        if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
            return True
        # A bare directory name excludes everything beneath it.
        if any(fnmatch.fnmatch(seg, pat) for seg in parts[:-1]):
            return True
    return False

def url_to_path(loc):
    """Map a canonical URL back to the file that serves it."""
    p = loc.replace(BASE, '').split('#')[0].split('?')[0]
    if p in ('', '/'):
        return 'index.html'
    p = p.lstrip('/')
    if p.endswith('/'):
        return p + 'index.html'
    # /foo -> foo.html, but /foo/ style dirs may also exist as foo/index.html
    if os.path.exists(p + '.html'):
        return p + '.html'
    if os.path.exists(os.path.join(p, 'index.html')):
        return os.path.join(p, 'index.html')
    return p + '.html'

def file_date(path):
    """Last commit date for the file; falls back to mtime for uncommitted files."""
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%ad', '--date=short', '--', path],
                             capture_output=True, text=True, timeout=20)
        d = out.stdout.strip()
        if d:
            return d
    except Exception:
        pass
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()
    except Exception:
        return datetime.date.today().isoformat()

def main():
    if not os.path.exists(SM):
        print('!! sitemap.xml not found - are you in ~/learntoupholster ?')
        raise SystemExit(1)

    xml = open(SM, encoding='utf-8').read()
    blocks = re.findall(r'[ \t]*<url>.*?</url>\s*\n?', xml, re.S)
    if not blocks:
        print('!! no <url> blocks parsed - sitemap left untouched')
        raise SystemExit(1)

    removed, dated, kept = [], [], []
    pats = load_assetsignore()

    for b in blocks:
        m = re.search(r'<loc>(.*?)</loc>', b, re.S)
        if not m:
            continue
        loc = m.group(1).strip()
        path = url_to_path(loc)

        if not os.path.exists(path):
            removed.append((loc, path, 'no file'))
            continue

        if is_ignored(path, pats):
            removed.append((loc, path, 'excluded by .assetsignore - not served'))
            continue

        if '<lastmod>' not in b:
            d = file_date(path)
            b = b.replace('</loc>', f'</loc><lastmod>{d}</lastmod>', 1)
            dated.append((loc, d))
        kept.append(b.rstrip('\n'))

    # Safety guard: removing a handful of dead entries is a fix; removing lots
    # means files are missing from this working copy, and rewriting the sitemap
    # would quietly delist live pages. Abort instead.
    MAX_REMOVE = 3
    if len(removed) > MAX_REMOVE:
        print(f'!! ABORTED - {len(removed)} entries have no matching file, which is more')
        print(f'!! than the safety limit of {MAX_REMOVE}. sitemap.xml has NOT been changed.')
        print('!! Those pages are probably live but missing from this folder. Check first:')
        for loc, path, why in removed:
            print(f'    ? {loc}   ({why}: {path})')
        raise SystemExit(1)

    new = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + '\n'.join('  ' + k.strip() for k in kept)
           + '\n</urlset>\n')

    open(SM, 'w', encoding='utf-8').write(new)

    print(f'sitemap.xml: {len(kept)} URLs kept')
    if removed:
        print(f'  removed {len(removed)} dead entr{"y" if len(removed)==1 else "ies"}:')
        for loc, path, why in removed:
            print(f'    - {loc}   ({why})')
    else:
        print('  no dead entries found')
    if dated:
        print(f'  added lastmod to {len(dated)}:')
        for loc, d in dated:
            print(f'    + {loc}  -> {d}')
    else:
        print('  all entries already had lastmod')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
build-md-extra.py — markdown variants for pages build-md.py doesn't reach.

build-md.py scans the site root, so anything in a subdirectory gets no .md
variant and therefore never lands in llms-full.txt. That currently means the
whole Business Hub and all six project pages.

This walks the subdirectories, converts each page's <article> to markdown in the
same shape build-md.py produces, and writes md/<path>.md.

Run after build-business.py and build-projects.py, before build-llms.py.
"""

import os, re, sys, glob, html as H

SITE = 'https://www.learntoupholster.com'
DIRS = ['business', 'projects', 'state-of-the-trade']

# Root pages build-md.py does not pick up. Rather than maintain a list — which
# has now been forgotten five times running — find them: any root .html page
# that has no markdown variant is a page missing from llms-full.txt.
#
# Excluded because they are not content: error pages, anything noindexed, and
# the legal boilerplate the llms build drops anyway.
ROOT_EXCLUDE = {'404', '500', 'index', 'search', 'press-pack',
                'cookie-policy', 'privacy-policy', 'terms-of-use', 'disclaimer'}


def find_orphan_root_pages():
    """Root pages with no md/<slug>.md — i.e. invisible to llms-full.txt."""
    out = []
    for path in sorted(glob.glob('*.html')):
        slug = os.path.splitext(path)[0]
        if slug in ROOT_EXCLUDE:
            continue
        if os.path.exists(os.path.join(MD_DIR, slug + '.md')):
            continue
        src = open(path, encoding='utf-8').read()
        if re.search(r'<meta[^>]+name="robots"[^>]+content="[^"]*noindex', src, re.I):
            continue
        out.append(path)
    return out
MD_DIR = 'md'


def inline(s):
    # UI-only badges ("Read now", "Free") are navigation furniture, not content.
    s = re.sub(r'<span class="tag-(?:live|soon)"[^>]*>.*?</span>', '', s, flags=re.S | re.I)
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', s, flags=re.S | re.I)
    s = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'**\2**', s, flags=re.S | re.I)
    s = re.sub(r'<(em|i|cite)[^>]*>(.*?)</\1>', r'*\2*', s, flags=re.S | re.I)

    def link(m):
        href, text = m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if href.startswith('/'):
            href = SITE + href
        return '[%s](%s)' % (text, href) if text else ''
    s = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', link, s, flags=re.S | re.I)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'[ \t]+', ' ', H.unescape(s)).strip()


def article_to_md(art):
    art = re.sub(r'<(script|style|svg)[^>]*>.*?</\1>', '', art, flags=re.S | re.I)
    out, pos = [], 0
    pattern = re.compile(
        r'<(h1|h2|h3|h4|p|ul|ol|blockquote)([^>]*)>(.*?)</\1>', re.S | re.I)
    for m in pattern.finditer(art):
        tag, attrs, inner = m.group(1).lower(), m.group(2), m.group(3)
        if 'biz-crumb' in attrs or 'chno' in attrs or 'updated' in attrs:
            continue
        if tag in ('h1', 'h2', 'h3', 'h4'):
            out.append('#' * int(tag[1]) + ' ' + inline(inner))
        elif tag == 'p':
            t = inline(inner)
            if t:
                out.append(t)
        elif tag in ('ul', 'ol'):
            items = re.findall(r'<li[^>]*>(.*?)</li>', inner, re.S | re.I)
            for n, it in enumerate(items, 1):
                t = inline(it)
                if t:
                    out.append(('%d. ' % n if tag == 'ol' else '- ') + t)
            out.append('')
        elif tag == 'blockquote':
            t = inline(inner)
            if t:
                out.append('> ' + t)
    return '\n\n'.join(x for x in out if x is not None).strip()


def main():
    if not os.path.exists('index.html'):
        sys.exit('Run this from ~/learntoupholster.')
    os.makedirs(MD_DIR, exist_ok=True)

    written, skipped = [], []

    targets = find_orphan_root_pages()
    if targets:
        print('root pages with no markdown variant: %s'
              % ', '.join(os.path.splitext(t)[0] for t in targets))
    for d in DIRS:
        if os.path.isdir(d):
            targets.extend(sorted(glob.glob(os.path.join(d, '**', '*.html'), recursive=True)))

    for _pass in (1,):
        for path in targets:
            src = open(path, encoding='utf-8').read()
            art = re.search(r'<article[^>]*>(.*?)</article>', src, re.S)
            if art:
                inner = art.group(1)
            else:
                # Project pages don't use <article>; their content sits in one or
                # more <section class="wrap read"> blocks. The tail's promo
                # sections are plain "wrap", so this does not pick them up.
                secs = re.findall(r'<section class="wrap read"[^>]*>(.*?)</section>', src, re.S)
                if not secs:
                    skipped.append(path + ' (no <article> or <section class="wrap read">)')
                    continue
                inner = '\n'.join(secs)

            t = re.search(r'<title>(.*?)</title>', src, re.S | re.I)
            title = re.sub(r'\s*\|\s*Learn to Upholster\s*$', '',
                           H.unescape(t.group(1)).strip()) if t else os.path.basename(path)
            dm = re.search(r'<meta\s+name="description"\s+content="(.*?)"', src, re.S | re.I)
            desc = re.sub(r'\s+', ' ', H.unescape(dm.group(1)).strip()) if dm else ''
            cm = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', src, re.I)
            kick = re.search(r'<p class="chno">(.*?)</p>', src, re.S)

            rel = os.path.splitext(path)[0]
            if os.path.basename(rel) == 'index':
                rel = os.path.dirname(rel)
                url = SITE + '/' + rel + '/'
                out_rel = rel + '/index'
            else:
                url = SITE + '/' + rel.replace(os.sep, '/')
                out_rel = rel
            if cm:
                url = cm.group(1)

            body = article_to_md(inner)
            if not body:
                skipped.append(path + ' (empty body)')
                continue

            doc = ['# ' + title, '']
            if kick:
                doc += ['*' + inline(kick.group(1)) + '*', '']
            if desc:
                doc += ['> ' + desc, '']
            doc += ['Canonical: ' + url, '', body, '']

            out_path = os.path.join(MD_DIR, out_rel.replace(os.sep, os.sep) + '.md')
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            open(out_path, 'w', encoding='utf-8').write('\n'.join(doc))
            written.append(out_path)

    print('%d markdown variants written' % len(written))
    by_dir = {}
    for w in written:
        k = os.path.relpath(w, MD_DIR).split(os.sep)[0]
        by_dir[k] = by_dir.get(k, 0) + 1
    for k in sorted(by_dir):
        print('   %-12s %d' % (k, by_dir[k]))
    if skipped:
        print('Skipped:')
        for s in skipped:
            print('   - ' + s)


if __name__ == '__main__':
    main()

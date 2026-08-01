#!/usr/bin/env python3
"""
build-llms.py — regenerate llms.txt and llms-full.txt from md/ and the page HTML.

v2: walks md/ recursively. The first version globbed md/*.md, which quietly
excluded everything in a subdirectory — the Business Hub and, as it turns out,
the six project pages, which had never been in llms-full.txt at all.

Run after build-md.py and build-business.py.
"""

import os, re, sys, glob, html, datetime

SITE = 'https://www.learntoupholster.com'
MD_DIR = 'md'

HEADER_FULL = """# Learn to Upholster \u2014 The Working Upholsterer's Bible (full text)

> By Shaun Greenwood, master upholsterer (AMUSF accredited), Greenwood Upholstery, Hebden Bridge.
> The complete text of the free online edition, including the Business Hub and project write-ups.
> Canonical URLs at {site}
> Usage signals: search=yes, ai-input=yes, ai-train=no (see /robots.txt).
> Knowledge version: {version}. Generated {date}.
> Tools: this reference is also queryable over MCP at {site}/mcp \u2014 see {site}/use-in-ai
"""

HEADER_INDEX = """# Learn to Upholster \u2014 The Working Upholsterer's Bible

> The complete text of The Working Upholsterer's Bible by Shaun Greenwood (master upholsterer, AMUSF accredited, Greenwood Upholstery, Hebden Bridge), published free online. Traditional and modern upholstery: materials, techniques, full step-by-step projects, business guidance for working upholsterers, and free calculators.

The complete text in one file: {site}/llms-full.txt
Queryable over MCP, including six upholstery calculators: {site}/mcp (documentation: {site}/use-in-ai)

## Chapters and pages
"""

# Pages that add nothing to an upholstery knowledge corpus.
NOISE = re.compile(r'(cookie|privacy|terms|disclaimer)', re.I)

# A page kept out of search should be kept out of the AI corpus too. Feeding a
# noindexed page to llms-full.txt while excluding it from the sitemap is an
# inconsistency an AI has no way to detect.
NOINDEX = re.compile(r'<meta[^>]+name="robots"[^>]+content="[^"]*noindex', re.I)


def knowledge_version():
    return datetime.date.today().strftime('%Y.%m')


def html_path_for(rel_slug):
    """md/business/foo.md -> business/foo.html or business/foo/index.html"""
    for cand in (rel_slug + '.html', os.path.join(rel_slug, 'index.html')):
        if os.path.exists(cand):
            return cand
    return None


def page_meta(rel_slug):
    """Title, description, and the page's own canonical URL.

    Taking the canonical rather than building a URL from the file path matters
    for directory indexes: md/business/index.md would otherwise be published as
    /business/index, which only redirects. Citing a redirect is a weaker
    citation than citing the page, and it contradicts what the page declares.
    """
    p = html_path_for(rel_slug)
    if not p:
        return None, '', None
    h = open(p, encoding='utf-8').read()
    t = re.search(r'<title>(.*?)</title>', h, re.S | re.I)
    d = re.search(r'<meta\s+name="description"\s+content="(.*?)"', h, re.S | re.I)
    c = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', h, re.I)
    title = html.unescape(t.group(1)).strip() if t else None
    if title:
        title = re.sub(r'\s*\|\s*Learn to Upholster\s*$', '', title).strip()
    desc = html.unescape(d.group(1)).strip() if d else ''
    canon = c.group(1).strip() if c else None
    if NOINDEX.search(h):
        return None, '', 'NOINDEX'
    return title, re.sub(r'\s+', ' ', desc), canon


def parse_md(path):
    text = open(path, encoding='utf-8').read()
    lines = text.split('\n')
    title, start = None, 0
    for i, ln in enumerate(lines):
        if ln.startswith('# ') and title is None:
            title = ln[2:].strip(); start = i + 1; break
    i = start
    while i < len(lines):
        s = lines[i].strip()
        if s == '' or s.startswith('>') or s.startswith('*') or s.startswith('Canonical:'):
            i += 1
        else:
            break
    return title, '\n'.join(lines[i:]).strip()


def demote(body):
    """Shift headings so the shallowest body heading sits at '###'."""
    levels = [len(m) for m in re.findall(r'^(#{1,6}) ', body, re.M)]
    if not levels:
        return body
    shift = max(0, 3 - min(levels))
    if not shift:
        return body
    out, fence = [], False
    for ln in body.split('\n'):
        if ln.strip().startswith('```'):
            fence = not fence
        if not fence:
            m = re.match(r'^(#{1,6})( .*)$', ln)
            if m:
                ln = '#' * min(6, len(m.group(1)) + shift) + m.group(2)
        out.append(ln)
    return '\n'.join(out)


def main():
    if not os.path.isdir(MD_DIR):
        sys.exit('No md/ directory. Run build-md.py first.')

    paths = sorted(glob.glob(os.path.join(MD_DIR, '**', '*.md'), recursive=True))
    if not paths:
        sys.exit('md/ is empty. Run build-md.py first.')

    pages, skipped_noise, skipped_noindex = [], 0, 0
    for p in paths:
        rel = os.path.relpath(p, MD_DIR)
        rel_slug = os.path.splitext(rel)[0].replace(os.sep, '/')
        if NOISE.search(rel_slug):
            skipped_noise += 1
            continue
        md_title, body = parse_md(p)
        if not body:
            continue
        html_title, desc, canon = page_meta(rel_slug)
        if canon == 'NOINDEX':
            skipped_noindex += 1
            continue
        title = html_title or md_title or rel_slug
        if canon:
            url = canon
        elif rel_slug == 'index':
            url = SITE + '/'
        elif rel_slug.endswith('/index'):
            url = SITE + '/' + rel_slug[:-len('index')]
        else:
            url = SITE + '/' + rel_slug
        pages.append({'slug': rel_slug, 'title': title, 'desc': desc, 'url': url, 'body': body})

    pages.sort(key=lambda d: d['title'].lower())
    version, today = knowledge_version(), datetime.date.today().isoformat()

    idx = [HEADER_INDEX.format(site=SITE)]
    for pg in pages:
        line = '- [%s](%s)' % (pg['title'], pg['url'])
        if pg['desc']:
            line += ': ' + pg['desc']
        idx.append(line)
    idx_text = '\n'.join(idx).rstrip() + '\n'

    full = [HEADER_FULL.format(site=SITE, version=version, date=today)]
    for pg in pages:
        full += ['', '## %s \u2014 %s' % (pg['title'], pg['url']), '', demote(pg['body'])]
    full_text = '\n'.join(full).rstrip() + '\n'

    prev_i = os.path.getsize('llms.txt') if os.path.exists('llms.txt') else 0
    prev_f = os.path.getsize('llms-full.txt') if os.path.exists('llms-full.txt') else 0
    open('llms.txt', 'w', encoding='utf-8').write(idx_text)
    open('llms-full.txt', 'w', encoding='utf-8').write(full_text)

    def delta(new, old):
        if not old:
            return 'new'
        d = new - old
        return '%+.1fKB' % (d / 1024.0) if d else 'unchanged'

    subs = {}
    for pg in pages:
        subs[pg['slug'].split('/')[0] if '/' in pg['slug'] else '(root)'] = \
            subs.get(pg['slug'].split('/')[0] if '/' in pg['slug'] else '(root)', 0) + 1

    print('%d pages -> llms.txt (%.1fKB, %s), llms-full.txt (%.1fKB, %s)' % (
        len(pages), len(idx_text) / 1024.0, delta(len(idx_text), prev_i),
        len(full_text) / 1024.0, delta(len(full_text), prev_f)))
    for k in sorted(subs):
        print('   %-14s %d' % (k, subs[k]))
    if skipped_noise:
        print('   %-14s %d (excluded: no upholstery content)' % ('legal/utility', skipped_noise))
    if skipped_noindex:
        print('   %-14s %d (excluded: noindex)' % ('noindexed', skipped_noindex))
    print('knowledge version: %s' % version)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Rebuild ask-index.json from the site's HTML. Run after adding or editing chapters:
    python3 build-ask-index.py
Requires: pip install lxml

Now covers subdirectories as well as the root, so the Business Hub, the project
write-ups and the supplier directory are all reachable through ask_the_book.
"""
import glob, json, os, re
from lxml import html

# Matched on the file name, so business/index.html is skipped by 'index.html'
# the same way the root one is.
SKIP = {'search.html', 'index.html', '404.html', 'privacy-policy.html',
        'cookie-policy.html', 'terms-of-use.html', 'disclaimer.html',
        'contents.html', 'contact.html', 'our-work.html',
        'find-an-upholsterer.html', 'about.html',
        # Forms and interactive pages: the text is field labels, which makes
        # noise rather than answers.
        'workshop-forms.html', 'take-part.html', 'press-pack.html'}

SKIP_DIRS = {'md', 'functions', 'node_modules', 'assets', 'images', '.git',
             'business-sources', 'project-sources', 'photos', 'outreach'}

# Interface furniture that appears inside the content wrapper. Without these the
# survey call-to-action at the foot of every Business Hub article, the directory
# filters and the Pro block all end up in the index as though they were prose.
EXCL = {'tools', 'related', 'capture',
        'biz-footnote', 'biz-survey', 'biz-pro', 'biz-tools', 'biz-related',
        'sup-filters', 'sup-form', 'sv-progress', 'wf-setup', 'wf-index',
        'sv-setup', 'biz-crumb'}

NOINDEX = re.compile(r'<meta[^>]+name="robots"[^>]+content="[^"]*noindex', re.I)


def excluded(el):
    a = el
    while a is not None:
        c = a.get('class') or ''
        if any(x in c.split() for x in EXCL):
            return True
        a = a.getparent()
    return False


def url_for(path):
    """business/saying-no.html -> /business/saying-no ; projects/index.html -> /projects/"""
    rel = path.replace(os.sep, '/')[:-5]          # drop .html
    if rel.endswith('/index'):
        return '/' + rel[:-len('index')]
    return '/' + rel


chunks = []
files = [p for p in sorted(glob.glob('**/*.html', recursive=True))
         if not any(part in SKIP_DIRS for part in p.split(os.sep))]

for f in files:
    if os.path.basename(f) in SKIP:
        continue
    raw = open(f, encoding='utf-8').read()
    if NOINDEX.search(raw):
        continue
    t = html.parse(f)
    title = (t.xpath('//h1/text()') or [f])[0].strip()
    url = url_for(f)
    # Project pages, the survey and the directory use <section class="wrap read">,
    # so match on the class list rather than the whole attribute.
    body = (t.xpath('//article')
            or t.xpath('//section[contains(concat(" ", normalize-space(@class), " "), " wrap ")]'))
    if not body:
        continue
    cur_head = 'Overview'
    cur = []

    def flush():
        global cur
        txt = re.sub(r'\s+', ' ', ' '.join(cur)).strip().replace('(paid link)', '')
        if len(txt) > 80:
            while len(txt) > 2000:
                cut = txt.rfind('. ', 800, 2000)
                cut = cut + 1 if cut > 0 else 2000
                chunks.append({'u': url, 't': title, 'h': cur_head, 'x': txt[:cut].strip()})
                txt = txt[cut:].strip()
            chunks.append({'u': url, 't': title, 'h': cur_head, 'x': txt})
        cur = []

    for el in body[0].iter():
        if not isinstance(el.tag, str):
            continue
        # Each supplier listing is its own answer. Without this, all 59 run
        # together into a handful of 2000-character chunks and a search for
        # "horsehair" is competing against four unrelated companies in the
        # same block.
        if el.tag == 'li' and 'sup-item' in (el.get('class') or '').split():
            flush()
        if el.tag == 'h2':
            if not excluded(el):
                flush()
                cur_head = re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()
        elif el.tag == 'tr':
            # Tables were invisible to the index, which meant the thread size
            # chart, the needle pairing and the fire regulations occupancy table
            # — the actual reference data — could not be retrieved at all.
            # Flatten each row into a readable line using the data-l labels that
            # already exist for the mobile card layout, falling back to the
            # header row where a table has no labels.
            if excluded(el):
                continue
            parts = []
            for cell in el.iter():
                if not isinstance(cell.tag, str) or cell.tag not in ('td', 'th'):
                    continue
                val = re.sub(r'\s+', ' ', ''.join(cell.itertext())).strip()
                if not val:
                    continue
                lab = cell.get('data-l')
                if lab:
                    parts.append('%s: %s' % (lab.strip(), val))
                else:
                    parts.append(val)
            if parts:
                cur.append('; '.join(parts) + '.')
        elif el.tag in ('p', 'li', 'h3', 'h4', 'figcaption', 'dt', 'dd', 'summary'):
            if excluded(el):
                continue
            s = re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()
            if s:
                cur.append(s)
    flush()

seen = set()
dedup = []
for c in chunks:
    k = c['x'][:120]
    if k in seen:
        continue
    seen.add(k)
    dedup.append(c)

json.dump(dedup, open('ask-index.json', 'w'), ensure_ascii=False, separators=(',', ':'))

by_area = {}
for c in dedup:
    area = c['u'].split('/')[1] if c['u'].count('/') > 1 and c['u'].split('/')[1] else '(root)'
    area = area if area in ('business', 'projects', 'state-of-the-trade') else '(root)'
    by_area[area] = by_area.get(area, 0) + 1

print(len(dedup), 'chunks written to ask-index.json')
for k in sorted(by_area):
    print('   %-18s %d' % (k, by_area[k]))

#!/usr/bin/env python3
"""One-shot patch for the Start Here launch:
  1. Adds 'Start Here' to the nav on every page (root + /projects).
  2. Adds a ghost button to the homepage hero.
  3. Adds a beginner callout to the top of the contents page.
  4. Adds /start-here to sitemap.xml.
  5. Adds the entry to llms.txt (alphabetical by title).
  6. Appends a full entry to search-index.json.
Idempotent — safe to re-run."""
import glob, json, re, urllib.parse
from lxml import html as lx

NAV_MARK = '<li><a class="nav-cta" href="/contents">Contents</a></li>'
NAV_ADD  = NAV_MARK + '\n      <li><a href="/start-here">Start Here</a></li>'

# ---- 1. nav, sitewide -------------------------------------------------------
patched, skipped, missing = [], [], []
for f in sorted(glob.glob('*.html') + glob.glob('projects/*.html')):
    c = open(f).read()
    if 'href="/start-here"' in c and NAV_MARK + '\n      <li><a href="/start-here">' in c:
        skipped.append(f); continue
    if NAV_MARK not in c:
        missing.append(f); continue
    open(f, 'w').write(c.replace(NAV_MARK, NAV_ADD, 1))
    patched.append(f)
print(f'nav: patched {len(patched)}, already-done {len(skipped)}, no-marker {missing or "none"}')

# ---- 2. homepage hero button ------------------------------------------------
c = open('index.html').read()
btn = '<a class="btn btn-ghost" href="/start-here">New to this? Start here</a>'
if btn not in c:
    old = '<a class="btn btn-primary" href="/contents">Start reading &mdash; free</a>'
    if old not in c:
        old = '<a class="btn btn-primary" href="/contents">Start reading — free</a>'
    assert old in c, 'homepage hero button marker not found'
    c = c.replace(old, old + '\n      ' + btn, 1)
    open('index.html', 'w').write(c)
    print('homepage: ghost button added')
else:
    print('homepage: already has button')

# ---- 3. contents callout ----------------------------------------------------
c = open('contents.html').read()
callout = ('<div class="sidenote" style="background:#fff;border:1px solid var(--rule);'
           'border-left:4px solid var(--gold);margin-top:1.6rem">\n'
           '    <span class="tag">First time here?</span>\n'
           '    <p>Don&#8217;t read front-to-back. <a href="/start-here"><strong>Follow the '
           'Start Here path</strong></a> &mdash; the exact order we give beginners: what to '
           'buy, what to read, and your first finished seat in about four hours at the bench.</p>\n'
           '  </div>')
if 'Follow the Start Here path' not in c:
    mark = '<div id="lu-reader-panel"></div>'
    assert mark in c, 'reader panel marker not found in contents'
    c = c.replace(mark, mark + '\n  ' + callout, 1)
    open('contents.html', 'w').write(c)
    print('contents: callout added')
else:
    print('contents: already has callout')

# ---- 4. sitemap -------------------------------------------------------------
c = open('sitemap.xml').read()
loc = '  <url><loc>https://www.learntoupholster.com/start-here</loc></url>\n'
if '/start-here<' not in c:
    mark = '  <url><loc>https://www.learntoupholster.com/contents</loc></url>\n'
    assert mark in c
    open('sitemap.xml', 'w').write(c.replace(mark, mark + loc, 1))
    print('sitemap: added')
else:
    print('sitemap: already present')

# ---- 5. llms.txt (alphabetical by title) ------------------------------------
c = open('llms.txt').read()
entry = ('- [Start Here — your first upholstery project, step by step]'
         '(https://www.learntoupholster.com/start-here): The beginner\u2019s path: why the '
         'drop-in dining seat comes first, the six tools and \u00a320 of materials to buy, '
         'the five stages in order, and the project ladder from first seat to Chesterfield.')
if '/start-here)' not in c:
    lines = c.split('\n')
    items = [(i, l) for i, l in enumerate(lines) if l.startswith('- [')]
    pos = None
    for i, l in items:
        title = l[3:l.index(']')]
        if title.lower() > 'start here':
            pos = i; break
    pos = pos if pos is not None else items[-1][0] + 1
    lines.insert(pos, entry)
    open('llms.txt', 'w').write('\n'.join(lines))
    print(f'llms.txt: inserted at line {pos+1}')
else:
    print('llms.txt: already present')

# ---- 6. search-index.json ---------------------------------------------------
idx = json.load(open('search-index.json'))
if not any(e['url'] == '/start-here' for e in idx):
    t = lx.parse('start-here.html')
    art = t.xpath('//article')[0]
    heads = [' '.join(''.join(h.itertext()).split())
             for h in art.xpath('.//h2') + art.xpath('.//ol[@class="path"]//h3')]
    body = ' '.join(' '.join(art.itertext()).split())
    affs = []
    seen = set()
    for a in art.xpath('.//a[@class="aff"]'):
        label = ' '.join(''.join(a.itertext()).split())
        q = urllib.parse.parse_qs(urllib.parse.urlparse(a.get('href')).query)
        url = q.get('u', [a.get('href')])[0]
        if label not in seen:
            affs.append({'label': label, 'url': url}); seen.add(label)
    idx.append({
        'url': '/start-here',
        'title': 'Start Here — Your First Upholstery Project',
        'chno': 'The beginner\u2019s path',
        'desc': ('The exact path we give every beginner: the drop-in dining seat — what to buy '
                 '(~\u00a350 of tools, \u00a320 of materials), what to read, and the five stages in order.'),
        'img': '/assets/gallery/43.jpg',
        'headings': heads,
        'aff': affs,
        'body': body,
    })
    json.dump(idx, open('search-index.json', 'w'), ensure_ascii=False, indent=1)
    print(f'search-index: appended ({len(heads)} headings, {len(affs)} aff links, {len(body)} chars body)')
else:
    print('search-index: already present')

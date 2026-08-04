#!/usr/bin/env python3
"""Build the blog from blog-sources/*.txt.

Generates:
  blog/<slug>.html            one page per source file
  blog/index.html             the hub, newest first, grouped by category
  blog/category/<slug>.html   one page per category

Also:
  - replaces "Buy the Book" in the main nav with a Blog dropdown on every page
    (Buy the Book moves into the Contents dropdown so it stays one click away)
  - adds every blog URL to sitemap.xml

Page shells are cloned from an existing live page so head, nav, footer and the
inlined CSS stay byte-identical. Reuses the existing biz-* classes, so no CSS
changes are needed. Idempotent.
"""
import os, re, glob, json, html, datetime

BASE = 'https://www.learntoupholster.com'
SRC = 'blog-sources'
OUT = 'blog'
TEMPLATE_CANDIDATES = [
    'business/uncollected-furniture.html',
    'business/saying-no-to-a-job.html',
    'business/charging-for-estimates.html',
]

BODY_START = '<header class="chapter-head">'
BODY_END_RE = re.compile(r'</article>\s*<aside class="ad-rail".*?</aside>\s*</div>', re.S)


# ---------------------------------------------------------------- source files

def parse_source(path):
    raw = open(path, encoding='utf-8').read()
    body = faq = tools = related = ''
    if '---BODY---' in raw:
        headpart, rest = raw.split('---BODY---', 1)
    else:
        headpart, rest = raw, ''
    for marker, name in (('---FAQ---', 'faq'), ('---TOOLS---', 'tools'), ('---RELATED---', 'related')):
        pass
    body = rest
    for marker in ('---FAQ---', '---TOOLS---', '---RELATED---'):
        if marker in body:
            body = body.split(marker)[0]
    faq = rest.split('---FAQ---', 1)[1].split('---TOOLS---')[0] if '---FAQ---' in rest else ''
    tools = rest.split('---TOOLS---', 1)[1].split('---RELATED---')[0] if '---TOOLS---' in rest else ''
    related = rest.split('---RELATED---', 1)[1] if '---RELATED---' in rest else ''

    meta = {}
    for line in headpart.splitlines():
        if ':' in line and not line.startswith(' '):
            k, v = line.split(':', 1)
            k = k.strip().lower()
            if k in ('title', 'description', 'category', 'category-slug', 'date',
                     'answer', 'answer-heading'):
                meta[k] = v.strip()

    meta['slug'] = os.path.basename(path)[:-4]
    meta['body'] = body.strip()
    meta['faq'] = parse_faq(faq)
    meta['tools'] = parse_links(tools)
    meta['related'] = parse_links(related)
    meta.setdefault('date', datetime.date.today().isoformat())
    meta.setdefault('category', 'General')
    meta.setdefault('category-slug', slugify(meta['category']))
    meta.setdefault('answer-heading', meta.get('title', ''))
    return meta


def slugify(s):
    s = s.lower().replace('&', 'and')
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def parse_faq(block):
    out, q, a = [], None, []
    for line in block.splitlines():
        if line.startswith('Q:'):
            if q:
                out.append((q, ' '.join(a).strip()))
            q, a = line[2:].strip(), []
        elif line.startswith('A:'):
            a = [line[2:].strip()]
        elif line.strip() and q and a:
            a.append(line.strip())
    if q:
        out.append((q, ' '.join(a).strip()))
    return out


def parse_links(block):
    out = []
    for line in block.splitlines():
        line = line.strip()
        if '|' in line:
            href, label = line.split('|', 1)
            out.append((href.strip(), label.strip()))
    return out


# ---------------------------------------------------------------- page shell

def get_shell():
    for c in TEMPLATE_CANDIDATES:
        if os.path.exists(c):
            return open(c, encoding='utf-8').read(), c
    raise SystemExit('!! no template page found - run from ~/learntoupholster')


def set_head(h, title, desc, url, og_type='article'):
    e = lambda s: html.escape(s, quote=True)
    h = re.sub(r'<title>.*?</title>', f'<title>{e(title)} | Learn to Upholster</title>', h, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content=".*?">',
               f'<meta name="description" content="{e(desc)}">', h, count=1, flags=re.S)
    h = re.sub(r'<link rel="canonical" href=".*?">',
               f'<link rel="canonical" href="{url}">', h, count=1, flags=re.S)
    h = re.sub(r'<meta property="og:title" content=".*?">',
               f'<meta property="og:title" content="{e(title)}">', h, count=1, flags=re.S)
    h = re.sub(r'<meta property="og:description" content=".*?">',
               f'<meta property="og:description" content="{e(desc)}">', h, count=1, flags=re.S)
    h = re.sub(r'<meta property="og:url" content=".*?">',
               f'<meta property="og:url" content="{url}">', h, count=1, flags=re.S)
    h = re.sub(r'<meta property="og:type" content=".*?">',
               f'<meta property="og:type" content="{og_type}">', h, count=1, flags=re.S)
    return h


def set_schema(h, blocks):
    h = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', '', h, flags=re.S)
    payload = ''.join('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False)
                      + '</script>\n' for b in blocks)
    return h.replace('</head>', payload + '</head>', 1)


def set_body(h, new_body):
    i = h.find(BODY_START)
    m = BODY_END_RE.search(h, i)
    if i < 0 or not m:
        raise SystemExit('!! could not locate the article region in the template page')
    return h[:i] + new_body + h[m.end():]


# ---------------------------------------------------------------- post pages

def render_post(p, shell):
    url = f'{BASE}/{OUT}/{p["slug"]}'
    e = lambda s: html.escape(s, quote=False)
    d = datetime.date.fromisoformat(p['date'])
    pretty = f'{d.day} {d.strftime("%B %Y")}'

    faq_html = ''
    if p['faq']:
        faq_html = '<div class="biz-faq"><h2>Common questions</h2>' + ''.join(
            f'<h3>{e(q)}</h3><p>{e(a)}</p>' for q, a in p['faq']) + '</div>'

    tools_html = ''
    if p['tools']:
        tools_html = '<div class="biz-tools"><h2>Tools for this</h2><ul>' + ''.join(
            f'<li><a href="{href}">{e(l)}</a></li>' for href, l in p['tools']) + '</ul></div>'

    rel_html = ''
    if p['related']:
        rel_html = '<div class="biz-related"><h2>Also worth reading</h2><ul>' + ''.join(
            f'<li><a href="{href}">{e(l)}</a></li>' for href, l in p['related']) + '</ul></div>'

    body = f'''<header class="chapter-head">
  <div class="wrap">
    <p class="chno">Blog · {e(p['category'])}</p>
    <h1>{e(p['title'])}</h1>
    <p class="updated">Last updated: <time datetime="{p['date']}">{pretty}</time></p>
  </div>
</header>

<hr class="seam">

<div class="page-cols">
<article class="article wrap read">
  <p class="biz-crumb"><a href="/{OUT}/">Blog</a> · <a href="/{OUT}/category/{p['category-slug']}">{e(p['category'])}</a></p>
  <div class="biz-answer" id="answer">
    <h2>{e(p['answer-heading'])}</h2>
    <p>{e(p['answer'])}</p>
  </div>
{p['body']}
{faq_html}{tools_html}{rel_html}</article>
<aside class="ad-rail" id="mv-sidebar" aria-hidden="true"></aside>
</div>'''

    article = {
        "@type": "Article", "@id": url + "#article",
        "headline": p['title'], "description": p['description'], "url": url,
        "datePublished": p['date'], "dateModified": p['date'], "inLanguage": "en",
        "articleSection": p['category'],
        "author": {"@type": "Person", "@id": f"{BASE}/about#shaun", "name": "Shaun Greenwood"},
        "publisher": {"@type": "Organization", "@id": f"{BASE}#org", "name": "Learn to Upholster"},
    }
    crumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Learn to Upholster", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{BASE}/{OUT}/"},
            {"@type": "ListItem", "position": 3, "name": p['category'],
             "item": f"{BASE}/{OUT}/category/{p['category-slug']}"},
            {"@type": "ListItem", "position": 4, "name": p['title'], "item": url},
        ]
    }
    graph = [article, crumbs]
    if p['faq']:
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p['faq']]
        })
    schema = [{"@context": "https://schema.org", "@graph": graph}]

    h = set_head(shell, p['title'], p['description'], url)
    h = set_schema(h, schema)
    h = set_body(h, body)
    return h


# ---------------------------------------------------------------- hub + cats

def write_md(p):
    """Emit md/blog/<slug>.md so build-llms.py picks the post up.
    build-md.py only scans the site root, so blog pages would otherwise never
    reach llms.txt or llms-full.txt."""
    os.makedirs(f'md/{OUT}', exist_ok=True)
    url = f'{BASE}/{OUT}/{p["slug"]}'
    txt = re.sub(r'<(script|style).*?</\1>', '', p['body'], flags=re.S)
    txt = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', txt, flags=re.S)
    txt = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', txt, flags=re.S)
    txt = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', txt, flags=re.S)
    txt = re.sub(r'</p>', '\n\n', txt)
    txt = re.sub(r'<[^>]+>', '', txt)
    txt = html.unescape(txt)
    txt = re.sub(r'\n{3,}', '\n\n', txt).strip()

    faq = ''
    if p['faq']:
        faq = '\n\n## Common questions\n\n' + '\n\n'.join(
            f'### {q}\n\n{a}' for q, a in p['faq'])

    out = (f'# {p["title"]}\n\n*Blog · {p["category"]}*\n\n> {p["description"]}\n\n'
           f'Canonical: {url}\n\n## {p["answer-heading"]}\n\n{p["answer"]}\n\n{txt}{faq}\n')
    open(f'md/{OUT}/{p["slug"]}.md', 'w', encoding='utf-8').write(out)


def render_listing(shell, title, desc, url, heading, eyebrow, groups):
    e = lambda s: html.escape(s, quote=False)
    sections = ''
    for cat, posts in groups:
        sections += f'<h2>{e(cat)}</h2><ul class="blog-list">' if cat else '<ul class="blog-list">'
        for p in posts:
            d = datetime.date.fromisoformat(p['date'])
            sections += (f'<li><a href="/{OUT}/{p["slug"]}"><strong>{e(p["title"])}</strong></a>'
                         f'<br><span class="foot-small">{e(p["description"])}</span>'
                         f'<br><span class="foot-note"><time datetime="{p["date"]}">'
                         f'{d.day} {d.strftime("%B %Y")}</time></span></li>')
        sections += '</ul>'

    body = f'''<header class="chapter-head">
  <div class="wrap">
    <p class="chno">{e(eyebrow)}</p>
    <h1>{e(heading)}</h1>
  </div>
</header>

<hr class="seam">

<div class="page-cols">
<article class="article wrap read">
  <p>{e(desc)}</p>
{sections}</article>
<aside class="ad-rail" id="mv-sidebar" aria-hidden="true"></aside>
</div>'''

    schema = [{"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url + "#page", "name": heading,
         "description": desc, "url": url, "inLanguage": "en",
         "publisher": {"@type": "Organization", "@id": f"{BASE}#org", "name": "Learn to Upholster"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Learn to Upholster", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": heading, "item": url}]},
    ]}]
    h = set_head(shell, title, desc, url, og_type='website')
    h = set_schema(h, schema)
    return set_body(h, body)


# ---------------------------------------------------------------- nav

def build_nav_block(cats):
    items = f'          <li><a href="/{OUT}/">All posts</a></li>\n'
    for cat, cslug in cats:
        items += f'          <li><a href="/{OUT}/category/{cslug}">{html.escape(cat, quote=False)}</a></li>\n'
    return (f'      <li class="has-sub"><a href="/{OUT}/">Blog</a>\n'
            f'        <ul class="sub-menu">\n{items}        </ul>\n'
            f'      </li>')


def patch_nav(cats):
    block = build_nav_block(cats)
    files = sorted(set(glob.glob('*.html') + glob.glob('*/*.html') + glob.glob('*/*/*.html')))
    changed = 0
    for f in files:
        h = open(f, encoding='utf-8', errors='ignore').read()
        orig = h

        # Remove any previously generated Blog dropdown so re-runs stay clean.
        # Must span the whole <ul class="sub-menu">...</ul> or it leaves fragments.
        h = re.sub(r'\s*<li class="has-sub"><a href="/blog/">Blog</a>\s*'
                   r'<ul class="sub-menu">.*?</ul>\s*</li>', '', h, flags=re.S)

        # Buy the Book moves into the Contents dropdown, if it isn't already there.
        if '<li><a href="/buy-the-book">Buy the Book</a></li>' in h:
            h = h.replace('<li><a href="/buy-the-book">Buy the Book</a></li>', '', 1)
            if 'sub-menu' in h and '/buy-the-book">Buy the Book</a></li>' not in h:
                h = h.replace('<li><a href="/a-z-glossary">A–Z glossary</a></li>',
                              '<li><a href="/a-z-glossary">A–Z glossary</a></li>\n'
                              '          <li><a href="/buy-the-book">Buy the Book</a></li>', 1)

        # Insert the Blog dropdown just before Projects.
        if '<li class="has-sub"><a href="/blog/">Blog</a>' not in h:
            h = h.replace('      <li><a href="/projects/">Projects</a></li>',
                          block + '\n      <li><a href="/projects/">Projects</a></li>', 1)

        h = re.sub(r'\n[ \t]+\n', '\n', h)
        h = re.sub(r'\n{3,}', '\n\n', h)
        if h != orig:
            open(f, 'w', encoding='utf-8').write(h)
            changed += 1
    return changed


# ---------------------------------------------------------------- sitemap

def patch_sitemap(urls_dates):
    SM = 'sitemap.xml'
    if not os.path.exists(SM):
        print('   sitemap.xml not found - skipped')
        return
    xml = open(SM, encoding='utf-8').read()
    added = 0
    entries = []
    for url, date in urls_dates:
        if f'<loc>{url}</loc>' in xml:
            continue
        entries.append(f'  <url><loc>{url}</loc><lastmod>{date}</lastmod></url>')
        added += 1
    if entries:
        xml = xml.replace('</urlset>', '\n'.join(entries) + '\n</urlset>')
        open(SM, 'w', encoding='utf-8').write(xml)
    print(f'   sitemap.xml: {added} blog URL(s) added')


# ---------------------------------------------------------------- main

def main():
    if not os.path.isdir(SRC):
        raise SystemExit(f'!! {SRC}/ not found - run from ~/learntoupholster')

    shell, tpl = get_shell()
    print(f'template shell: {tpl}')

    posts = [parse_source(f) for f in sorted(glob.glob(f'{SRC}/*.txt'))]
    if not posts:
        raise SystemExit(f'!! no source files in {SRC}/')
    posts.sort(key=lambda p: p['date'], reverse=True)

    os.makedirs(OUT, exist_ok=True)
    os.makedirs(f'{OUT}/category', exist_ok=True)

    for p in posts:
        open(f'{OUT}/{p["slug"]}.html', 'w', encoding='utf-8').write(render_post(p, shell))
        write_md(p)
        print(f'  built /{OUT}/{p["slug"]}  ({p["category"]}, {len(p["faq"])} FAQs)')

    # categories, in order of first appearance
    cats, seen = [], set()
    for p in posts:
        if p['category-slug'] not in seen:
            seen.add(p['category-slug'])
            cats.append((p['category'], p['category-slug']))

    groups = [(c, [p for p in posts if p['category-slug'] == cs]) for c, cs in cats]
    hub = render_listing(
        shell, 'Blog',
        'Notes from the workshop bench: materials, problems, and the questions customers actually ask.',
        f'{BASE}/{OUT}/', 'Blog', 'Learn to Upholster', groups)
    open(f'{OUT}/index.html', 'w', encoding='utf-8').write(hub)
    print(f'  built /{OUT}/ hub ({len(posts)} posts, {len(cats)} categor{"y" if len(cats)==1 else "ies"})')

    for cat, cslug in cats:
        cp = [p for p in posts if p['category-slug'] == cslug]
        page = render_listing(
            shell, cat, f'Blog posts on {cat.lower()} from a working upholsterer\u2019s bench.',
            f'{BASE}/{OUT}/category/{cslug}', cat, 'Blog', [(None, cp)])
        open(f'{OUT}/category/{cslug}.html', 'w', encoding='utf-8').write(page)
        print(f'  built /{OUT}/category/{cslug}  ({len(cp)} post(s))')

    changed = patch_nav(cats)
    print(f'   nav updated on {changed} page(s): Buy the Book -> Blog dropdown')

    urls = [(f'{BASE}/{OUT}/', posts[0]['date'])]
    urls += [(f'{BASE}/{OUT}/{p["slug"]}', p['date']) for p in posts]
    urls += [(f'{BASE}/{OUT}/category/{cs}', max(p['date'] for p in posts if p['category-slug'] == cs))
             for _, cs in cats]
    patch_sitemap(urls)
    print('done.')


if __name__ == '__main__':
    main()

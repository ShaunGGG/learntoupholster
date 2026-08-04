#!/usr/bin/env python3
"""
build-business.py — build the Business Hub from plain text sources.

    business-sources/<slug>.txt   ->   business/<slug>.html
                                       business/index.html (hub, rebuilt)

Source format — front matter, blank line, body:

    title: I'm busy but I'm not making money
    question: Why am I fully booked and still broke?
    answer: 60-110 words. Becomes the answer block and the hub summary.
    section: Problems Nobody Talks About
    order: 20
    updated: 2026-07-31
    related: /pricing-and-quoting, /customers-and-the-workshop-year
    tools: /reupholstery-cost-calculator, /fabric-yardage

Body markup: ## and ### headings, paragraphs, - bullets, 1. lists, > asides,
**bold**, *italic*, [links](/url), `code`. Raw HTML passes through.

Page chrome comes from an existing chapter page at build time, so the Hub
follows the rest of the site automatically. The chapter header block is
regenerated rather than inherited — inheriting it is how every Business Hub
page ended up with an <h1> reading "Webbing".
"""

import os, re, sys, glob, html, datetime

SRC_DIR = 'business-sources'
OUT_DIR = 'business'
CHROME_FROM = 'webbing.html'
SITE = 'https://www.learntoupholster.com'
OG_DEFAULT = SITE + '/assets/og-card.jpg'
PRO_URL = 'https://pro.learntoupholster.com/'

SECTION_ORDER = [
    'Starting Out', 'Pricing & Profit', 'Quoting Jobs', 'Getting Customers',
    'Dealing With Customers', 'Running the Workshop', 'Money & Finance',
    'Working With the Trade', 'Growing the Business', 'Problems Nobody Talks About',
    'Templates & Documents',
]

# Every calculator on the site, with the reason a working upholsterer opens it.
TOOLS = [
    ('/reupholstery-cost-calculator', 'Cost estimator',
     'Labour, materials and contingency for a job, split modern or traditional. Start here when quoting.'),
    ('/fabric-yardage', 'Fabric calculator',
     'Metres and yards by piece or from measured panels. Handles roll width and pattern repeat.'),
    ('/leather-hide-calculator', 'Leather hide calculator',
     'Hides rather than metres, with the uplift for aniline finishes and buttoning.'),
    ('/foam-cushion-calculator', 'Foam & cushion spec',
     'Density, hardness, thickness and the fire grade. Keeps density and firmness apart.'),
    ('/deep-buttoning-calculator', 'Deep-buttoning calculator',
     'Button count, base grid, fabric grid and cut size. The two grids are never the same.'),
    ('/box-cushion-calculator', 'Box cushion cutting plan',
     'Cutting list for boxed cushions, panels and gussets.'),
    ('/piping-calculator', 'Piping & bias strips',
     'How much bias to cut, and how much cloth that eats.'),
    ('/fire-safety-checker', 'Fire regulations checker',
     'UK compliance for domestic and contract work, including BS 7176 hazard categories.'),
    ('/invoice-template', 'Invoice & quote template',
     'Printable quote and invoice you can put your own details on.'),
    ('/fabric-visualiser', 'Fabric visualiser',
     'Show a customer their own chair in a different cloth before they commit.'),
    ('/workshop-forms', 'Workshop forms',
     'Enquiry, condition report, job sheet and delivery note. Print-ready, no download.'),
    ('/suppliers', 'Supplier directory',
     'Where to buy materials, by country. Verified, and nobody pays to be listed.'),
]

HUB_INTRO = ("Free resources for working upholsterers and anyone thinking of going professional. "
             "The rest of this site teaches the craft. This part is about making a living from it: "
             "what to charge, how to quote, how to keep a workshop solvent, and the awkward "
             "situations nobody warns you about.")

HUB_CAVEAT = ('<div class="sidenote" style="background:#fff;border:1px solid var(--rule);'
              'border-left:4px solid var(--gold);margin-top:1.6rem">\n'
              '    <span class="tag">Before you start</span>\n'
              '    <p>This is an international resource, and tax, insurance and employment law '
              'differ everywhere. Where a topic turns on them you will find the general principle '
              'and a link to the official source for your country \u2014 never a figure. Nothing '
              'here is legal, tax or financial advice.</p>\n  </div>')

NUMERALS = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
            'Nine', 'Ten', 'Eleven', 'Twelve']

# Shaun's own products. These are the honest monetisation route for business
# content: relevant, high-value, and no disclosure problem because they are his.
PRODUCTS = {
    'book': ('/buy-the-book', 'The Working Upholsterer\u2019s Bible',
             'The whole reference in print \u2014 35 chapters, 72 figures, and a wiro-bound '
             'workshop edition that lies flat on the bench. From \u00a39.99.'),
    'pro': (PRO_URL, 'Visualiser Pro',
            'Show a customer their own chair in the fabric they are considering, from a photo. '
            '\u00a339.99 for 100 images, no account or subscription.'),
    'bodella': ('https://bodella.co.uk/', 'Bodella fabrics',
                'Our own upholstery fabric shop \u2014 ranges, samples and trade-priced cloth.'),
}

AMAZON_TAG = '842699-21'

AFFIL_DISCLOSURE = (
    '<p class="biz-disclosure">Some links on this page are Amazon affiliate links. '
    'If you buy through one, this site earns a small commission at no extra cost to you. '
    'It does not affect what gets recommended \u2014 the tools listed are the ones actually '
    'used at the bench.</p>')


def amazon_link(query):
    from urllib.parse import quote
    return '/go/amazon?q=%s&u=%s' % (
        quote(query),
        quote('https://www.amazon.co.uk/s?k=%s&tag=%s' % (quote(query), AMAZON_TAG), safe=''))



SURVEY_BLOCK = ('<div class="biz-survey">\n'
                '  <h2>State of the Upholstery Trade</h2>\n'
                '  <p>There is no reliable public data on what this work is worth. Rates get passed '
                'around as rumour and new workshops price from guesswork. So we are collecting it: '
                'shop rates, bench hours by piece, fabric markup, lead times, and which work actually '
                'pays \u2014 from working upholsterers, in every country.</p>\n'
                '  <p>Anonymous, thirteen questions, about three minutes. No name, no email address. '
                'Nothing publishes until thirty workshops have answered, and the results are free for '
                'anyone to read or cite.</p>\n'
                '  <p><a class="biz-survey-cta" href="/state-of-the-trade/take-part">Add your workshop '
                'to the data</a> <a class="biz-survey-alt" href="/state-of-the-trade/">See the results '
                'so far</a></p>\n'
                '</div>')

PRO_BLOCK = ('<div class="biz-pro">\n'
             '  <h2>Visualiser Pro</h2>\n'
             '  <p>The hardest part of selling reupholstery is that the customer cannot picture it. '
             'Visualiser Pro puts <em>their</em> chair in the fabric they are considering, from a photo, '
             'so the conversation stops being hypothetical. Useful at the quoting stage, when a customer '
             'is hesitating between three cloths and will not commit to any of them.</p>\n'
             '  <p class="biz-pro-price"><a class="btn" href="%s">Visualiser Pro \u2014 \u00a339.99 for 100 images</a> '
             '<span>No account, no subscription.</span></p>\n'
             '</div>' % PRO_URL)


# ---------------------------------------------------------------- parsing


def meta_desc(text, limit=155):
    """Trim to a search-result-sized description at a sentence or word break.

    The answer blocks run 60-110 words, and using the first 300 characters of one
    produced descriptions twice as long as a search result will show. Cutting at
    a sentence boundary keeps them readable rather than ending mid-clause.
    """
    t = ' '.join(str(text).split())
    if len(t) <= limit:
        return t
    cut = t[:limit]
    stop = max(cut.rfind('. '), cut.rfind('? '), cut.rfind('! '))
    if stop > limit * 0.55:
        return cut[:stop + 1]
    sp = cut.rfind(' ')
    return (cut[:sp] if sp > 0 else cut).rstrip(',;:') + '\u2026'

def parse_source(path):
    raw = open(path, encoding='utf-8').read().replace('\r\n', '\n')
    parts = raw.split('\n\n', 1)
    head, body = parts[0], (parts[1] if len(parts) > 1 else '')
    meta, key = {}, None
    for line in head.split('\n'):
        m = re.match(r'^([a-z_]+):\s*(.*)$', line)
        if m:
            key = m.group(1); meta[key] = m.group(2).strip()
        elif key and line.startswith((' ', '\t')):
            meta[key] += ' ' + line.strip()
    return meta, body.strip()


def md(text):
    out, lines, i = [], text.split('\n'), 0

    def inline(s):
        s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', s)
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
        return s

    while i < len(lines):
        ln = lines[i]; s = ln.strip()
        if not s:
            i += 1; continue
        if s.startswith('<'):
            out.append(ln); i += 1; continue
        m = re.match(r'^(#{2,4})\s+(.*)$', s)
        if m:
            lvl = len(m.group(1))
            out.append('<h%d>%s</h%d>' % (lvl, inline(html.escape(m.group(2))), lvl)); i += 1; continue
        if s.startswith('> '):
            blk = []
            while i < len(lines) and lines[i].strip().startswith('> '):
                blk.append(inline(html.escape(lines[i].strip()[2:]))); i += 1
            out.append('<blockquote class="biz-aside"><p>%s</p></blockquote>' % ' '.join(blk)); continue
        if re.match(r'^[-*]\s+', s):
            it = []
            while i < len(lines) and re.match(r'^[-*]\s+', lines[i].strip()):
                it.append('<li>%s</li>' % inline(html.escape(re.sub(r'^[-*]\s+', '', lines[i].strip())))); i += 1
            out.append('<ul>%s</ul>' % ''.join(it)); continue
        if re.match(r'^\d+\.\s+', s):
            it = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                it.append('<li>%s</li>' % inline(html.escape(re.sub(r'^\d+\.\s+', '', lines[i].strip())))); i += 1
            out.append('<ol>%s</ol>' % ''.join(it)); continue
        para = []
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#', '>', '<')) \
                and not re.match(r'^([-*]|\d+\.)\s+', lines[i].strip()):
            para.append(lines[i].strip()); i += 1
        out.append('<p>%s</p>' % inline(html.escape(' '.join(para))))
    return '\n'.join(out)


# ---------------------------------------------------------------- chrome

def get_chrome():
    """Split a chapter page into pre-header / post-header / tail.

    The chapter header is deliberately excluded from the inherited chrome and
    rebuilt per page. Inheriting it gave every Hub page a heading of "Webbing",
    a chapter number and someone else's epigraph.
    """
    if not os.path.exists(CHROME_FROM):
        sys.exit('Cannot find %s to use as the page template.' % CHROME_FROM)
    h = open(CHROME_FROM, encoding='utf-8').read()

    art = re.search(r'<article[^>]*>.*?</article>', h, re.S)
    if not art:
        sys.exit('No <article> found in %s.' % CHROME_FROM)

    hdr = re.search(r'<header class="chapter-head">.*?</header>', h, re.S)
    tail = h[art.end():]

    # The tail carries the source chapter's "Keep reading" links. Left alone,
    # every Business Hub page invites the reader on to Springing — Traditional.
    hub_links = ('<div class="related">\n'
                 '    <a href="/business/"><span class="dir">Business Hub</span><br>'
                 '<span class="ttl">All business articles \u2192</span></a>\n'
                 '    <a href="/contents"><span class="dir">Contents</span><br>'
                 '<span class="ttl">All chapters \u2192</span></a>\n  </div>')
    tail, n = re.subn(r'<div class="related">.*?</div>', lambda _m: hub_links, tail, count=1, flags=re.S)
    if not n:
        print('  note: no "Keep reading" block found in the template tail — nothing to rewrite.')

    if hdr and hdr.end() <= art.start():
        return h[:hdr.start()], h[hdr.end():art.start()], tail
    # Fallback: no chapter header in the template.
    return h[:art.start()], '', tail


def page_header(title, kicker, updated):
    return ('<header class="chapter-head">\n  <div class="wrap">\n'
            '    <p class="chno">%s</p>\n    <h1>%s</h1>\n'
            '    <p class="updated">Last updated: <time datetime="%s">%s</time></p>\n'
            '  </div>\n</header>' % (html.escape(kicker), html.escape(title), updated,
                                     datetime.date.fromisoformat(updated).strftime('%-d %B %Y')))


def swap_head(head, title, desc, url, image=OG_DEFAULT):
    def sub(pattern, value, s):
        return re.sub(pattern, lambda m: m.group(1) + value + m.group(2), s, count=1)

    head = re.sub(r'<title>.*?</title>',
                  lambda _m: '<title>%s | Learn to Upholster</title>' % html.escape(title),
                  head, count=1, flags=re.S)
    for attr, val in (('name="description"', html.escape(desc)),
                      ('property="og:title"', html.escape(title)),
                      ('property="og:description"', html.escape(desc)),
                      ('property="og:url"', url),
                      ('property="og:image"', image),
                      ('name="twitter:title"', html.escape(title)),
                      ('name="twitter:description"', html.escape(desc)),
                      ('name="twitter:image"', image)):
        head = sub(r'(<meta\s+' + attr + r'\s+content=")(?:[^"]*)(")', val, head)
    head = sub(r'(<link\s+rel="canonical"\s+href=")(?:[^"]*)(")', url, head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', head, flags=re.S)
    return head


def schema(a):
    esc = lambda s: (s or '').replace('\\', '\\\\').replace('"', '\\"')
    return ('<script type="application/ld+json">\n{"@context":"https://schema.org","@graph":['
            '{"@type":"Article","@id":"%s#article","headline":"%s","description":"%s","url":"%s",'
            '"dateModified":"%s","inLanguage":"en",'
            '"author":{"@type":"Person","@id":"%s/about#shaun","name":"Shaun Greenwood"},'
            '"publisher":{"@type":"Organization","@id":"%s#org","name":"Learn to Upholster"},'
            '"isPartOf":{"@type":"WebPage","@id":"%s/business/#hub","name":"Business Hub"}},'
            '{"@type":"FAQPage","@id":"%s#faq","mainEntity":[{"@type":"Question","name":"%s",'
            '"acceptedAnswer":{"@type":"Answer","text":"%s"}}]},'
            '{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
            '{"@type":"ListItem","position":2,"name":"Business Hub","item":"%s/business/"},'
            '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}]}\n</script>'
            % (a['url'], esc(a['title']), esc(a['answer'][:300]), a['url'], a['updated'],
               SITE, SITE, SITE, a['url'], esc(a['question']), esc(a['answer']),
               SITE, SITE, esc(a['title']), a['url']))


CSS = """<style>
.biz-answer{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--gold);
  padding:1.1rem 1.3rem;margin:0 0 1.8rem;border-radius:3px}
.biz-answer h2{font-family:var(--display);font-size:1.24rem;margin:0 0 .5rem;color:var(--green-deep);font-weight:600}
.biz-answer p{margin:0;font-size:1.06rem;line-height:1.55}
.biz-aside{border-left:3px solid var(--sage);margin:1.4rem 0;padding:.2rem 0 .2rem 1.1rem;font-style:italic}
.biz-crumb{font-size:.92rem;margin:0 0 1.2rem}
.biz-related,.biz-tools{background:var(--cream-deep);border-radius:3px;padding:1rem 1.2rem;margin:1.6rem 0 0}
.biz-related h2,.biz-tools h2{font-size:1.05rem;margin:0 0 .5rem;font-family:var(--display)}
.biz-related ul,.biz-tools ul{margin:0;padding-left:1.1rem}
.biz-caveat{background:var(--cream-deep);border-left:3px solid var(--terracotta);
  padding:.9rem 1.1rem;border-radius:3px;font-size:.97rem;margin:1.6rem 0}
.biz-section{margin:2.4rem 0 0}
.biz-section h2{font-family:var(--display);color:var(--green-deep);font-size:1.4rem;
  border-bottom:1px solid var(--rule);padding-bottom:.35rem}
.biz-list{list-style:none;padding:0;margin:1rem 0 0}
.biz-list li{padding:.75rem 0;border-bottom:1px solid var(--rule)}
.biz-list a{font-weight:600;text-decoration:none}
.biz-list p{margin:.25rem 0 0;font-size:.97rem}
.biz-toolgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:.9rem;margin:1rem 0 0}
.biz-toolgrid a{display:block;background:#fff;border:1px solid var(--rule);border-radius:3px;
  padding:.8rem .9rem;text-decoration:none}
.biz-toolgrid strong{display:block;font-family:var(--display);color:var(--green-deep);margin-bottom:.2rem}
.biz-toolgrid span{font-size:.93rem}
.biz-pro{background:var(--green-deep);color:var(--cream);border-radius:3px;padding:1.3rem 1.5rem;margin:2rem 0 0}
.biz-pro h2{font-family:var(--display);color:var(--gold);margin:0 0 .5rem;font-size:1.3rem;border:0}
.biz-pro p{margin:0 0 .7rem}
.biz-pro a.btn{display:inline-block;background:var(--gold);color:#22382C;font-weight:600;
  padding:.55rem 1.1rem;border-radius:3px;text-decoration:none}
.biz-pro-price span{display:inline-block;margin-left:.6rem;font-size:.92rem;opacity:.85}
.biz-kit{background:var(--cream-deep);border-radius:3px;padding:1rem 1.2rem;margin:1.6rem 0 0}
.biz-kit h2{font-size:1.05rem;margin:0 0 .5rem;font-family:var(--display)}
.biz-kit ul{margin:0 0 .7rem;padding-left:1.1rem}
.biz-disclosure{font-size:.87rem;margin:0;opacity:.8;border-top:1px solid var(--rule);padding-top:.6rem}
.biz-survey{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--sage);
  border-radius:3px;padding:1.2rem 1.4rem;margin:1.6rem 0 0}
.biz-survey h2{font-family:var(--display);color:var(--green-deep);margin:0 0 .5rem;font-size:1.3rem;border:0}
.biz-survey p{margin:0 0 .7rem}
.biz-survey-cta{display:inline-block;background:var(--green-deep);color:var(--cream);font-weight:600;
  padding:.55rem 1.1rem;border-radius:3px;text-decoration:none;margin-right:.7rem}
.biz-survey-alt{font-size:.95rem}
.biz-footnote{border-top:1px solid var(--rule);margin:2rem 0 0;padding-top:1rem;font-size:.97rem}
</style>"""


# ---------------------------------------------------------------- build


def hub_schema(articles, ordered, by_section):
    esc = lambda t: (t or '').replace('\\', '\\\\').replace('"', '\\"')
    items = []
    n = 0
    for sec in ordered:
        for a in sorted(by_section[sec], key=lambda x: (x['order'], x['title'])):
            n += 1
            items.append('{"@type":"ListItem","position":%d,"url":"%s","name":"%s"}'
                         % (n, a['url'], esc(a['title'])))
    return ('<script type="application/ld+json">\n'
            '{"@context":"https://schema.org","@graph":['
            '{"@type":"CollectionPage","@id":"%s/business/#hub",'
            '"name":"Business Hub","url":"%s/business/",'
            '"description":"Free resources for working upholsterers: pricing, quoting, '
            'finding customers, running a workshop and making a living from the craft.",'
            '"inLanguage":"en",'
            '"author":{"@type":"Person","@id":"%s/about#shaun","name":"Shaun Greenwood"},'
            '"publisher":{"@type":"Organization","@id":"%s#org","name":"Learn to Upholster"},'
            '"mainEntity":{"@type":"ItemList","numberOfItems":%d,"itemListElement":[%s]}},'
            '{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
            '{"@type":"ListItem","position":2,"name":"Business Hub","item":"%s/business/"}]}]}\n'
            '</script>' % (SITE, SITE, SITE, SITE, n, ','.join(items), SITE, SITE))


def tool_part():
    items = ''.join('<li><a href="%s">%s <span class="tag-live">Free</span></a></li>'
                    % (u, html.escape(n)) for u, n, _ in TOOLS)
    return ('<div class="toc-part" id="tools">\n'
            '    <span class="pn">Tools</span><h2>Calculators for the trade</h2>\n'
            '    <p>Every calculator on the site. Free, no account, and the same figures '
            'the <a href="/use-in-ai">MCP server</a> returns.</p>\n'
            '    <ul class="toc-list">%s</ul>\n  </div>' % items)


def main():
    if not os.path.isdir(SRC_DIR):
        os.makedirs(SRC_DIR)
        print('Created %s/ — put article sources in there and run again.' % SRC_DIR); return
    os.makedirs(OUT_DIR, exist_ok=True)

    pre, mid, tail = get_chrome()
    tool_names = {u: n for u, n, _ in TOOLS}
    articles, skipped = [], []

    for path in sorted(glob.glob(os.path.join(SRC_DIR, '*.txt'))):
        slug = os.path.splitext(os.path.basename(path))[0]
        meta, body = parse_source(path)
        missing = [k for k in ('title', 'question', 'answer', 'section') if not meta.get(k)]
        if missing:
            skipped.append('%s (missing: %s)' % (slug, ', '.join(missing))); continue
        articles.append({
            'slug': slug, 'title': meta['title'], 'question': meta['question'],
            'answer': meta['answer'], 'section': meta['section'],
            'order': int(meta.get('order') or 50),
            'updated': meta.get('updated') or datetime.date.today().isoformat(),
            'related': [r.strip() for r in (meta.get('related') or '').split(',') if r.strip()],
            'tools': [t.strip() for t in (meta.get('tools') or '').split(',') if t.strip()],
            'products': [p.strip() for p in (meta.get('products') or '').split(',') if p.strip()],
            'affiliate': [a.strip() for a in (meta.get('affiliate') or '').split(',') if a.strip()],
            'url': '%s/%s/%s' % (SITE, OUT_DIR, slug), 'body': md(body),
        })

    for a in articles:
        extras = ''
        if a['tools']:
            items = ''.join('<li><a href="%s">%s</a></li>' % (t, html.escape(tool_names.get(t, t.strip('/').replace('-', ' ').capitalize())))
                            for t in a['tools'])
            extras += '<div class="biz-tools"><h2>Tools for this</h2><ul>%s</ul></div>' % items
        if a['related']:
            items = ''.join('<li><a href="%s">%s</a></li>' % (r, r.strip('/').split('/')[-1].replace('-', ' ').capitalize())
                            for r in a['related'])
            extras += '<div class="biz-related"><h2>Also worth reading</h2><ul>%s</ul></div>' % items
        if a['affiliate']:
            rows = []
            for item in a['affiliate']:
                label, _, query = item.partition('|')
                query = (query or label).strip()
                rows.append('<li><a href="%s" rel="sponsored nofollow">%s</a></li>'
                            % (html.escape(amazon_link(query)), html.escape(label.strip())))
            extras += ('<div class="biz-kit"><h2>Kit for this</h2><ul>%s</ul>%s</div>'
                       % (''.join(rows), AFFIL_DISCLOSURE))
        if a['products']:
            cards = []
            for key in a['products']:
                if key not in PRODUCTS:
                    continue
                url, name, blurb = PRODUCTS[key]
                cards.append('<a href="%s"><strong>%s</strong><span>%s</span></a>'
                             % (url, html.escape(name), html.escape(blurb)))
            if cards:
                extras += ('<div class="biz-section"><h2>From Learn to Upholster</h2>'
                           '<div class="biz-toolgrid">%s</div></div>' % ''.join(cards))

        extras += ('<div class="biz-footnote"><p><strong>Do you work at the bench?</strong> '
                   'The <a href="/state-of-the-trade/">State of the Upholstery Trade</a> survey collects '
                   'rates, bench hours and lead times from working upholsterers worldwide, so the next '
                   'person setting a price has something better than guesswork. Anonymous, about three '
                   'minutes. <a href="/state-of-the-trade/take-part">Add your workshop</a>.</p></div>')

        art = ('<article class="article wrap read">\n'
               '  <p class="biz-crumb"><a href="/business/">Business Hub</a> \u00b7 %s</p>\n'
               '  <div class="biz-answer" id="answer">\n    <h2>%s</h2>\n    <p>%s</p>\n  </div>\n'
               '  %s\n  %s\n</article>'
               % (html.escape(a['section']), html.escape(a['question']),
                  html.escape(a['answer']), a['body'], extras))

        page = swap_head(pre, a['title'], meta_desc(a['answer']), a['url'])
        page = page.replace('</head>', CSS + '\n' + schema(a) + '\n</head>', 1)
        page += page_header(a['title'], 'Business Hub \u00b7 ' + a['section'], a['updated'])
        open(os.path.join(OUT_DIR, a['slug'] + '.html'), 'w', encoding='utf-8').write(page + mid + art + tail)

    # ---- hub
    by_section = {}
    for a in articles:
        by_section.setdefault(a['section'], []).append(a)
    ordered = [s for s in SECTION_ORDER if s in by_section] + \
              sorted(s for s in by_section if s not in SECTION_ORDER)

    blocks = []
    for n, sec in enumerate(ordered):
        rows = sorted(by_section[sec], key=lambda x: (x['order'], x['title']))
        items = ''.join('<li><a href="/business/%s">%s <span class="tag-live">Read now</span></a></li>'
                        % (a['slug'], html.escape(a['title'])) for a in rows)
        blocks.append('<div class="toc-part">\n'
                      '    <span class="pn">%s</span><h2>%s</h2>\n'
                      '    <ul class="toc-list">%s</ul>\n  </div>'
                      % (NUMERALS[n] if n < len(NUMERALS) else str(n + 1),
                         html.escape(sec), items))

    hub_art = ('<section class="wrap read">\n  <p class="lede">%s</p>\n'
               '  %s\n\n  %s\n\n  %s\n\n  %s\n</section>'
               % (html.escape(HUB_INTRO), HUB_CAVEAT, PRO_BLOCK + '\n\n  ' + SURVEY_BLOCK,
                  '\n  '.join(blocks) or '<p>Nothing published yet.</p>', tool_part()))

    hub_desc = ('Free business resources for working upholsterers: pricing, quoting, finding '
                'customers, running a workshop and making a living from the craft.')
    today = datetime.date.today().isoformat()
    hub = swap_head(pre, 'Business Hub \u2014 free resources for working upholsterers',
                    hub_desc, SITE + '/business/')
    hub = hub.replace('</head>', CSS + '\n' + hub_schema(articles, ordered, by_section) + '\n</head>', 1)
    hub += page_header('Business Hub', 'Making a living from upholstery', today)
    open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8').write(hub + mid + hub_art + tail)

    # ---- MCP data: the canonical answers, for the Business Hub tool.
    if os.path.isdir('functions'):
        def js(v):
            return ('"' + str(v).replace('\\', '\\\\').replace('"', '\\"')
                    .replace('\n', ' ').replace('\u2019', "\\u2019")
                    .replace('\u2014', "\\u2014").replace('\u00a3', "\\u00a3") + '"')
        rows = ',\n  '.join(
            '{slug:%s,title:%s,question:%s,answer:%s,section:%s,url:%s}'
            % (js(a['slug']), js(a['title']), js(a['question']), js(a['answer']),
               js(a['section']), js(a['url'])) for a in articles)
        open(os.path.join('functions', '_business-data.js'), 'w', encoding='utf-8').write(
            '// Generated by build-business.py. Do not edit by hand.\n'
            '// Regenerated on every build, so the MCP tool and the site cannot disagree.\n'
            'export const BUSINESS_UPDATED = "%s";\n'
            'export const BUSINESS_ARTICLES = [\n  %s\n];\n'
            % (datetime.date.today().isoformat(), rows))
        print('functions/_business-data.js written (%d articles for MCP)' % len(articles))

    # robots.txt already keeps /project-sources/ out of the index; the article
    # sources deserve the same treatment.
    if os.path.exists('robots.txt'):
        rb = open('robots.txt', encoding='utf-8').read()
        if '/business-sources/' not in rb and 'Disallow: /project-sources/' in rb:
            rb = rb.replace('Disallow: /project-sources/',
                            'Disallow: /project-sources/\nDisallow: /business-sources/', 1)
            open('robots.txt', 'w', encoding='utf-8').write(rb)
            print('robots.txt: /business-sources/ disallowed')

    print('%d articles across %d sections -> %s/' % (len(articles), len(by_section), OUT_DIR))
    for sec in ordered:
        print('   %-30s %d' % (sec, len(by_section[sec])))
    print('   %-30s %d calculators + Visualiser Pro' % ('hub tool directory', len(TOOLS)))
    if skipped:
        print('Skipped:')
        for s in skipped:
            print('   - ' + s)


if __name__ == '__main__':
    main()

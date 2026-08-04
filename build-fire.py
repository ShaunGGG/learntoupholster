#!/usr/bin/env python3
"""
build-fire.py — the fire regulations section.

Generates:
    fire-regulations.html                  hub, linking every country
    fire-regulations-usa.html
    fire-regulations-canada.html
    fire-regulations-australia-new-zealand.html
    fire-regulations-ireland.html

The UK keeps its existing page at /fire-safety-checker, which has years of
search history behind it. The hub links to it rather than duplicating it.

Every page carries domestic and commercial requirements, and states plainly
where a country has none \u2014 because "there is no mandatory standard" is itself
the answer an upholsterer needs, and is nowhere written down.

Content comes from fire-data.py, where every claim is traceable to a listed
source. Page chrome is lifted from an existing page at build time so the
section matches the rest of the site automatically.

Run before build-inline.py.
"""

import os, re, sys, html, datetime, importlib.util

SITE = 'https://www.learntoupholster.com'
CHROME_FROM = 'webbing.html'
OG = SITE + '/assets/og-card.jpg'
HUB = 'fire-regulations.html'

STATUS = {
    'mandatory': ('Required by law', 'st-req'),
    'partial':   ('Depends on the building', 'st-part'),
    'voluntary': ('Voluntary standard only', 'st-vol'),
    'none':      ('No upholstery fire standard', 'st-none'),
}


def load():
    spec = importlib.util.spec_from_file_location('fd', 'fire-data.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def get_chrome():
    if not os.path.exists(CHROME_FROM):
        sys.exit('Cannot find %s to use as the page template.' % CHROME_FROM)
    h = open(CHROME_FROM, encoding='utf-8').read()
    art = re.search(r'<article[^>]*>.*?</article>', h, re.S)
    if not art:
        sys.exit('No <article> in %s.' % CHROME_FROM)
    hdr = re.search(r'<header class="chapter-head">.*?</header>', h, re.S)
    tail = h[art.end():]
    links = ('<div class="related">\n'
             '    <a href="/fire-regulations"><span class="dir">All countries</span><br>'
             '<span class="ttl">Fire regulations by country \u2192</span></a>\n'
             '    <a href="/tools"><span class="dir">Free tools</span><br>'
             '<span class="ttl">Calculators &amp; checkers \u2192</span></a>\n  </div>')
    tail = re.sub(r'<div class="related">.*?</div>', lambda _m: links, tail, count=1, flags=re.S)
    if hdr and hdr.end() <= art.start():
        return h[:hdr.start()], h[hdr.end():art.start()], tail
    return h[:art.start()], '', tail


def swap_head(head, title, desc, url):
    def sub(pat, val, s):
        return re.sub(pat, lambda m: m.group(1) + val + m.group(2), s, count=1)
    head = re.sub(r'<title>.*?</title>',
                  lambda _m: '<title>%s | Learn to Upholster</title>' % html.escape(title),
                  head, count=1, flags=re.S)
    for attr, val in (('name="description"', html.escape(desc)),
                      ('property="og:title"', html.escape(title)),
                      ('property="og:description"', html.escape(desc)),
                      ('property="og:url"', url),
                      ('property="og:image"', OG)):
        head = sub(r'(<meta\s+' + attr + r'\s+content=")(?:[^"]*)(")', val, head)
    head = sub(r'(<link\s+rel="canonical"\s+href=")(?:[^"]*)(")', url, head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', head, flags=re.S)
    return head


CSS = """<style>
.fr-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:1rem;margin:1.6rem 0}
.fr-card{background:#fff;border:1px solid var(--rule);border-radius:3px;padding:1rem 1.2rem;
  text-decoration:none;display:block;color:var(--ink)}
.fr-card:hover{border-color:var(--green-deep)}
.fr-card h2{font-family:var(--display);font-size:1.15rem;margin:0 0 .35rem;color:var(--green-deep)}
.fr-card p{margin:.35rem 0 0;font-size:.95rem}
.fr-tags{margin:.4rem 0 0;font-size:.82rem}
.fr-tag{display:inline-block;border-radius:2px;padding:.12rem .5rem;margin:0 .3rem .3rem 0;font-weight:600}
.st-req{background:var(--terracotta);color:#fff}
.st-part{background:var(--gold);color:#22382C}
.st-vol{background:var(--sage);color:#22382C}
.st-none{background:var(--cream-deep);color:var(--ink);border:1px solid var(--rule)}
.fr-sec{background:#fff;border:1px solid var(--rule);border-left:4px solid var(--green-deep);
  border-radius:3px;padding:1.2rem 1.4rem;margin:1.8rem 0 0}
.fr-sec h2{font-family:var(--display);font-size:1.3rem;margin:0 0 .2rem;color:var(--green-deep)}
.fr-sec .std{font-size:.97rem;margin:.2rem 0 .9rem}
.fr-pt{margin:0 0 1rem}
.fr-pt h3{font-family:var(--display);font-size:1.03rem;margin:0 0 .2rem;color:var(--green-deep)}
.fr-pt p{margin:0}
.fr-label{background:#fff;border:1px solid #000;padding:.75rem .9rem;margin:.6rem 0;
  font-family:ui-monospace,monospace;font-size:.9rem;color:#000}
.fr-table{width:100%;border-collapse:collapse;margin:.8rem 0;font-size:.94rem}
.fr-table th,.fr-table td{text-align:left;padding:.42rem .6rem;border-bottom:1px solid var(--rule)}
.fr-table th{font-family:var(--display);color:var(--green-deep)}
.fr-table td.none{color:var(--ink-soft)}
@media(max-width:700px){
  /* Three columns of occupancy data will not fit a phone; restack each row. */
  .fr-table,.fr-table tbody,.fr-table tr,.fr-table td{display:block;width:100%;box-sizing:border-box}
  .fr-table thead{position:absolute;left:-9999px}
  .fr-table tr{background:#fff;border:1px solid var(--rule);border-radius:3px;
    padding:.55rem .7rem;margin:0 0 .7rem}
  .fr-table td{border:0;padding:.2rem 0;display:flex;gap:.6rem;align-items:baseline}
  .fr-table td::before{content:attr(data-l);flex:0 0 8.4rem;font-size:.8rem;font-weight:600;
    text-transform:uppercase;letter-spacing:.02em;color:var(--green-deep)}
}
.fr-src{font-size:.88rem;border-top:1px solid var(--rule);margin-top:1.8rem;padding-top:.9rem}
.fr-src ul{margin:.3rem 0 .7rem;padding-left:1.1rem}
.fr-warn{background:var(--cream-deep);border-left:4px solid var(--terracotta);border-radius:3px;
  padding:.9rem 1.1rem;margin:1.4rem 0;font-size:.97rem}
.fr-checked{font-size:.88rem;margin:.4rem 0 0}
@media print{.fr-card{break-inside:avoid}}
</style>"""


def section(kind, data):
    label_txt, cls = STATUS[data['status']]
    h = ['<div class="fr-sec">',
         '  <h2>%s</h2>' % ('Domestic work' if kind == 'domestic' else 'Commercial and contract work'),
         '  <p class="fr-tags"><span class="fr-tag %s">%s</span></p>' % (cls, label_txt),
         '  <p class="std"><strong>%s</strong></p>' % html.escape(data['headline'])]
    for title, body in data['points']:
        h.append('  <div class="fr-pt"><h3>%s</h3><p>%s</p></div>'
                 % (html.escape(title), body))
    if data.get('table'):
        t = data['table']
        h.append('  <table class="fr-table"><thead><tr>%s</tr></thead><tbody>'
                 % ''.join('<th>%s</th>' % html.escape(c) for c in t['head']))
        for row in t['rows']:
            cells = ''.join('<td%s data-l="%s">%s</td>'
                            % (' class="none"' if c == 'None' else '',
                               html.escape(t['head'][i]), html.escape(c))
                            for i, c in enumerate(row))
            h.append('    <tr>%s</tr>' % cells)
        h.append('  </tbody></table>')
        h.append('  <p class="fr-checked">%s</p>' % html.escape(t['note']))
    if data.get('label'):
        h.append('  <h3 style="font-family:var(--display);color:var(--green-deep);'
                 'margin:1.2rem 0 .2rem">The label</h3>')
        h.append('  <div class="fr-label">%s</div>' % html.escape(data['label']))
        if data.get('label_notes'):
            h.append('  <ul>%s</ul>' % ''.join('<li>%s</li>' % html.escape(n)
                                               for n in data['label_notes']))
    h.append('</div>')
    return '\n'.join(h)


def country_schema(c, url):
    esc = lambda t: (t or '').replace('\\', '\\\\').replace('"', '\\"')
    return ('<script type="application/ld+json">\n'
            '{"@context":"https://schema.org","@graph":['
            '{"@type":"Article","@id":"%s#article","headline":"%s upholstery fire regulations",'
            '"description":"%s","url":"%s","inLanguage":"en","dateModified":"%s",'
            '"author":{"@id":"%s/about#shaun"},"publisher":{"@id":"%s#org"},'
            '"isPartOf":{"@type":"WebPage","@id":"%s/fire-regulations#hub"}},'
            '{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
            '{"@type":"ListItem","position":2,"name":"Fire regulations","item":"%s/fire-regulations"},'
            '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}]}\n</script>'
            % (url, esc(c['name']), esc(c['summary']), url, datetime.date.today().isoformat(),
               SITE, SITE, SITE, SITE, SITE, esc(c['name']), url))


def build_country(pre, mid, tail, c, checked):
    slug = 'fire-regulations-%s' % c['code']
    url = '%s/%s' % (SITE, slug)
    title = '%s upholstery fire regulations' % c['name']
    desc = c['summary'][:158]

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">%s</p>\n\n'
        '  <div class="fr-warn"><p><strong>Written by a British upholsterer.</strong> '
        'This is informational guidance rather than legal advice, and I work in England. '
        'Every statement is sourced and the sources are listed at the foot of the page \u2014 '
        'check them, and where a job carries real risk get the requirement confirmed in writing '
        'by whoever is responsible for the premises.</p></div>\n\n'
        '  %s\n\n  %s\n\n'
        '  <div class="fr-src">\n    <p><strong>Sources.</strong></p>\n    <ul>%s</ul>\n'
        '    <p class="fr-checked">Last checked %s. Fire rules change \u2014 verify before you '
        'rely on this.</p>\n'
        '    <p><a href="/fire-regulations">All countries</a> \u00b7 '
        '<a href="/fire-safety-checker">United Kingdom checker</a> \u00b7 '
        '<a href="/disclaimer">Disclaimer</a></p>\n'
        '  </div>\n</article>'
        % (html.escape(c['summary']),
           section('domestic', c['domestic']),
           section('commercial', c['commercial']),
           ''.join('<li><a href="%s" rel="noopener nofollow" target="_blank">%s</a></li>'
                   % (u, html.escape(t)) for t, u in c['sources']),
           checked))

    page = swap_head(pre, title, desc, url)
    page = page.replace('</head>', CSS + '\n' + country_schema(c, url) + '\n</head>', 1)
    page += ('<header class="chapter-head">\n  <div class="wrap">\n'
             '    <p class="chno">Fire regulations \u00b7 %s</p>\n    <h1>%s</h1>\n'
             '    <p class="updated">Last updated: <time datetime="%s">%s</time></p>\n'
             '  </div>\n</header>'
             % (html.escape(c['name']), html.escape(title),
                datetime.date.today().isoformat(), datetime.date.today().strftime('%-d %B %Y')))
    open(slug + '.html', 'w', encoding='utf-8').write(page + mid + body + tail)
    return slug


def build_hub(pre, mid, tail, data):
    cards = []
    uk = data.UK
    cards.append(
        '<a class="fr-card" href="%s">\n  <h2>%s</h2>\n  <p>%s</p>\n'
        '  <p class="fr-tags"><span class="fr-tag %s">Domestic: %s</span>'
        '<span class="fr-tag %s">Commercial: %s</span></p>\n</a>'
        % (uk['url'], html.escape(uk['name']), html.escape(uk['summary']),
           STATUS[uk['domestic_status']][1], STATUS[uk['domestic_status']][0],
           STATUS[uk['commercial_status']][1], STATUS[uk['commercial_status']][0]))
    for c in data.COUNTRIES:
        cards.append(
            '<a class="fr-card" href="/fire-regulations-%s">\n  <h2>%s</h2>\n  <p>%s</p>\n'
            '  <p class="fr-tags"><span class="fr-tag %s">Domestic: %s</span>'
            '<span class="fr-tag %s">Commercial: %s</span></p>\n</a>'
            % (c['code'], html.escape(c['name']), html.escape(c['summary']),
               STATUS[c['domestic']['status']][1], STATUS[c['domestic']['status']][0],
               STATUS[c['commercial']['status']][1], STATUS[c['commercial']['status']][0]))

    body = (
        '<article class="article wrap read">\n'
        '  <p class="lede">Upholstery fire regulations differ enormously between countries, and '
        'most guidance online assumes you know which country it is describing. These pages set out '
        'what actually applies where, for domestic work and for commercial and contract seating.</p>\n\n'
        '  <p>Where a country has no mandatory standard, the page says so plainly. That is an '
        'answer in itself, and it is almost nowhere written down.</p>\n\n'
        '  <div class="fr-grid">\n    %s\n  </div>\n\n'
        '  <div class="fr-warn"><p><strong>The one rule that holds everywhere.</strong> On any '
        'commercial or contract job, the requirement belongs to the building rather than to the '
        'furniture. Get the required standard in writing from whoever is responsible for the '
        'premises, before you cut anything, and keep it with the job record.</p></div>\n\n'
        '  <div class="fr-src">\n'
        '    <p>Written by a British upholsterer as informational guidance, not legal advice. '
        'Every country page lists its sources. Fire rules change; each page records when it was '
        'last checked.</p>\n'
        '    <p class="fr-checked">All countries last checked %s. '
        'See also the site <a href="/disclaimer">disclaimer</a>.</p>\n'
        '  </div>\n</article>' % ('\n    '.join(cards), data.CHECKED))

    names = [data.UK['name']] + [c['name'] for c in data.COUNTRIES]
    desc = ('Upholstery fire regulations by country: %s. Domestic and commercial requirements, '
            'sourced and dated.' % ', '.join(names[:4]))[:158]

    items = []
    items.append('{"@type":"ListItem","position":1,"name":"%s","url":"%s%s"}'
                 % (data.UK['name'], SITE, data.UK['url']))
    for i, c in enumerate(data.COUNTRIES, 2):
        items.append('{"@type":"ListItem","position":%d,"name":"%s","url":"%s/fire-regulations-%s"}'
                     % (i, c['name'].replace('&', 'and'), SITE, c['code']))
    schema = ('<script type="application/ld+json">\n'
              '{"@context":"https://schema.org","@graph":['
              '{"@type":"CollectionPage","@id":"%s/fire-regulations#hub",'
              '"name":"Upholstery fire regulations by country","url":"%s/fire-regulations",'
              '"description":"Upholstery fire regulations by country, for domestic and commercial '
              'work, with sources.","inLanguage":"en",'
              '"author":{"@id":"%s/about#shaun"},"publisher":{"@id":"%s#org"},'
              '"mainEntity":{"@type":"ItemList","numberOfItems":%d,"itemListElement":[%s]}},'
              '{"@type":"BreadcrumbList","itemListElement":['
              '{"@type":"ListItem","position":1,"name":"Home","item":"%s/"},'
              '{"@type":"ListItem","position":2,"name":"Fire regulations","item":"%s/fire-regulations"}]}]}\n'
              '</script>' % (SITE, SITE, SITE, SITE, len(items), ','.join(items), SITE, SITE))

    page = swap_head(pre, 'Upholstery fire regulations by country', desc, SITE + '/fire-regulations')
    page = page.replace('</head>', CSS + '\n' + schema + '\n</head>', 1)
    page += ('<header class="chapter-head">\n  <div class="wrap">\n'
             '    <p class="chno">Free tools</p>\n'
             '    <h1>Fire regulations by country</h1>\n'
             '    <p class="updated">Last updated: <time datetime="%s">%s</time></p>\n'
             '  </div>\n</header>'
             % (datetime.date.today().isoformat(), datetime.date.today().strftime('%-d %B %Y')))
    open(HUB, 'w', encoding='utf-8').write(page + mid + body + tail)


def main():
    if not os.path.exists('fire-data.py'):
        sys.exit('fire-data.py not found. Run this from ~/learntoupholster.')
    data = load()
    pre, mid, tail = get_chrome()

    build_hub(pre, mid, tail, data)
    print('%s written \u2014 hub, %d countries' % (HUB, len(data.COUNTRIES) + 1))
    for c in data.COUNTRIES:
        slug = build_country(pre, mid, tail, c, data.CHECKED)
        print('   %-42s %s / %s'
              % (slug + '.html', c['domestic']['status'], c['commercial']['status']))
    print('   %-42s (existing page, linked from the hub)' % 'fire-safety-checker.html')


if __name__ == '__main__':
    main()

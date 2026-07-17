#!/usr/bin/env python3
"""International terminology layer:
  1. Inline first-mention US annotations in chapter/tool prose: calico (US: muslin) etc.
  2. US equivalents added to glossary.json (tooltips) and the matching A-Z entries.
  3. Four missing pairs added to the UK/US table + two FAQs on /a-z-glossary.
Idempotent. Run from repo root, then: build-inline, build-md, build-ask-index."""
import glob, json, re
from lxml import html as lx
from lxml import etree

# ---- the pairs -------------------------------------------------------------
# inline: [UK phrase (regex-safe base), US annotation]  — longest first at runtime
INLINE = [
    ('deep buttoning',   'diamond tufting'),
    ('bottoming cloth',  'cambric dust cover'),
    ('platform cloth',   'decking'),
    ('loose covers',     'slipcovers'),
    ('loose cover',      'slipcover'),
    ('drop-in seats',    'slip seats'),
    ('drop-in seat',     'slip seat'),
    ('tack roll',        'edge roll'),
    ('laid cord',        'spring twine'),
    ('web strainer',     'webbing stretcher'),
    ('webbing strainer', 'webbing stretcher'),
    ('calico',           'muslin'),
    ('wadding',          'batting'),
    ('hessian',          'burlap'),
    ('piping',           'welting'),
    ('fluting',          'channeling'),
    ('pouffe',           'pouf'),
    ('valance',          'skirt'),
]
# one annotation per BASE surface term per page (so 'loose covers' consumes 'loose cover' too)
FAMILY = {'loose covers': 'loose cover', 'drop-in seats': 'drop-in seat',
          'webbing strainer': 'web strainer'}

SKIP_PAGES = {'a-z-glossary.html', 'search.html', '404.html', 'privacy-policy.html',
              'cookie-policy.html', 'terms-of-use.html', 'disclaimer.html', 'contact.html',
              'about.html', 'contents.html', 'index.html', 'our-work.html', 'use-in-ai.html',
              'find-an-upholsterer.html', 'buy-the-book.html',
              # workshop stories stay clean prose
              'the-pair-of-nursing-chairs.html', 'the-wing-back-that-wasnt-a-howard.html',
              'the-family-sofa-from-heptonstall.html', 'the-last-chair.html'}
SKIP_ANC = {'tools', 'matbox', 'ataglance', 'related', 'capture', 'tlegend'}
SKIP_TAGS = {'a', 'h1', 'h2', 'h3', 'h4', 'figcaption', 'script', 'style', 'title', 'cite', 'svg', 'text'}

def blocked(el):
    a = el
    while a is not None:
        if isinstance(a.tag, str):
            if a.tag.lower() in SKIP_TAGS: return True
            c = a.get('class') or ''
            if any(x in c.split() for x in SKIP_ANC): return True
        a = a.getparent()
    return False

total = {}
for f in sorted(glob.glob('*.html') + glob.glob('projects/*.html')):
    if f in SKIP_PAGES: continue
    raw = open(f).read()
    if 'class="us"' in raw: continue  # already annotated
    tree = lx.fromstring(raw)
    arts = tree.xpath('//article')
    if not arts: continue
    art = arts[0]
    done = set()
    count = 0
    for base, us in INLINE:
        fam = FAMILY.get(base, base)
        if fam in done: continue
        # US term already used on the page? then no annotation needed
        page_text = ' '.join(art.itertext()).lower()
        if us.split()[0].lower() in page_text: 
            done.add(fam); continue
        pat = re.compile(r'\b(' + re.escape(base) + r')\b', re.I)
        hit = False
        for node in art.iter():
            if hit: break
            if not isinstance(node.tag, str) or blocked(node): continue
            for attr in ('text', 'tail'):
                s = getattr(node, attr)
                if not s: continue
                # tail belongs to parent context; block if parent context blocked
                if attr == 'tail' and node.getparent() is not None and blocked(node.getparent()): continue
                m = pat.search(s)
                if not m: continue
                before, term, after = s[:m.start()], m.group(1), s[m.end():]
                span = lx.fragment_fromstring(
                    '<span class="us">\u00a0(US: ' + us + ')</span>')
                span.tail = after
                if attr == 'text':
                    node.text = before + term
                    node.insert(0, span)
                else:
                    node.tail = before + term
                    parent = node.getparent()
                    parent.insert(parent.index(node) + 1, span)
                hit = True; count += 1; done.add(fam)
                break
    if count:
        new_art = etree.tostring(art, encoding='unicode', method='html')
        old_m = re.search(r'<article class="article wrap read".*?</article>', raw, re.S)
        if old_m:
            raw = raw[:old_m.start()] + new_art + raw[old_m.end():]
            open(f, 'w').write(raw)
            total[f] = count
print(f'inline: annotated {len(total)} pages, {sum(total.values())} annotations')
for k, v in sorted(total.items()): print(f'   {k}: {v}')

# ---- glossary.json + A-Z entries -------------------------------------------
US_FOR_TERM = {
    'Hessian': 'burlap', 'Calico': 'muslin', 'Wadding': 'batting', 'Piping': 'welt / welting',
    'Bottoming cloth': 'dust cover / cambric', 'Laid cord': 'spring twine',
    'Skewer': 'upholstery pin', 'Pouffe': 'pouf / hassock', 'Drop-in seat': 'slip seat',
    'Loose cover': 'slipcover', 'Webbing strainer': 'webbing stretcher',
    'Deep buttoning': 'diamond tufting',
}
g = json.load(open('glossary.json'))
jn = 0
for e in g:
    us = US_FOR_TERM.get(e['term'])
    if us and '(US:' not in e['def']:
        e['def'] = e['def'].rstrip()
        if not e['def'].endswith('.'): e['def'] += '.'
        e['def'] += f' (US: {us}.)'
        jn += 1
json.dump(g, open('glossary.json', 'w'), ensure_ascii=False, indent=1)
print(f'glossary.json: {jn} defs given US equivalents')

az = open('a-z-glossary.html').read()
an = 0
for term, us in US_FOR_TERM.items():
    gid = 'g-' + term.lower().replace(' ', '-').replace(',', '')
    m = re.search(r'(<p id="' + re.escape(gid) + r'"><strong>' + re.escape(term) + r'\.</strong>[^<]*?)(\s*<a class="aff"|</p>)', az)
    if m and '(US:' not in m.group(1):
        az = az.replace(m.group(0), m.group(1).rstrip() + f' <em>(US: {us}.)</em>' + m.group(2), 1)
        an += 1
print(f'a-z-glossary entries annotated: {an}')

# ---- extend the UK/US table + FAQ ------------------------------------------
NEW_ROWS = [
    ('Drop-in seat', 'Slip seat', 'The lift-out dining-chair pad &#8212; the classic first project both sides of the Atlantic.'),
    ('Loose cover', 'Slipcover', 'The removable tailored cover; American pattern books and suppliers all say slipcover.'),
    ('Fluting', 'Channeling', 'The parallel padded channels of a fluted back &#8212; Americans say &#8220;channel back.&#8221;'),
    ('Web strainer', 'Webbing stretcher', 'The bat-shaped tensioning tool; identical tool, different name in US catalogues.'),
]
if 'Slip seat' not in az:
    row_html = ''.join(
        f'<tr><td style="padding:.45rem .6rem;border-bottom:1px solid var(--rule)"><strong>{uk}</strong></td>'
        f'<td style="padding:.45rem .6rem;border-bottom:1px solid var(--rule)">{us}</td>'
        f'<td style="padding:.45rem .6rem;border-bottom:1px solid var(--rule)">{note}</td></tr>'
        for uk, us, note in NEW_ROWS)
    # insert before the Foam grades row (keep it last as the systems row)
    anchor = az.find('<tr><td style="padding:.45rem .6rem;border-bottom:1px solid var(--rule)"><strong>Foam grades')
    assert anchor > -1, 'foam grades row not found'
    az = az[:anchor] + row_html + az[anchor:]
    print('table: 4 rows added')

NEW_FAQS = [
    ('What is a drop-in seat called in America?',
     'A slip seat. Same thing: the removable webbed and padded frame that lifts out of a dining chair.'),
    ('What is a loose cover called in America?',
     'A slipcover. British loose covers and American slipcovers are the same removable tailored covers.'),
]
if 'slip seat' not in az.lower():
    pass  # already handled above; faq check below is on the JSON
m = re.search(r'(<script type="application/ld\+json">\s*)(\{[^<]*?"@type"\s*:\s*"FAQPage".*?\})(\s*</script>)', az, re.S)
if m:
    faq = json.loads(m.group(2))
    have = {q['name'] for q in faq['mainEntity']}
    added = 0
    for q, a in NEW_FAQS:
        if q not in have:
            faq['mainEntity'].append({'@type': 'Question', 'name': q,
                                      'acceptedAnswer': {'@type': 'Answer', 'text': a}})
            added += 1
    az = az.replace(m.group(0), m.group(1) + json.dumps(faq, ensure_ascii=False) + m.group(3), 1)
    print(f'FAQ schema: {added} questions added')
open('a-z-glossary.html', 'w').write(az)

#!/usr/bin/env python3
"""Fabric visualiser: depth + findability (idempotent).
  1. New sections after the tool: Getting a good result (furniture photo / swatch photo /
     honest limits) + Why see it first.
  2. Three new FAQs, visible + FAQPage JSON-LD.
  3. Sharper meta/og description; enriched WebApplication schema.
  4. Contextual links in from choosing-the-right-fabric, fabric-yardage, start-here.
  5. search-index.json entry refreshed with new headings/body."""
import json, re
from lxml import html as lx

F = 'fabric-visualiser.html'
c = open(F).read()

# ---- 1. new sections before the FAQ heading ---------------------------------
if 'Getting a good result' not in c:
    sections = """
<h2>Getting a good result &mdash; the two photos</h2>
<p>The tool is only ever as good as what you feed it, and two minutes of care with the photos roughly doubles the realism. Here&#8217;s what thirty years of looking at chairs suggests.</p>

<h3>The furniture photo</h3>
<p>The whole piece in frame, straight on or at a slight three-quarter angle &mdash; and stand back a couple of metres rather than crowding in, because a phone lens up close bows the arms and legs. Daylight from a window beats everything; <strong>skip the flash</strong>, which flattens texture and throws hard shadows the tool can read as marks on the cloth. Take the throws and clutter off, leave the cushions on, and photograph the actual piece in its actual room &mdash; the visualiser keeps your background, your light and your angle, which is exactly what makes the result believable.</p>

<h3>The fabric photo</h3>
<p>Lay the swatch flat and smooth it &mdash; iron it if it&#8217;s been folded, because creases come through as shading. Shoot square-on from directly above, cloth filling the frame edge to edge, in daylight with no shadow falling across it. If the fabric is patterned, get at least one full repeat in the shot so the scale has a chance of reading true; if it has a sheen, tilt until the glare goes. A supplier&#8217;s flat product photo of the fabric works well too.</p>

<div class="sidenote">
  <span class="tag">What it&#8217;s honest about</span>
  <p>Colour and the overall look: good. Pattern scale, drape, pile direction and seam placement: approximate. Use it to answer the first question &mdash; <em>roughly right, or plainly wrong?</em> &mdash; and let your upholsterer&#8217;s real sample on the real piece answer the rest. That isn&#8217;t a limitation to apologise for; it&#8217;s the correct order of decisions.</p>
</div>

<h2>Why see it first</h2>
<p>Fabric is the biggest single cost of a re-cover and the one mistake that can&#8217;t be quietly fixed &mdash; once the metres are cut, they&#8217;re yours. Every upholsterer has met the customer holding a beautiful swatch that became a sofa they can&#8217;t live with. Two photos and twenty seconds before you order is the cheapest insurance in the trade. When the answer looks right: <a href="/fabric-yardage">work out how much you&#8217;d need</a>, check it against the <a href="/fire-safety-checker">UK fire regulations</a> if it&#8217;s for a home, read <a href="/choosing-the-right-fabric">how to choose fabric that lasts</a> &mdash; then <a href="/find-an-upholsterer">find an upholsterer</a> or <a href="/start-here">learn to do it yourself</a>.</p>

"""
    mark = '<h2>Questions this tool answers</h2>'
    assert mark in c
    c = c.replace(mark, sections + mark, 1)
    print('sections added')

# ---- 2. three new visible FAQs ----------------------------------------------
if 'free way to see fabric on my own sofa' not in c:
    last_ans = 'both are resized automatically.'
    i = c.find(last_ans)
    assert i > -1, 'last FAQ answer not found'
    j = c.find('</p>', i) + 4
    new_faqs = """
<h3>Is there a free way to see fabric on my own sofa before buying?</h3>
<p><strong>Yes &mdash; this one.</strong> Upload a photo of your sofa, chair, stool or headboard and a photo of the fabric, and the visualiser shows the piece re-covered in about twenty seconds, free, with the picture emailed to you. No account, no app to install.</p>
<h3>How should I photograph a fabric swatch for the visualiser?</h3>
<p><strong>Flat, smooth, square-on from directly above, filling the frame, in daylight.</strong> Iron out creases (they read as shading), keep shadows and glare off the cloth, and if it&#8217;s patterned include at least one full repeat so the scale reads true. A supplier&#8217;s flat product photo also works.</p>
<h3>Can I try more than one fabric on the same chair?</h3>
<p><strong>Yes &mdash; you get three visualisations an hour</strong>, which is exactly a shortlist: try your two or three contenders on the same photo of the piece and compare like for like. There&#8217;s also a daily limit shared across all visitors, so if today&#8217;s are gone, it refills overnight.</p>"""
    c = c[:j] + new_faqs + c[j:]
    print('3 FAQs added')

# ---- FAQ JSON-LD to match ---------------------------------------------------
m = re.search(r'<script type="application/ld\+json">\s*(\{[^<]*?"FAQPage".*?\})\s*</script>', c, re.S)
faq = json.loads(m.group(1))
have = {q['name'] for q in faq['mainEntity']}
NEW = [
    ("Is there a free way to see fabric on my own sofa before buying?",
     "Yes. Upload a photo of your sofa, chair, stool or headboard and a photo of the fabric, and the visualiser shows the piece re-covered in about twenty seconds, free, with the picture emailed to you. No account and no app to install."),
    ("How should I photograph a fabric swatch for the visualiser?",
     "Flat, smooth, square-on from directly above, filling the frame, in daylight. Iron out creases, keep shadows and glare off the cloth, and if it is patterned include at least one full repeat so the scale reads true. A supplier's flat product photo also works."),
    ("Can I try more than one fabric on the same chair?",
     "Yes. You get three visualisations an hour, which suits a shortlist: try two or three fabrics on the same photo of the piece and compare like for like. A daily limit is shared across all visitors and refills overnight."),
]
added = 0
for q, a in NEW:
    if q not in have:
        faq['mainEntity'].append({"@type": "Question", "name": q,
                                  "acceptedAnswer": {"@type": "Answer", "text": a}})
        added += 1
if added:
    c = c.replace(m.group(0),
                  '<script type="application/ld+json">\n' + json.dumps(faq, ensure_ascii=False) + '\n</script>')
    print(f'FAQ schema: +{added}')

# ---- 3. meta/og + WebApplication -------------------------------------------
old_desc = re.search(r'name="description" content="([^"]*)"', c).group(1)
new_desc = ("Wondering what your chair or sofa would look like in a different fabric? Upload two photos "
            "&#8212; the piece and a swatch &#8212; and see it re-covered in seconds, free. With photo tips "
            "for a realistic result, then find an upholsterer near you.")
c = c.replace(f'name="description" content="{old_desc}"', f'name="description" content="{new_desc}"')
og = re.search(r'property="og:description" content="([^"]*)"', c)
if og:
    c = c.replace(og.group(0), 'property="og:description" content="See your chair or sofa re-covered in your fabric in seconds &#8212; free. Two photos in, one answer out, with photo tips for a realistic result."')

m = re.search(r'<script type="application/ld\+json">\s*(\{[^<]*?"WebApplication".*?\})\s*</script>', c, re.S)
app = json.loads(m.group(1))
if 'featureList' not in app:
    app.update({
        "description": "Upload a photo of your furniture and a photo of a fabric swatch and see the piece re-covered in that fabric in about twenty seconds, free.",
        "isAccessibleForFree": True,
        "operatingSystem": "Any (web browser)",
        "featureList": ["See your own chair or sofa in any fabric from two photos",
                        "Result emailed to you in about twenty seconds",
                        "Free, no account, three tries an hour"],
    })
    c = c.replace(m.group(0),
                  '<script type="application/ld+json">\n' + json.dumps(app, ensure_ascii=False) + '\n</script>')
    print('WebApplication enriched')
open(F, 'w').write(c)

# ---- 4. inbound links --------------------------------------------------------
def after_lede(fname, html_block, guard):
    d = open(fname).read()
    if guard in d:
        print(f'{fname}: already linked'); return
    m = re.search(r'<p class="lede">.*?</p>', d, re.S)
    assert m, f'lede not found in {fname}'
    d = d.replace(m.group(0), m.group(0) + '\n\n  ' + html_block, 1)
    open(fname, 'w').write(d)
    print(f'{fname}: link added')

after_lede('choosing-the-right-fabric.html',
    ('<div class="sidenote" style="background:#fff;border:1px solid var(--rule);border-left:4px solid var(--gold)">\n'
     '    <span class="tag">See it before you buy it</span>\n'
     '    <p>Torn between fabrics? The <a href="/fabric-visualiser"><strong>free fabric visualiser</strong></a> '
     'shows your actual chair re-covered in any fabric from two photos, in about twenty seconds &mdash; '
     'the cheapest way to rule a cloth in or out before a metre is cut.</p>\n  </div>'),
    'fabric-visualiser"><strong>free fabric visualiser')

after_lede('fabric-yardage.html',
    ('<div class="sidenote" style="background:#fff;border:1px solid var(--rule);border-left:4px solid var(--gold)">\n'
     '    <span class="tag">Know the metreage &mdash; now see the cloth</span>\n'
     '    <p>Once you know how much you need, the <a href="/fabric-visualiser"><strong>free fabric '
     'visualiser</strong></a> shows the fabric on a photo of your actual piece before you order it.</p>\n  </div>'),
    'free fabric visualiser')

d = open('start-here.html').read()
if 'fabric-visualiser' not in d.split('site-footer')[0]:
    old = 'run your fabric choice through the <a href="/fire-safety-checker">fire regulations checker</a>.'
    assert old in d, 'start-here fire-checker sentence not found'
    d = d.replace(old, old + ' Torn between two fabrics? The <a href="/fabric-visualiser">free visualiser</a> shows each one on a photo of your actual chair before you order.', 1)
    open('start-here.html', 'w').write(d)
    print('start-here: link added')

# ---- 5. refresh search-index entry ------------------------------------------
idx = json.load(open('search-index.json'))
t = lx.parse(F)
art = t.xpath('//article') or t.xpath('//body')
art = art[0]
heads = [' '.join(''.join(h.itertext()).split()) for h in t.xpath('//h2') + t.xpath('//h3')]
body = ' '.join(' '.join(art.itertext()).split())[:12000]
for e in idx:
    if e['url'] == '/fabric-visualiser':
        e['headings'] = heads
        e['body'] = body
        e['desc'] = ("See your chair or sofa re-covered in your fabric in seconds, free \u2014 "
                     "with photo tips for a realistic result.")
json.dump(idx, open('search-index.json', 'w'), ensure_ascii=False, indent=1)
print('search-index refreshed')

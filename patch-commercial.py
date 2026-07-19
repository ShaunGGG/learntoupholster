#!/usr/bin/env python3
"""Close the commercial gaps found in the audit (idempotent):
  1. End-of-chapter book block on all 49 chapters (before 'Keep reading').
  2. Newsletter capture on the pages missing it.
  3. About linked from the chapter book block (E-E-A-T + kills the orphan).
  4. Tool cross-links matched to the right chapters.
  5. 404 meta; empty img alts.
"""
import glob, re

# ---------- 1 + 3. book block on chapters ----------
BOOK = '''<hr class="seam">

<section class="wrap">
  <div class="read bookblock">
    <div class="bb-text">
      <p class="eyebrow">The book this came from</p>
      <h2>Every chapter, on the bench beside you.</h2>
      <p>This whole reference is free and always will be &mdash; but a screen is a poor thing in a dusty workshop.
      <em>The Working Upholsterer&#8217;s Bible</em> is the same 35 chapters and 72 figures in a wiro-bound A4 edition
      that lies flat on the bench and takes a thumbprint without complaint. Written by
      <a href="/about">a working AMUSF-accredited upholsterer</a>, thirty years in.</p>
      <p><a class="btn btn-primary" href="/buy-the-book">The four editions &mdash; from &pound;9.99</a></p>
    </div>
  </div>
</section>

'''
BB_CSS = """.bookblock{background:var(--green-deep);color:var(--cream);border-radius:12px;padding:1.6rem 1.8rem;margin:1.6rem auto}
.bookblock .eyebrow{color:var(--gold);margin:0 0 .2rem}
.bookblock h2{color:var(--cream);font-size:1.45rem;margin:.1rem 0 .5rem}
.bookblock p{color:var(--cream);opacity:.94}
.bookblock a{color:var(--gold)}
.bookblock .btn{margin-top:.5rem;background:var(--gold);border-color:var(--gold);color:var(--green-deep);opacity:1}
"""

pages = sorted(glob.glob('*.html') + glob.glob('projects/*.html'))
chapters = [f for f in pages
            if 'class="chno"' in open(f).read() and '<article' in open(f).read()
            and f not in ('buy-the-book.html', 'about.html', 'contact.html')]

n = 0
for f in chapters:
    c = open(f).read()
    if 'bookblock' in c:
        continue
    m = re.search(r'<hr class="seam">\s*<section class="wrap">\s*<p class="eyebrow read" style="text-align:center">Keep reading</p>', c)
    if not m:
        m = re.search(r'<hr class="seam">\s*<section class="wrap">\s*<div class="related">', c)
    if not m:
        continue
    c = c[:m.start()] + BOOK + c[m.start():]
    open(f, 'w').write(c)
    n += 1
print(f'book block added to {n} chapters')

# stylesheet (build-inline will push it into every page)
css = open('styles.css').read()
if '.bookblock' not in css:
    open('styles.css', 'w').write(css + '\n' + BB_CSS)
    print('styles.css: bookblock styles added')

# ---------- 2. newsletter capture where missing ----------
src = open('webbing.html').read()
CAP = re.search(r'<section class="wrap">\s*<div class="capture read">.*?</section>', src, re.S).group(0)
missing = [f for f in pages if '/api/subscribe' not in open(f).read()
           and f not in ('404.html', 'search.html')]
n = 0
for f in missing:
    c = open(f).read()
    m = re.search(r'<footer class="site-footer">', c)
    if not m:
        continue
    c = c[:m.start()] + CAP + '\n\n' + c[m.start():]
    open(f, 'w').write(c)
    n += 1
print(f'capture added to {n} pages: {missing[:12]}')

# ---------- 4. chapter → tool cross-links ----------
LINKS = {
    'buttoning-and-tufting.html': ('Work out the diamonds',
        'Planning a buttoned job? The <a href="/deep-buttoning-calculator">deep-buttoning calculator</a> gives you the diamond grid, the fabric fullness and the button count for any panel.'),
    'calico-wadding-and-top-cover.html': ('How much cloth?',
        'Before you cut, the <a href="/fabric-yardage">fabric yardage calculator</a> works out the metreage for any piece, with pattern repeats allowed for.'),
    'foam-construction.html': ('Spec it properly',
        'The <a href="/foam-cushion-calculator">foam &amp; cushion calculator</a> turns seat dimensions into a foam specification &mdash; grade, thickness and cut sizes.'),
    'choosing-the-right-fabric.html': ('Check it&#8217;s legal',
        'For domestic work in the UK, run any cloth through the <a href="/fire-safety-checker">fire regulations checker</a> before you order it.'),
    'leather-and-hides.html': ('Hides, not metres',
        'Leather is sold by the hide and priced by the square foot &mdash; the <a href="/leather-hide-calculator">leather hide calculator</a> converts a job into hides needed.'),
    'cushions-and-fillings.html': ('Cutting plan',
        'The <a href="/box-cushion-calculator">box cushion calculator</a> gives you the full cutting plan &mdash; panels, borders, zip gusset and piping lengths.'),
    'trimming-and-finishing.html': ('Piping lengths',
        'The <a href="/piping-calculator">piping calculator</a> works out bias strip lengths and how much cloth they&#8217;ll take.'),
    'pricing-and-quoting.html': ('Price it, then paper it',
        'The <a href="/reupholstery-cost-calculator">cost estimator</a> gets you to a defensible number, and the <a href="/invoice-template">free quote &amp; invoice template</a> turns it into paperwork.'),
    'springing-traditional.html': ('See it first',
        'Customer undecided on cloth? The <a href="/fabric-visualiser">free fabric visualiser</a> shows their own chair re-covered in any fabric from two photos.'),
}
n = 0
for f, (tag, text) in LINKS.items():
    try:
        c = open(f).read()
    except FileNotFoundError:
        print(f'  (missing chapter: {f})'); continue
    if 'sidenote toolnote' in c:
        continue
    m = re.search(r'<p class="lede">.*?</p>', c, re.S)
    if not m:
        continue
    note = (f'\n\n  <div class="sidenote toolnote" style="background:#fff;border:1px solid var(--rule);'
            f'border-left:4px solid var(--gold)">\n    <span class="tag">{tag}</span>\n    <p>{text}</p>\n  </div>')
    c = c.replace(m.group(0), m.group(0) + note, 1)
    open(f, 'w').write(c)
    n += 1
print(f'tool cross-links added to {n} chapters')

# ---------- 5. 404 meta + empty alts ----------
c = open('404.html').read()
if 'name="description"' not in c:
    meta = ('<meta name="description" content="That page isn\'t here \u2014 but the whole upholstery reference is. '
            'Browse the contents, search every chapter, or start with your first project.">\n'
            '<link rel="canonical" href="https://www.learntoupholster.com/404">\n'
            '<meta property="og:title" content="Page not found \u2014 Learn to Upholster">\n'
            '<meta property="og:image" content="https://www.learntoupholster.com/assets/og-card.jpg">\n')
    c = c.replace('</head>', meta + '</head>', 1)
    open('404.html', 'w').write(c)
    print('404: meta added')

for f, fixes in {
    'fabric-visualiser.html': [
        ('<img id="prev-chair"', 'Your uploaded photo of the furniture'),
        ('<img id="prev-fabric"', 'Your uploaded photo of the fabric'),
        ('<img id="v-result"', 'Your furniture visualised in the chosen fabric'),
    ],
    'our-work.html': [('<img id="ba-img"', 'Greenwood Upholstery work in progress')],
}.items():
    c = open(f).read()
    ch = 0
    for needle, alt in fixes:
        i = c.find(needle)
        if i == -1:
            continue
        end = c.find('>', i)
        tag = c[i:end]
        if 'alt=' in tag:
            c = c[:i] + re.sub(r'alt="[^"]*"', f'alt="{alt}"', tag) + c[end:]
        else:
            c = c[:end] + f' alt="{alt}"' + c[end:]
        ch += 1
    if ch:
        open(f, 'w').write(c)
        print(f'{f}: {ch} alt attributes set')

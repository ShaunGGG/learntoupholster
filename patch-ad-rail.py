#!/usr/bin/env python3
"""Install the dormant Mediavine ad rail sitewide (idempotent).
Wraps each page's main content element in <div class="page-cols"> with an empty
<aside class="ad-rail" id="mv-sidebar"> sibling. Visually inert today (aside is
display:none and the grid is single-column); at Journey launch one commented CSS
block in styles.css is uncommented and the rail goes live at >=1180px.
Skipped by design: index, our-work, search, 404."""
import glob, re

ASIDE = '<aside class="ad-rail" id="mv-sidebar" aria-hidden="true"></aside>'
SKIP = {'index.html', 'our-work.html', 'search.html', '404.html'}

def find_close(c, open_pos, tag):
    """Return index just past the matching close tag, nesting-aware."""
    pat = re.compile(r'<' + tag + r'\b|</' + tag + r'>')
    depth = 0
    for m in pat.finditer(c, open_pos):
        depth += 1 if not m.group(0).startswith('</') else -1
        if depth == 0:
            return m.end()
    return -1

def wrap_first(c, open_re, tag):
    m = re.search(open_re, c)
    if not m: return c, False
    start = m.start()
    end = find_close(c, start, tag)
    if end < 0: return c, False
    return (c[:start] + '<div class="page-cols">\n' + c[start:end] +
            '\n' + ASIDE + '\n</div>' + c[end:]), True

# per-page main-content pattern, tried in order
PATTERNS = [
    (r'<article class="article wrap read">', 'article'),
    (r'<section class="wrap read">', 'section'),
    (r'<div class="wrap calc-wrap">', 'div'),
    (r'<div class="wrap ce-wrap">', 'div'),
    (r'<div class="wrap tools-wrap">', 'div'),
]
# plain-wrap pages: anchor to the first div.wrap after the closing header
PLAIN = {'a-z-glossary.html', 'use-in-ai.html'}

done, skipped, missed = [], [], []
for f in sorted(glob.glob('*.html') + glob.glob('projects/*.html')):
    if f in SKIP: skipped.append(f); continue
    c = open(f).read()
    if 'mv-sidebar' in c: done.append(f); continue
    ok = False
    if f in PLAIN:
        h = c.find('</header>')
        m = re.search(r'<div class="wrap">', c[h:])
        if m:
            start = h + m.start()
            end = find_close(c, start, 'div')
            if end > 0:
                c = (c[:start] + '<div class="page-cols">\n' + c[start:end] +
                     '\n' + ASIDE + '\n</div>' + c[end:])
                ok = True
    else:
        for pat, tag in PATTERNS:
            c, ok = wrap_first(c, pat, tag)
            if ok: break
    if ok:
        open(f, 'w').write(c); done.append(f)
    else:
        missed.append(f)

print(f'rail installed on {len(done)} pages | skipped by design: {sorted(skipped)} | NO PATTERN: {missed or "none"}')

# ---- dormant CSS -------------------------------------------------------------
css = open('styles.css').read()
if '.page-cols' not in css:
    css += """
/* Mediavine ad rail — structure live, display dormant until Journey launch.
   AT LAUNCH: uncomment the @media block below, run build-inline.py, redeploy,
   and tell the Mediavine launch team the sidebar element is aside#mv-sidebar.
   (After any later sidebar change, email publishers@mediavine.com to re-target.) */
.page-cols{display:grid;grid-template-columns:minmax(0,1fr)}
.ad-rail{display:none}
/*
@media(min-width:1180px){
  .page-cols{grid-template-columns:minmax(0,46rem) 300px;gap:3rem;justify-content:center;max-width:78rem;margin:0 auto;padding:0 1.5rem}
  .page-cols>.wrap{max-width:none;margin:0;padding:0;min-width:0}
  .ad-rail{display:block;width:300px;min-height:600px}
}
*/
"""
    open('styles.css', 'w').write(css)
    print('styles.css: dormant rail CSS appended')

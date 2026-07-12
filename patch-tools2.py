#!/usr/bin/env python3
"""Wires in the two new calculators: nav sub-menu sitewide, two tool cards on
/tools, and sitemap entries. Idempotent. Run from repo root."""
import glob

LEATHER_LI = '<li><a href="/leather-hide-calculator">Leather hide calculator</a></li>'
NEW_LIS = ('<li><a href="/leather-hide-calculator">Leather hide calculator</a></li>\n'
  '          <li><a href="/box-cushion-calculator">Box cushion cutting plan</a></li>\n'
  '          <li><a href="/piping-calculator">Piping &amp; bias strips</a></li>')

n = 0
for f in glob.glob('*.html'):
    t = open(f, encoding='utf-8').read()
    if '/box-cushion-calculator">Box cushion' in t or LEATHER_LI not in t:
        continue
    t = t.replace(LEATHER_LI, NEW_LIS, 1)
    open(f, 'w', encoding='utf-8').write(t); n += 1
print(f"nav: {n} pages updated")

# tools page cards, inserted after the leather card
CARDS = '''      <a class="tool-card" href="/box-cushion-calculator">
        <p class="eyebrow">Cutting</p>
        <h2>Box cushion cutting plan</h2>
        <p>Enter width, depth and height and get every panel cut to size &#8212; boxing, zip border, piping strips &#8212; with total fabric and a printable cutting list. Metric and imperial.</p>
        <span class="go">Open calculator &#8594;</span>
      </a>
      <a class="tool-card" href="/piping-calculator">
        <p class="eyebrow">Trimmings</p>
        <h2>Piping &amp; bias-strip calculator</h2>
        <p>How much cord, how wide to cut the strips, and how much fabric &#8212; straight cut or bias &#8212; with the joins counted and the honest rule on when bias is worth the waste.</p>
        <span class="go">Open calculator &#8594;</span>
      </a>
'''
t = open('tools.html', encoding='utf-8').read()
if '/box-cushion-calculator"' not in t.split('tools-soon')[0] or 'tool-card" href="/box-cushion' not in t:
    anchor = '</a>\n    </div>\n\n    <div class="tools-soon">'
    if anchor in t:
        t = t.replace(anchor, '</a>\n' + CARDS + '    </div>\n\n    <div class="tools-soon">', 1)
        open('tools.html', 'w', encoding='utf-8').write(t)
        print("tools page: 2 cards added")
    else:
        print("tools page: anchor not found - add cards manually")
else:
    print("tools page: already has cards")

# sitemap
try:
    s = open('sitemap.xml', encoding='utf-8').read()
except FileNotFoundError:
    print("sitemap.xml not found - skipped"); raise SystemExit
added = 0
for slug in ['box-cushion-calculator', 'piping-calculator']:
    if slug not in s:
        s = s.replace('</urlset>',
          f'  <url><loc>https://www.learntoupholster.com/{slug}</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>\n</urlset>')
        added += 1
if added:
    open('sitemap.xml', 'w', encoding='utf-8').write(s)
print(f"sitemap: {added} entries added")

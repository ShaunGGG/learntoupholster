#!/usr/bin/env python3
"""Wires in the fabric visualiser: nav sub-menu sitewide, tools-page card,
sitemap entry. Idempotent. Run from repo root:  python3 patch-visualiser.py"""
import glob

ANCHOR = '<li><a href="/piping-calculator">Piping &amp; bias strips</a></li>'
NEW = ANCHOR + '\n          <li><a href="/fabric-visualiser">Fabric visualiser (AI)</a></li>'
n = 0
for f in glob.glob('*.html'):
    t = open(f, encoding='utf-8').read()
    if '/fabric-visualiser">Fabric visualiser' in t or ANCHOR not in t:
        continue
    t = t.replace(ANCHOR, NEW, 1)
    open(f, 'w', encoding='utf-8').write(t); n += 1
print(f"nav: {n} pages updated")

CARD = '''      <a class="tool-card" href="/fabric-visualiser">
        <p class="eyebrow">AI</p>
        <h2>See your chair in your fabric</h2>
        <p>Upload a photo of your furniture and a fabric swatch and see the piece re-covered in seconds &#8212; free, emailed to you, with a route straight to an upholsterer who can make it real.</p>
        <span class="go">Open tool &#8594;</span>
      </a>
'''
try:
    t = open('tools.html', encoding='utf-8').read()
    if 'tool-card" href="/fabric-visualiser' not in t:
        anchor = '</a>\n    </div>\n\n    <div class="tools-soon">'
        if anchor in t:
            t = t.replace(anchor, '</a>\n' + CARD + '    </div>\n\n    <div class="tools-soon">', 1)
            open('tools.html', 'w', encoding='utf-8').write(t)
            print("tools page: card added")
        else:
            print("tools page: anchor not found - add card manually")
    else:
        print("tools page: card already present")
except FileNotFoundError:
    print("tools.html not found - skipped")

try:
    s = open('sitemap.xml', encoding='utf-8').read()
    if 'fabric-visualiser' not in s:
        s = s.replace('</urlset>',
          '  <url><loc>https://www.learntoupholster.com/fabric-visualiser</loc><changefreq>monthly</changefreq><priority>0.9</priority></url>\n</urlset>')
        open('sitemap.xml', 'w', encoding='utf-8').write(s)
        print("sitemap: entry added")
    else:
        print("sitemap: already present")
except FileNotFoundError:
    print("sitemap.xml not found - skipped")

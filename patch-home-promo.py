#!/usr/bin/env python3
"""Adds a visualiser promo strip to the homepage, before the footer.
Idempotent. Run from repo root:  python3 patch-home-promo.py"""

PROMO = '''<hr class="seam">
<section class="wrap read" id="visualiser-promo" style="text-align:center">
<p class="eyebrow">New &#183; free AI tool</p>
<h2 style="margin:.3rem 0 .6rem">See your chair in your fabric &#8212; before anyone lifts a staple</h2>
<p style="max-width:44rem;margin:0 auto 1.1rem">Upload a photo of your furniture and a fabric swatch, and in about twenty seconds you&#8217;ll see the piece re-covered &#8212; free, emailed to you, with a route straight to a professional who can make it real. 100 free visualisations a day, three per person per hour.</p>
<p><a href="/fabric-visualiser" style="display:inline-block;background:#B5552D;color:#FBF6ED;padding:.7rem 1.8rem;border-radius:3px;text-decoration:none;font-family:Fraunces,serif;font-weight:600;font-size:1.1rem;letter-spacing:.03em">Try the fabric visualiser</a></p>
</section>'''

t = open('index.html', encoding='utf-8').read()
if 'id="visualiser-promo"' in t:
    print("homepage: already has promo")
else:
    anchor = '<footer class="site-footer">'
    assert anchor in t, "footer anchor missing"
    t = t.replace(anchor, PROMO + '\n' + anchor, 1)
    open('index.html', 'w', encoding='utf-8').write(t)
    print("homepage: promo added")

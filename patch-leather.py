#!/usr/bin/env python3
"""Tunes /leather-hide-calculator to the exact query language Search Console
is showing impressions for: 'leather by the square foot', 'leather hide size',
plus adds the missing 'wastage' vocabulary. Idempotent.
Run from repo root:  python3 patch-leather.py"""
import re

F = 'leather-hide-calculator.html'
t = open(F, encoding='utf-8').read()
orig = t

# 1. Two new sections, in query language, before the worked example
NEW = '''<h2>How big is a leather hide? Standard leather hide sizes</h2>
<p>A full cow hide runs <strong>45&#8211;55 square feet</strong>, though anything from 40 to 60 sq ft turns up. Suppliers also sell a <strong>side</strong> (half a hide, split down the backbone) at roughly <strong>20&#8211;28 sq ft</strong>, and a <strong>shoulder</strong> at about <strong>12&#8211;15 sq ft</strong> &#8212; a sensible buy for dining seats and small projects. Remember a hide is animal-shaped, not rectangular: the quoted square footage includes narrow legs and irregular edges you can&#8217;t cut large panels from, which is why the wastage allowance below matters more with leather than with any cloth.</p>
<h2>Why is leather sold by the square foot, not the metre?</h2>
<p>Cloth comes off a loom at a fixed width, so it&#8217;s sold by the linear metre. Leather comes off an animal, so it&#8217;s measured flat and sold <strong>by the square foot</strong> (marked on the back of the hide, often in quarter-foot units). That&#8217;s why fabric estimates don&#8217;t translate directly: the trade rule is that <strong>one linear metre of 140&#8202;cm fabric &#8776; 18&#8211;20 sq ft of leather</strong> once you allow for the higher wastage of cutting around scars, brands and the hide&#8217;s shape &#8212; typically 25&#8211;30% wastage on leather against 10&#8211;15% on plain cloth. The calculator above applies this conversion and wastage for you.</p>
<h2>A worked example</h2>'''

if 'How big is a leather hide? Standard leather hide sizes' not in t:
    t = t.replace('<h2>A worked example</h2>', NEW, 1)

# 2. Matching FAQ schema entries (query-language names)
FAQ_ADD = ('{"@type":"Question","name":"What size is a leather hide?",'
  '"acceptedAnswer":{"@type":"Answer","text":"A full cow hide is typically 45\\u201355 square feet; '
  'a side (half hide) is 20\\u201328 sq ft and a shoulder about 12\\u201315 sq ft. Hides are irregular '
  'in shape, so allow 25\\u201330% wastage when estimating."}},'
  '{"@type":"Question","name":"Why is leather sold by the square foot?",'
  '"acceptedAnswer":{"@type":"Answer","text":"Unlike cloth, leather has no fixed roll width, so it is '
  'measured flat and sold by the square foot. As a rule of thumb, one linear metre of 140cm upholstery '
  'fabric equals roughly 18\\u201320 square feet of leather once wastage is allowed."}},')

if 'What size is a leather hide?' not in t:
    t = t.replace('"mainEntity":[', '"mainEntity":[' + FAQ_ADD, 1)

# 3. Meta description in query language
t = t.replace(
  'How much leather do you need to upholster a chair or sofa? A free leather hide calculator: pick the piece or convert a fabric estimate to square feet, allow',
  'Leather is sold by the square foot &#8212; and hide sizes vary. Free calculator: convert fabric metres to leather sq ft, see standard hide sizes, allow the right wastage, and')

if t != orig:
    open(F, 'w', encoding='utf-8').write(t)
    print("leather-hide-calculator.html patched")
else:
    print("no changes (already patched or anchors missing)")

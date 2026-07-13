#!/usr/bin/env python3
"""Buy page: adds the Amazon link (hardback / paperback / Kindle) beneath the
main buy button, makes the wiro-only-here message explicit, and adds a matching
FAQ (visible + schema). Idempotent. Run from repo root: python3 patch-buy-amazon.py"""
import json, re

F = 'buy-the-book.html'
t = open(F, encoding='utf-8').read()
if 'id="amazon-cta"' in t:
    print("already patched"); raise SystemExit

# Routed through /go/amazon so non-UK visitors land on their own marketplace.
# UK/IE -> the exact tagged product page; elsewhere -> a search on their Amazon.
HREF = ('/go/amazon?q=The+Working+Upholsterers+Bible+Greenwood'
        '&amp;u=https%3A%2F%2Fwww.amazon.co.uk%2Fdp%2FB0H8M7NDV8%3Ftag%3D842699-21')

BLOCK = f'''
<div id="amazon-cta">
  <p style="margin:1.1rem 0 .5rem;padding:.75rem .95rem;background:#fff9ec;border-left:4px solid #C19A4B;font-size:1rem">
    <strong>The wiro-bound workshop edition is sold here and nowhere else.</strong> It isn&#8217;t stocked on Amazon or in shops &#8212; this page is the only place to get it.
  </p>
  <p style="margin:.6rem 0 0;font-size:1rem;color:#6b6459">Just want to read it rather than work from it?</p>
  <p style="margin:.45rem 0 0">
    <a class="aff" href="{HREF}" target="_blank" rel="sponsored noopener"
       style="display:inline-block;padding:.6rem 1.3rem;border:1.5px solid #2F4A3A;border-radius:3px;color:#2F4A3A;text-decoration:none;font-family:Fraunces,serif;font-weight:600;font-size:1.02rem">
      Hardback, paperback &amp; Kindle on Amazon &#8594;</a>
    <span class="paid">(paid link)</span>
  </p>
</div>'''

# 1. insert after the buy button
t, n = re.subn(r'(<button id="buy"[^>]*>Buy the Workshop Edition</button>)', r'\1' + BLOCK, t, count=1)
assert n == 1, "buy button anchor not found"

# 2. trim the now-duplicated Amazon sentence from the Stripe note
t = re.sub(r'\.\s*Also available as a hardback and Kindle on Amazon\s*&#8212;\s*but this wiro edition is exclusive to this site\.', '.', t, count=1)

# 3. FAQ — visible + schema
Q = "Is the wiro-bound edition available on Amazon?"
A = ("No. The wiro-bound A4 workshop edition is sold only on learntoupholster.com - it is not stocked on "
     "Amazon or in shops. Amazon carries the hardback, paperback and Kindle editions, which contain the same "
     "words and figures but are bound for reading rather than for working from at the bench.")
if Q not in t:
    t = t.replace('<h2>Questions buyers ask</h2>',
                  f'<h2>Questions buyers ask</h2>\n<h3>{Q}</h3>\n<p>{A}</p>', 1)
    add = json.dumps({"@type": "Question", "name": Q,
                      "acceptedAnswer": {"@type": "Answer", "text": A}}, ensure_ascii=False) + ','
    # schema may be written compact or spaced - handle both
    t, k = re.subn(r'("mainEntity":\s*\[)', lambda m: m.group(1) + add, t, count=1)
    assert k == 1, "FAQ schema anchor not found"

open(F, 'w', encoding='utf-8').write(t)
print("buy-the-book.html patched: Amazon CTA + exclusivity note + FAQ")

#!/usr/bin/env python3
"""
add-amusf-crest.py — display the AMUSF member crest (used with permission).

  1. Footer: a small crest beside the "AMUSF accredited" byline on every
     content page that carries it (~38 pages).
  2. /about: a larger crest in the "Who's behind it" area.

Reuses assets/amusf-member-crest{,.webp} (240px) and -lg (360px), already
generated with a transparent background. Styling added to styles.css; run
build-inline.py afterwards to inline it. Idempotent. Preview with --dry-run.
"""
import re, os, sys, glob

DRY = "--dry-run" in sys.argv
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# The crest markup for the footer — <picture> for WebP with PNG fallback.
FOOTER_CREST = (
    '<p class="foot-crest">'
    '<picture>'
    '<source srcset="/assets/amusf-member-crest.webp" type="image/webp">'
    '<img src="/assets/amusf-member-crest.png" '
    'alt="Member of the Association of Master Upholsterers &amp; Soft Furnishers" '
    'width="120" height="110" loading="lazy" decoding="async"></picture></p>'
)

BYLINE = ('<p class="foot-small">By Shaun Greenwood \u00b7 master upholsterer, '
          'AMUSF accredited \u00b7 Greenwood Upholstery, Hebden Bridge.</p>')

MARK = "foot-crest"

n_footer = 0
for f in sorted(glob.glob("*.html")) + sorted(glob.glob("projects/*.html")):
    html = open(f, encoding="utf-8").read()
    if MARK in html or BYLINE not in html:
        continue
    # insert the crest right after the byline paragraph
    html2 = html.replace(BYLINE, BYLINE + "\n        " + FOOTER_CREST, 1)
    if html2 != html:
        n_footer += 1
        if not DRY:
            open(f, "w", encoding="utf-8").write(html2)

print("Footer crest added to %d pages" % n_footer)

# --- /about larger placement ---
about = open("about.html", encoding="utf-8").read()
if 'about-crest' in about:
    print("/about crest already present")
else:
    about_crest = (
        '\n  <p class="about-crest">'
        '<picture>'
        '<source srcset="/assets/amusf-member-crest-lg.webp" type="image/webp">'
        '<img src="/assets/amusf-member-crest-lg.png" '
        'alt="Member of the Association of Master Upholsterers &amp; Soft Furnishers" '
        'width="180" height="164" loading="lazy" decoding="async"></picture></p>\n'
    )
    # place it right after the "Who's behind it" heading
    m = re.search(r'(<h2[^>]*>Who[^<]*behind it</h2>)', about)
    if m:
        about = about.replace(m.group(1), m.group(1) + about_crest, 1)
        if not DRY:
            open("about.html", "w", encoding="utf-8").write(about)
        print("/about crest added after 'Who's behind it'")
    else:
        print("WARNING: 'Who's behind it' heading not found on /about — skipped")

# --- CSS (append to styles.css if absent) ---
css_path = "styles.css"
css = open(css_path, encoding="utf-8").read()
if ".foot-crest" not in css:
    rule = (
        "\n.foot-crest{margin:.9rem 0 0}"
        ".foot-crest img{width:120px;height:auto;opacity:.95}"
        ".about-crest{margin:1rem 0 1.4rem}"
        ".about-crest img{width:180px;height:auto}\n"
    )
    if not DRY:
        open(css_path, "a", encoding="utf-8").write(rule)
    print("CSS rules added to styles.css (run build-inline.py next)")
else:
    print("CSS rules already present")

print("\n%sDone." % ("DRY RUN — " if DRY else ""))
if not DRY:
    print("Next: python3 build-inline.py  (to inline the new CSS)")

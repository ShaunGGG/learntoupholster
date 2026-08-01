#!/usr/bin/env python3
"""
link-projects.py — wire technique chapters <-> project pages.

Each project page gains a "Techniques used in this project" block linking to
the relevant chapters. Each of those chapters gains a "See it in practice"
block linking to the project(s) that demonstrate it. Uses the site's existing
.related card styling so it looks native. Idempotent — safe to re-run.

Inserts immediately before <footer class="site-footer">. Preview with --dry-run.
Run once from repo root, then deploy (edits pages directly, no rebuild needed).
"""
import re, os, sys

DRY = "--dry-run" in sys.argv
os.chdir(os.path.dirname(os.path.abspath(__file__)))

FOOTER = '<footer class="site-footer">'
MARK_PROJ = "<!-- techniques-used -->"   # idempotency markers
MARK_CHAP = "<!-- worked-example -->"

# --- friendly titles for chapters (used in the cards) ---
CHAP_TITLE = {
 "stripping-the-old-work":            "Stripping the Old Work",
 "frame-repair-and-joint-reinforcement":"Frame Repair &amp; Joints",
 "webbing":                           "Webbing",
 "springing-traditional":             "Springing (Traditional)",
 "springing-modern":                  "Springing (Modern)",
 "stuffing-and-stitched-edges":       "Stuffing &amp; Stitched Edges",
 "foam-construction":                 "Foam Construction",
 "calico-wadding-and-top-cover":      "Calico, Wadding &amp; Top Cover",
 "buttoning-and-tufting":             "Buttoning &amp; Tufting",
 "trimming-and-finishing":            "Trimming &amp; Finishing",
}

# --- friendly titles for projects ---
PROJ_TITLE = {
 "parker-knoll-wing-chair":  "Parker Knoll Wing Chair",
 "kawasaki-motorbike-seat":  "Kawasaki Motorbike Seat",
 "modern-wing-chair":        "Modern Wing Chair",
 "fluted-chair":             "Fluted Chair",
 "renault-twizy-seat-wrap":  "Renault Twizy Seat Wrap",
 "jensen-s-v8-carpet-set":   "Jensen S-V8 Carpet Set",
}

# --- the mapping: project -> chapters it demonstrates ---
MAP = {
 "parker-knoll-wing-chair":  ["stripping-the-old-work","webbing","springing-traditional","buttoning-and-tufting"],
 "kawasaki-motorbike-seat":  ["foam-construction","buttoning-and-tufting","trimming-and-finishing"],
 "modern-wing-chair":        ["springing-modern","foam-construction","calico-wadding-and-top-cover"],
 "fluted-chair":             ["foam-construction","buttoning-and-tufting","trimming-and-finishing"],
 "renault-twizy-seat-wrap":  ["foam-construction","calico-wadding-and-top-cover","trimming-and-finishing"],
 "jensen-s-v8-carpet-set":   ["stripping-the-old-work","trimming-and-finishing"],
}

# invert: chapter -> projects that demonstrate it
CHAP_TO_PROJ = {}
for proj, chaps in MAP.items():
    for c in chaps:
        CHAP_TO_PROJ.setdefault(c, []).append(proj)

def card(href, dir_label, title):
    return ('    <a href="%s"><span class="dir">%s</span><br>'
            '<span class="ttl">%s</span></a>' % (href, dir_label, title))

def block(title, marker, cards):
    return (
        '\n<hr class="seam">\n'
        '<section class="wrap read">\n'
        '  %s\n'
        '  <h2 style="font-size:1.4rem;margin:0 0 .3rem">%s</h2>\n'
        '  <div class="related">\n%s\n  </div>\n'
        '</section>\n' % (marker, title, "\n".join(cards)))

def upsert(html, marker, snippet):
    """Replace the existing marked block if present, else insert before footer.
    Without this, adding a new project never reaches chapters that were already
    linked — their block would be skipped as 'already done' and go stale."""
    pat = re.compile(r'\n?<hr class="seam">\n<section class="wrap read">\n  '
                     + re.escape(marker) + r'.*?</section>\n', re.S)
    if pat.search(html):
        return pat.sub(lambda m: snippet, html, count=1), True, "refreshed"
    idx = html.find(FOOTER)
    if idx == -1:
        return html, False, ""
    return html[:idx] + snippet + "\n" + html[idx:], True, "added"

def insert_before_footer(html, snippet):
    idx = html.find(FOOTER)
    if idx == -1:
        return html, False
    return html[:idx] + snippet + "\n" + html[idx:], True

changed = 0

# 1) PROJECT pages: add "Techniques used"
for proj, chaps in MAP.items():
    f = "projects/%s.html" % proj
    if not os.path.exists(f):
        print("  skip (missing): %s" % f); continue
    html = open(f, encoding="utf-8").read()
    cards = [card("/"+c, "Technique", CHAP_TITLE.get(c, c)) for c in chaps]
    snippet = block("Techniques used in this project", MARK_PROJ, cards)
    html2, ok, how = upsert(html, MARK_PROJ, snippet)
    if ok and html2 != html:
        changed += 1
        if not DRY: open(f, "w", encoding="utf-8").write(html2)
        print("  %s /projects/%s  (%d technique links)" %
              ("would %s" % how if DRY else how, proj, len(cards)))

# 2) CHAPTER pages: add "See it in practice"
for chap, projs in CHAP_TO_PROJ.items():
    f = "%s.html" % chap
    if not os.path.exists(f):
        print("  skip (missing): %s" % f); continue
    html = open(f, encoding="utf-8").read()
    cards = [card("/projects/"+p, "Worked example", PROJ_TITLE.get(p, p)) for p in projs]
    snippet = block("See it in practice", MARK_CHAP, cards)
    html2, ok, how = upsert(html, MARK_CHAP, snippet)
    if ok and html2 != html:
        changed += 1
        if not DRY: open(f, "w", encoding="utf-8").write(html2)
        print("  %s /%s  (%d project link%s)" %
              ("would %s" % how if DRY else how, chap, len(cards), "" if len(cards)==1 else "s"))

print("\n%s%d pages %s." % ("DRY RUN — " if DRY else "", changed,
                            "to update" if DRY else "updated"))
if not DRY and changed:
    print("Deploy as usual — no rebuild step needed (pages edited directly).")

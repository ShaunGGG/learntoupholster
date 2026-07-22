#!/usr/bin/env python3
"""
patch-audit-fixes.py  —  one-shot fixes from the July 2026 site audit.

Run ONCE from the repo root (~/learntoupholster), then rebuild inline CSS
and deploy. Idempotent: safe to re-run.

  1. Freshness dates
       a. datePublished + dateModified into every Article JSON-LD
          (from git: first commit = published, last = modified).
       b. Visible "Last updated: <date>" line under each chapter <h1>.
       c. <lastmod> on every <url> in sitemap.xml (per-URL, from git).
  2. Meta + schema descriptions — the 17 that were truncated mid-sentence
     or over-long get clean hand-written versions (<=160 chars); the Article
     schema "description" is kept in step with the meta description.
  3. search.html gets robots=noindex,follow and is dropped from sitemap.xml.

Preview:  python3 patch-audit-fixes.py --dry-run
"""

import re, os, glob, sys, subprocess, datetime

DRY  = "--dry-run" in sys.argv
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
TODAY = datetime.date.today().isoformat()

def write(path, text):
    if not DRY:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

META = {
 "the-workshop":
   "How to set up an upholstery workshop: the right space and doors, three-layer lighting, a bench height that saves your back, and dust and fire safety.",
 "fabric-yardage":
   "How much fabric to reupholster a chair or sofa? A free calculator in metres and yards, a rule-of-thumb chart, and how to allow for pattern repeats.",
 "webbing":
   "A complete guide to upholstery webbing: choosing 10-strand jute, the 8-strand interlace, the five-tack fixing pattern, and tensioning with a strainer.",
 "customers-and-the-workshop-year":
   "The business side of upholstery: the first customer conversation, managing expectations, quoting with confidence, and the seasonal rhythm of the year.",
 "materials-reference-charts":
   "Quick-reference charts for every upholstery material: webbing, hessian and scrim, stuffings, springs, twines, tacks and staples, with typical sizes.",
 "the-family-sofa-from-heptonstall":
   "A workshop story: a 2019 Heal's sofa shredded by the family dogs but sound underneath, and why a good modern re-cover was the right call over replacing it.",
 "calico-wadding-and-top-cover":
   "Fitting an upholstery cover properly: the calico under-cover as a dress rehearsal, the wadding that smooths it, then cutting and fitting the show fabric.",
 "buttoning-and-tufting":
   "Deep buttoning and tufting explained: setting out the diamond grid, pulling buttons through to a backing patch, and forming the diagonal pleats cleanly.",
 "trimming-and-finishing":
   "The trims that finish a chair: gimp over the tack line, single and double welt (piping), and decorative dome-headed nails set at the right spacing.",
 "our-work":
   "Real pieces reupholstered by hand at Greenwood Upholstery, West Yorkshire: wing chairs, Victorian show-frames, mid-century settees and footstools.",
 "leather-hide-calculator":
   "Leather is sold by the square foot and hides vary in size. Free calculator: convert fabric metres to leather square feet and allow the right wastage.",
 "stool-pouffe":
   "How to reupholster a stool or pouffe: the three types (square, drum, pouffe) and a full buttoned drum-stool walk-through with the six-around-one pattern.",
 "fabric-visualiser":
   "See your chair or sofa in a different fabric: upload the piece and a swatch, and preview it re-covered in seconds, free, with tips for a realistic result.",
 "invoice-template":
   "A free quote, order form and invoice template for upholstery businesses: deposit terms, customer's-own-material lines, fire-safety wording and a VAT toggle.",
 "start-here":
   "New to upholstery? The exact beginner's path: the drop-in dining seat, what to buy, what to read, and the five stages in order, the way we teach it.",
 "readers-bench":
   "Reader-made first projects: drop-in seats and early pieces by people learning from The Working Upholsterer's Bible. Made yours? Submit it and get featured.",
 "fire-safety-checker":
   "Which fire regulations apply to your upholstery job? A UK checker with a printable compliance record, plus US, EU, Ireland, Canada and Australia at a glance.",
}

def git_dates(path):
    try:
        added = subprocess.run(
            ["git","log","--diff-filter=A","--format=%aI","--",path],
            capture_output=True, text=True, timeout=20).stdout.strip().splitlines()
        modified = subprocess.run(
            ["git","log","-1","--format=%aI","--",path],
            capture_output=True, text=True, timeout=20).stdout.strip()
        pub = (added[-1] if added else modified)[:10] or TODAY
        mod = (modified or pub)[:10] or TODAY
        return pub, mod
    except Exception:
        return TODAY, TODAY

def human(iso):
    try:
        return datetime.date.fromisoformat(iso).strftime("%-d %B %Y")
    except Exception:
        return iso

html_files = sorted(glob.glob("*.html")) + sorted(glob.glob("projects/*.html"))
n_dates = n_visible = n_meta = 0

for f in html_files:
    html = open(f, encoding="utf-8").read()
    orig = html
    stem = f[:-5].split("/")[-1]
    pub, mod = git_dates(f)

    def add_dates(m):
        global n_dates
        b = m.group(0)
        if '"Article"' not in b or "datePublished" in b:
            return b
        nb = re.sub(r'("@type":\s*"Article",)',
                    r'\1 "datePublished": "%s", "dateModified": "%s",' % (pub, mod),
                    b, count=1)
        if nb != b: n_dates += 1
        return nb
    html = re.sub(r'<script type="application/ld\+json">.*?</script>',
                  add_dates, html, flags=re.S)

    if 'class="updated"' not in html and "<h1>" in html and 'class="article' in html:
        def add_vis(m):
            global n_visible
            n_visible += 1
            return m.group(0) + ('\n    <p class="updated">Last updated: '
                                 '<time datetime="%s">%s</time></p>' % (mod, human(mod)))
        html = re.sub(r'</h1>', add_vis, html, count=1)

    if stem in META:
        new = META[stem]
        def repl(m):
            global n_meta
            if m.group(1) != new: n_meta += 1
            return '<meta name="description" content="%s">' % new
        html = re.sub(r'<meta name="description" content="([^"]*)">', repl, html, count=1)
        # keep Article schema description in step (literal replacement via lambda)
        html = re.sub(r'("@type": "Article"[^}]*?"description": ")[^"]*(")',
                      lambda m: m.group(1) + new + m.group(2), html, count=1)

    if f == "search.html" and 'name="robots"' not in html:
        html = re.sub(r'(<link rel="canonical"[^>]*>)',
                      r'\1\n<meta name="robots" content="noindex,follow">', html, count=1)
        print("  search.html: added noindex,follow")

    if html != orig:
        write(f, html)

print("Article schema dates added : %d" % n_dates)
print("Visible 'Last updated' line: %d" % n_visible)
print("Meta descriptions replaced : %d" % n_meta)

sm = open("sitemap.xml", encoding="utf-8").read()
smo = sm
before = sm
sm = re.sub(r'\s*<url><loc>https://www\.learntoupholster\.com/search</loc>.*?</url>',
            '', sm, flags=re.S)
if sm != before: print("Sitemap: removed /search")

def url_to_file(loc):
    p = loc.replace("https://www.learntoupholster.com","").strip("/")
    if p == "": return "index.html"
    return p + ".html" if os.path.exists(p + ".html") else None

added = 0
def add_lastmod(m):
    global added
    ub = m.group(0)
    if "<lastmod>" in ub: return ub
    loc = re.search(r'<loc>([^<]+)</loc>', ub)
    if not loc: return ub
    src = url_to_file(loc.group(1))
    _, mod = git_dates(src) if src else (TODAY, TODAY)
    added += 1
    return ub.replace("</loc>", "</loc><lastmod>%s</lastmod>" % mod, 1)
sm = re.sub(r'<url>.*?</url>', add_lastmod, sm, flags=re.S)
print("Sitemap: added <lastmod> to %d URLs" % added)
if sm != smo:
    write("sitemap.xml", sm)

print("\n" + "="*60)
print("DRY RUN — nothing written." if DRY else "Applied.")
print("="*60)

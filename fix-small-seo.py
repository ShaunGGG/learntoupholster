#!/usr/bin/env python3
"""
fix-small-seo.py — three small, verified fixes. Idempotent; aborts on anchor drift.

  A. Adds the missing /fabric-visualiser nav link to the 2 calculator pages
     that lack it (box-cushion-calculator, piping-calculator).
  B. Adds noindex + canonical to outreach/supplier-outreach.html — a working
     page with no nav, no canonical and no sitemap entry, currently crawlable.
  C. Strips <priority> and <changefreq> from sitemap.xml. They were on only
     14 of 113 URLs; Google ignores both, and partial coverage is worse than none.

Run from ~/learntoupholster.  python3 fix-small-seo.py [--dry-run]
"""
import re, os, sys, shutil, datetime

DRY = '--dry-run' in sys.argv
BK = os.path.expanduser('~/ltu-backups')
os.makedirs(BK, exist_ok=True)
STAMP = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

def backup(p):
    if DRY: return
    shutil.copy2(p, os.path.join(BK, p.replace('/', '__') + '.' + STAMP + '.bak'))

def write(p, s):
    if DRY: print("   [dry-run] would write", p); return
    open(p, 'w', encoding='utf-8').write(s)

changed = 0

# ---- A. nav link ----------------------------------------------------------
ANCHOR = '<li><a href="/workshop-forms">Workshop forms</a></li>'
NEWLI  = '\n          <li><a href="/fabric-visualiser">Fabric visualiser (AI)</a></li>'
for f in ('box-cushion-calculator.html', 'piping-calculator.html'):
    if not os.path.exists(f):
        print("A: SKIP (missing)", f); continue
    c = open(f, encoding='utf-8', errors='replace').read()
    if '/fabric-visualiser' in c:
        print("A: already present  ", f); continue
    if c.count(ANCHOR) != 1:
        print("A: ABORT anchor drift (%d matches) %s" % (c.count(ANCHOR), f)); continue
    backup(f); write(f, c.replace(ANCHOR, ANCHOR + NEWLI, 1))
    print("A: nav link added   ", f); changed += 1

# ---- B. noindex the outreach page ----------------------------------------
f = 'outreach/supplier-outreach.html'
if os.path.exists(f):
    c = open(f, encoding='utf-8', errors='replace').read()
    CHARSET = '<meta charset="utf-8">'
    if re.search(r'name=["\']robots["\'][^>]*noindex', c, re.I):
        print("B: already noindexed", f)
    elif c.count(CHARSET) != 1:
        # this page is a bare fragment with no <head>; anchor on charset
        print("B: ABORT anchor drift (%d charset matches) %s" % (c.count(CHARSET), f))
    else:
        tags = (CHARSET + '\n<meta name="robots" content="noindex,nofollow">'
                '\n<link rel="canonical" href="https://www.learntoupholster.com/outreach/supplier-outreach">')
        backup(f); write(f, c.replace(CHARSET, tags, 1))
        print("B: noindexed        ", f); changed += 1
else:
    print("B: SKIP (missing)", f)

# ---- C. sitemap tidy ------------------------------------------------------
if os.path.exists('sitemap.xml'):
    s = open('sitemap.xml', encoding='utf-8').read()
    n = len(re.findall(r'<priority>|<changefreq>', s))
    if n == 0:
        print("C: sitemap already clean")
    else:
        backup('sitemap.xml')
        s2 = re.sub(r'[ \t]*<(priority|changefreq)>.*?</\1>[ \t]*\n?', '', s)
        write('sitemap.xml', s2)
        print("C: removed %d priority/changefreq tags" % n); changed += 1

print("\n%d change(s)%s." % (changed, " (dry run - nothing written)" if DRY else ""))
if changed and not DRY:
    print("Backups in ~/ltu-backups/ stamped %s" % STAMP)

#!/usr/bin/env python3
"""
fix-sitemap-noindex.py — Learn to Upholster

patch-seo-audit-sep26.py added 7 URLs to sitemap.xml that are deliberately
noindexed (6 blog category pages via noindex-categories.py, plus
/press-pack). A noindexed URL in a sitemap is a conflicting signal and
Search Console reports it as an error.

This removes any sitemap URL whose page carries meta robots noindex, and
blanks SITEMAP_ADD in the audit script so a re-run cannot re-add them.

Checks the files on disk, not a hardcoded list — so it catches any other
noindexed page that may have crept in.

Usage:
    python3 fix-sitemap-noindex.py
    python3 fix-sitemap-noindex.py --apply
"""
import os, re, shutil, sys
from datetime import datetime, timezone

SITE = "https://www.learntoupholster.com"
APPLY = "--apply" in sys.argv
BACKUP_ROOT = os.path.expanduser("~/ltu-backups")
NOINDEX = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\'][^"\']*noindex',
                     re.I)

def die(m):
    print(f"\n  ABORT: {m}\n  Nothing was changed.\n"); sys.exit(1)

def resolve(loc):
    p = loc.replace(SITE, "").split("#")[0].split("?")[0].strip("/")
    if not p:
        return "index.html"
    for c in (f"{p}.html", f"{p}/index.html"):
        if os.path.isfile(c):
            return c
    return None

if not os.path.isfile("sitemap.xml"):
    die("sitemap.xml not found. Run from the repo root.")
xml = open("sitemap.xml", encoding="utf-8").read()
blocks = re.findall(r'[ \t]*<url>.*?</url>\s*\n?', xml, re.S)
if not blocks:
    die("no <url> blocks parsed — sitemap left untouched")

keep, drop = [], []
for b in blocks:
    m = re.search(r'<loc>(.*?)</loc>', b, re.S)
    f = resolve(m.group(1)) if m else None
    if f and NOINDEX.search(open(f, encoding="utf-8").read()):
        drop.append((m.group(1).replace(SITE, ""), f))
    else:
        keep.append(b)

print(f"  mode: {'APPLY' if APPLY else 'DRY RUN (nothing written)'}")
print(f"  sitemap URLs: {len(blocks)}   noindexed, to remove: {len(drop)}")
for loc, f in drop:
    print(f"     - {loc}")
if len(drop) > 15:
    die(f"{len(drop)} removals is more than expected — refusing to gut the "
        "sitemap. Check noindex-categories.py has not over-applied.")

# also blank SITEMAP_ADD so a re-run cannot re-add them
audit = "patch-seo-audit-sep26.py"
audit_fixed = False
if os.path.isfile(audit):
    a = open(audit, encoding="utf-8").read()
    m = re.search(r'SITEMAP_ADD = \[.*?\]', a, re.S)
    if m and m.group(0) != "SITEMAP_ADD = []":
        audit_fixed = True
        print(f"\n  {audit}: SITEMAP_ADD will be blanked "
              f"({m.group(0).count(chr(34))//2} entries) so a re-run cannot re-add")

if not drop and not audit_fixed:
    print("\n  Nothing to do — clean no-op.\n"); sys.exit(0)
if not APPLY:
    print("\n  Dry run only. Re-run with --apply.\n"); sys.exit(0)

ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
bdir = os.path.join(BACKUP_ROOT, f"sitemap-noindex-{ts}")
os.makedirs(bdir, exist_ok=True)

if drop:
    shutil.copy2("sitemap.xml", os.path.join(bdir, "sitemap.xml"))
    head = xml[:xml.find(blocks[0])]
    tail = xml[xml.rfind(blocks[-1]) + len(blocks[-1]):]
    open("sitemap.xml", "w", encoding="utf-8").write(head + "".join(keep) + tail)
    n = len(re.findall(r'<url>', open('sitemap.xml', encoding='utf-8').read()))
    if n != len(keep):
        shutil.copy2(os.path.join(bdir, "sitemap.xml"), "sitemap.xml")
        die(f"rewrote to {n} urls, expected {len(keep)} — restored.")
    print(f"\n  sitemap.xml: {len(blocks)} -> {n} URLs")

if audit_fixed:
    shutil.copy2(audit, os.path.join(bdir, audit))
    a = re.sub(r'SITEMAP_ADD = \[.*?\]',
               'SITEMAP_ADD = []  # emptied: those pages are deliberately noindexed',
               a, flags=re.S)
    open(audit, "w", encoding="utf-8").write(a)
    import py_compile
    try:
        py_compile.compile(audit, doraise=True)
        print(f"  {audit}: SITEMAP_ADD blanked, py_compile OK")
    except py_compile.PyCompileError as e:
        shutil.copy2(os.path.join(bdir, audit), audit)
        die(f"{audit} would not compile ({e}) — restored.")

print(f"  backup: {bdir}")
print("\n  Next: sitemap-freshness.py, build-inline.py, deploy, indexnow-ping.py\n")

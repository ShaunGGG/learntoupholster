#!/usr/bin/env python3
"""
fix-audit.py — fixes from the 14 Aug crawl of all 113 sitemap URLs.

  1. Internal links pointing at .html URLs that 301 to the clean path
  2. The one missing alt attribute on /fabric-visualiser
  3. Reports titles over 60 chars and meta descriptions over 165

DRY RUN BY DEFAULT. Nothing is written unless you pass --apply.

Titles and descriptions are only ever REPORTED, never rewritten -- that
is editorial copy and a script has no business guessing at it.

Generated files: business/ and blog/ pages come from build-business.py
and build-blog.py, so edits there are overwritten on the next build.
The script flags any such file rather than patching it silently.
"""
import os, re, sys, shutil
from datetime import datetime

APPLY = "--apply" in sys.argv
ROOT = os.path.expanduser("~/learntoupholster")

# Confirmed by crawl: each of these 301s to the same path without .html
REDIRECTS = {
    "/sewing.html": "/sewing",
    "/suppliers.html": "/suppliers",
    "/fabric-yardage.html": "/fabric-yardage",
    "/fire-safety-checker.html": "/fire-safety-checker",
    "/start-here.html": "/start-here",
}
# press-pack.html deliberately excluded: it is noindexed, so the hop costs nothing.

GENERATED = ("business/", "blog/", "projects/")

def is_generated(rel):
    return any(rel.startswith(g) for g in GENERATED)

os.chdir(ROOT)
print("mode   :", "APPLY" if APPLY else "DRY RUN (pass --apply to write)")
print("root   :", ROOT)
print()

link_hits, alt_hits, skipped = [], [], []
long_titles, long_descs = [], []

for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in
                   (".git", "node_modules", "assets", "blog-sources", "project-sources")]
    for fn in filenames:
        if not fn.endswith(".html"):
            continue
        path = os.path.join(dirpath, fn)
        rel = os.path.relpath(path, ".")
        try:
            text = open(path, encoding="utf-8").read()
        except Exception as e:
            print("  ! unreadable:", rel, e)
            continue
        original = text

        # --- 1. redirecting internal links ---------------------------------
        for old, new in REDIRECTS.items():
            for quote in ('"', "'"):
                needle = "href=%s%s%s" % (quote, old, quote)
                if needle in text:
                    if is_generated(rel):
                        skipped.append((rel, old))
                    else:
                        n = text.count(needle)
                        text = text.replace(needle, "href=%s%s%s" % (quote, new, quote))
                        link_hits.append((rel, old, new, n))

        # --- 2. the missing alt --------------------------------------------
        if "fabric-visualiser" in rel:
            def add_alt(m):
                tag = m.group(0)
                if re.search(r"\balt\s*=", tag, re.I):
                    return tag
                alt_hits.append((rel, tag[:70]))
                return tag[:-1].rstrip() + ' alt="">' if tag.endswith(">") else tag
            text = re.sub(r"<img\b[^>]*>", add_alt, text, flags=re.I)

        # --- 3. report only -------------------------------------------------
        m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
        if m:
            t = re.sub(r"\s+", " ", m.group(1)).strip()
            if len(t) > 60:
                long_titles.append((len(t), rel, t))
        m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
                      text, re.I | re.S)
        if m:
            d = re.sub(r"\s+", " ", m.group(1)).strip()
            if len(d) > 165:
                long_descs.append((len(d), rel, d))

        if APPLY and text != original:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            bdir = os.path.expanduser("~/ltu-backups")
            os.makedirs(bdir, exist_ok=True)
            shutil.copy2(path, os.path.join(bdir, rel.replace(os.sep, "_") + ".bak-" + stamp))
            open(path, "w", encoding="utf-8").write(text)

print("=== 1. INTERNAL LINKS AT REDIRECTING URLs ===")
if link_hits:
    for rel, old, new, n in link_hits:
        print("   %-44s %s -> %s  (x%d)" % (rel, old, new, n))
else:
    print("   none found")
if skipped:
    print("\n   SKIPPED (generated files -- fix in the build script instead):")
    for rel, old in skipped:
        print("     %-42s %s" % (rel, old))

print("\n=== 2. MISSING ALT ===")
print("   %d fixed" % len(alt_hits) if alt_hits else "   none found")

print("\n=== 3. TITLES OVER 60 CHARS (%d) -- report only ===" % len(long_titles))
for n, rel, t in sorted(long_titles, reverse=True)[:20]:
    print("   %3d  %s" % (n, t[:88]))
if len(long_titles) > 20:
    print("   ...and %d more" % (len(long_titles) - 20))

print("\n=== 4. META DESCRIPTIONS OVER 165 CHARS (%d) -- report only ===" % len(long_descs))
for n, rel, d in sorted(long_descs, reverse=True)[:15]:
    print("   %3d  %s" % (n, rel))

if not APPLY:
    print("\nNothing written. Re-run with --apply to make changes 1 and 2.")
else:
    print("\nWritten. Backups in ~/ltu-backups/. Now: ltu-deploy")

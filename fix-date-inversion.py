#!/usr/bin/env python3
"""
fix-date-inversion.py — Learn to Upholster

patch-seo-audit-sep26.py sourced datePublished from sitemap lastmod. On
pages whose lastmod reflects a later edit (the 19 Aug business cluster
work), that produced datePublished > dateModified — published after
modified, which is impossible and makes both dates untrustworthy.

Fix: where datePublished > dateModified, set datePublished to the existing
dateModified. We do not know the true publication date, but we know it is
not after the modification date. Only inverted pages are touched.

Conventions: dry-run by default, timestamped backup, JSON revalidated with
restore on failure, clean no-op on re-run, minified output to match.

Usage:
    python3 fix-date-inversion.py
    python3 fix-date-inversion.py --apply
"""
import json, os, re, shutil, sys
from datetime import datetime, timezone

SITE = "https://www.learntoupholster.com"
APPLY = "--apply" in sys.argv
BACKUP_ROOT = os.path.expanduser("~/ltu-backups")
LD = re.compile(r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.S | re.I)
ART = {"Article", "BlogPosting", "HowTo", "TechArticle"}


def die(m):
    print(f"\n  ABORT: {m}\n  Nothing was changed.\n"); sys.exit(1)


def resolve(path):
    p = path.replace(SITE, "").strip("/")
    if not p:
        return "index.html"
    for c in (f"{p}.html", f"{p}/index.html"):
        if os.path.isfile(c):
            return c
    return None


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


if not os.path.isfile("sitemap.xml") or not os.path.isfile("index.html"):
    die("Run from the repo root (the publish directory).")

locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", open("sitemap.xml", encoding="utf-8").read())
files = sorted({f for f in (resolve(u) for u in locs) if f})
if len(files) < 50:
    die(f"Only {len(files)} files resolved. Wrong directory?")
print(f"  mode: {'APPLY' if APPLY else 'DRY RUN (nothing written)'}")
print(f"  scanning {len(files)} files")

planned, found = {}, []
for f in files:
    src = open(f, encoding="utf-8").read()
    hits = []

    def repl(m):
        try:
            d = json.loads(m.group(2))
        except (ValueError, TypeError):
            return m.group(0)
        ch = False
        for n in walk(d):
            if not isinstance(n, dict):
                continue
            t = n.get("@type")
            ts = {t} if isinstance(t, str) else set(t or [])
            if not (ts & ART):
                continue
            p, mod = n.get("datePublished"), n.get("dateModified")
            if p and mod and p > mod:
                hits.append((f, p, mod))
                n["datePublished"] = mod
                ch = True
        if not ch:
            return m.group(0)
        return m.group(1) + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + m.group(3)

    new = LD.sub(repl, src)
    if hits:
        found += hits
        planned[f] = new

print(f"\n  inverted pages found: {len(planned)}")
for f, p, mod in found:
    print(f"    {f:52s} pub {p} -> {mod}")

if not planned:
    print("\n  Nothing to do — clean no-op.\n"); sys.exit(0)
if not APPLY:
    print("\n  Dry run only. Re-run with --apply.\n"); sys.exit(0)

ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
bdir = os.path.join(BACKUP_ROOT, f"date-inversion-{ts}")
for f in planned:
    dst = os.path.join(bdir, f)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(f, dst)
print(f"\n  backup: {bdir}")

ok = bad = 0
for f, new in planned.items():
    open(f, "w", encoding="utf-8").write(new)
    good = True
    for m in LD.finditer(open(f, encoding="utf-8").read()):
        try:
            json.loads(m.group(2))
        except (ValueError, TypeError):
            good = False; break
    if good:
        ok += 1
    else:
        shutil.copy2(os.path.join(bdir, f), f); bad += 1; print(f"    RESTORED {f}")
print(f"  written: {ok}   restored: {bad}")
print("\n  Next: build-inline.py, sitemap-freshness.py, deploy, indexnow-ping.py\n")

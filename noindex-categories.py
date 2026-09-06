#!/usr/bin/env python3
"""noindex-categories.py — keep the thin blog category pages out of the index.

Six category pages carry 2-3 post links each. They are navigation, not
destinations. With ~45 pages already sitting in "crawled - currently not
indexed", asking Google to index six near-empty pages competes with the posts
they point at.

  noindex  stops them being indexed
  follow   keeps the crawl path to the posts, so link equity still flows

Also removes them from sitemap.xml — a noindexed URL in a sitemap is a
contradictory signal.

Reconsider this if a category reaches 8-10 posts. At that point it is a real
hub and worth writing a proper 400-600 word orientation for instead.

Idempotent. Preview with --dry-run. Run after build-blog.py, before build-inline.py.
"""
import re, os, sys, glob, shutil, datetime, pathlib

DRY = "--dry-run" in sys.argv
os.chdir(os.path.dirname(os.path.abspath(__file__)))

ROBOTS = '<meta name="robots" content="noindex,follow">'
PAGES = sorted(glob.glob("blog/category/*.html"))
THRESHOLD = 0          # posts at which a category earns indexing again

if not PAGES:
    print("No blog/category/*.html found — nothing to do")
    sys.exit(0)

stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
bak = pathlib.Path.home() / "ltu-backups" / stamp
touched = []
noindexed = []          # slugs to pull from the sitemap

for f in PAGES:
    html = open(f, encoding="utf-8").read()
    posts = len(set(re.findall(r'href="(/blog/[^"/]+)"', html)))
    slug = "/" + f[:-len(".html")]

    if posts >= THRESHOLD:
        print("  %-46s %d posts — big enough to index, skipped" % (f, posts))
        continue
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', html, re.I):
        print("  %-46s already noindex" % f)
        noindexed.append(slug)
        continue
    if "</head>" not in html:
        print("  %-46s WARNING no </head>, skipped" % f)
        continue

    if not DRY:
        bak.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, bak / f.replace("/", "_"))
        open(f, "w", encoding="utf-8").write(
            html.replace("</head>", "  " + ROBOTS + "\n</head>", 1))
    touched.append(f)
    noindexed.append(slug)
    print("  %-46s %d posts — noindex,follow" % (f, posts))

# ---- sitemap: drop exactly the noindexed URLs, nothing else --------------
sm = "sitemap.xml"
removed = 0
if os.path.exists(sm) and noindexed:
    xml = open(sm, encoding="utf-8").read()
    new = xml
    for slug in noindexed:
        new, n = re.subn(
            r'\s*<url>(?:(?!</url>).)*?<loc>[^<]*%s/?</loc>(?:(?!</url>).)*?</url>'
            % re.escape(slug), '', new, flags=re.S)
        removed += n
    if removed and not DRY:
        bak.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sm, bak / sm)
        open(sm, "w", encoding="utf-8").write(new)

print()
print("  category pages noindexed : %d" % len(touched))
print("  sitemap entries removed  : %d" % removed)
if touched or removed:
    print("  backup                   : ~/ltu-backups/%s/" % stamp if not DRY else "  (dry run)")
print("DRY RUN — nothing written." if DRY else "Done.  Next: python3 build-inline.py")

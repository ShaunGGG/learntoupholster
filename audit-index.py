#!/usr/bin/env python3
"""learntoupholster - indexation audit + sameAs candidate finder.

Read-only. Writes nothing, changes nothing. Run from ~/learntoupholster.

Answers two questions:
  1. Why might ~45 pages be sitting in "crawled - currently not indexed"?
  2. Which profile URLs already exist on the site, for the empty SAME_AS?
"""
import re, pathlib, collections, sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent
SITE = "learntoupholster.com"
THIN = 300          # words below this is worth a look

pages = sorted(p for p in ROOT.rglob("*.html")
               if "ltu-backups" not in str(p) and ".wrangler" not in str(p))
if not pages:
    print("No HTML found - run this from ~/learntoupholster"); sys.exit(1)


class Strip(HTMLParser):
    def __init__(self):
        super().__init__()
        self.txt, self.skip = [], 0
    def handle_starttag(self, t, a):
        if t in ("script", "style", "nav", "footer"): self.skip += 1
    def handle_endtag(self, t):
        if t in ("script", "style", "nav", "footer"): self.skip = max(0, self.skip - 1)
    def handle_data(self, d):
        if not self.skip: self.txt.append(d)


def text_of(html):
    s = Strip()
    try: s.feed(html)
    except Exception: pass
    return " ".join("".join(s.txt).split())


def tag(html, pat):
    m = re.search(pat, html, re.I | re.S)
    return m.group(1).strip() if m else None


docs = {}
for p in pages:
    h = p.read_text(encoding="utf-8", errors="replace")
    rel = str(p.relative_to(ROOT))
    docs[rel] = {
        "html":  h,
        "title": tag(h, r'<title[^>]*>(.*?)</title>'),
        "desc":  tag(h, r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']'),
        "canon": tag(h, r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](.*?)["\']'),
        "noidx": bool(re.search(r'name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', h, re.I)),
        "words": len(text_of(h).split()),
    }

print("=" * 62)
print("INDEXATION AUDIT  -  %d pages" % len(docs))
print("=" * 62)

def block(label, items, show=8):
    print("\n%-34s %d" % (label, len(items)))
    for i in list(items)[:show]:
        print("    " + str(i))
    if len(items) > show:
        print("    ... and %d more" % (len(items) - show))

block("noindex tag present",  [k for k, d in docs.items() if d["noidx"]])
block("no canonical",         [k for k, d in docs.items() if not d["canon"]])
block("no meta description",  [k for k, d in docs.items() if not d["desc"]])
block("thin (<%d words)" % THIN,
      sorted(("%-52s %4dw" % (k, d["words"]) for k, d in docs.items() if d["words"] < THIN)))

for name, key in (("duplicate titles", "title"), ("duplicate descriptions", "desc")):
    c = collections.Counter(d[key] for d in docs.values() if d[key])
    dupes = [("%dx  %s" % (n, (t or "")[:60])) for t, n in c.most_common() if n > 1]
    block(name, dupes)

# ---- internal linking: orphans are the classic not-indexed cause ----------
inbound = collections.Counter()
for k, d in docs.items():
    for href in re.findall(r'href=["\'](/[^"\'#?]*)["\']', d["html"]):
        t = href.lstrip("/") or "index.html"
        if not t.endswith(".html"):
            t = t.rstrip("/") + ".html"
        if t in docs and t != k:
            inbound[t] += 1
block("ORPHANS (0 internal links in)",
      sorted(k for k in docs if inbound[k] == 0), show=15)
block("only 1 internal link in",
      sorted(k for k in docs if inbound[k] == 1), show=10)

# ---- sitemap coverage ----------------------------------------------------
sm = ROOT / "sitemap.xml"
if sm.exists():
    urls = set(re.findall(r'<loc>\s*(.*?)\s*</loc>', sm.read_text(), re.S))
    def to_file(u):
        path = re.sub(r'https?://[^/]+/?', '', u).rstrip("/")
        return (path or "index") + ".html"
    listed = {to_file(u) for u in urls}
    block("in sitemap, not on disk", sorted(listed - set(docs)))
    block("on disk, not in sitemap",
          sorted(k for k in set(docs) - listed if not docs[k]["noidx"]), show=15)
    print("\nsitemap entries: %d" % len(urls))
else:
    print("\nNO sitemap.xml")

rb = ROOT / "robots.txt"
print("\nrobots.txt:")
print("  " + ("\n  ".join(rb.read_text().strip().splitlines()[:12]) if rb.exists() else "MISSING"))

# ---- sameAs candidates ---------------------------------------------------
print("\n" + "=" * 62)
print("sameAs CANDIDATES  (external profile URLs already on the site)")
print("=" * 62)
HOSTS = ("facebook.com", "instagram.com", "youtube.com", "linkedin.com",
         "x.com", "twitter.com", "pinterest", "amazon.", "github.com",
         "amusf.org", "tiktok.com", "threads.")
found = collections.Counter()
for d in docs.values():
    for href in re.findall(r'href=["\'](https?://[^"\']+)["\']', d["html"]):
        if any(h in href.lower() for h in HOSTS) and SITE not in href:
            found[href.split("?")[0].rstrip("/")] += 1
if not found:
    print("  none found")
for u, n in found.most_common(25):
    print("  %4d  %s" % (n, u))

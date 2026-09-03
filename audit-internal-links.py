#!/usr/bin/env python3
"""
audit-internal-links.py
-----------------------
Reads the built site in this directory and reports on the internal link graph.
Read-only: it writes one file, link-audit.txt, and touches nothing else.

The point is to separate *editorial* links (in body copy, which Google treats as
endorsement) from *boilerplate* links (nav and footer, repeated on every page,
which Google heavily discounts). A link target appearing on 70% or more of pages
is treated as boilerplate and excluded from the contextual counts.

Run from ~/learntoupholster:  python3 audit-internal-links.py
Then paste link-audit.txt back into the chat.
"""

import collections
import html.parser
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
BOILERPLATE_THRESHOLD = 0.70
GENERIC_ANCHORS = {
    "read more", "more", "click here", "here", "learn more", "find out more",
    "see more", "read", "next", "previous", "back", "home", "link", "this",
    "continue", "view", "see all", "read on", "go", "start", "open",
}
SKIP_DIRS = {".git", "node_modules", "assets", "images", "functions",
             ".wrangler", "__pycache__", "md", "backups"}


class Links(html.parser.HTMLParser):
    """Collect (href, anchor_text) pairs. Ignores nothing - filtering is later."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self._href = None
        self._buf = []
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        d = dict(attrs)
        href = d.get("href")
        if self._href is not None:
            self._depth += 1
            return
        if href:
            self._href = href
            self._buf = []

    def handle_data(self, data):
        if self._href is not None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag != "a" or self._href is None:
            return
        if self._depth:
            self._depth -= 1
            return
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        self.out.append((self._href, text))
        self._href = None
        self._buf = []

    def error(self, message):
        pass


def file_to_url(p):
    """Map a built file to the URL Cloudflare Pages will serve it at."""
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel[: -len(".html")]


def normalise(href, from_url):
    """Return an internal URL path, or None if the link is external/not a page."""
    href = href.strip()
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href):
        if not href.startswith(("https://www.learntoupholster.com",
                                "https://learntoupholster.com")):
            return None
        href = re.sub(r"^https://(www\.)?learntoupholster\.com", "", href) or "/"
    href = href.split("#")[0].split("?")[0]
    if not href:
        return None
    if not href.startswith("/"):
        base = from_url.rsplit("/", 1)[0] + "/"
        href = os.path.normpath(base + href)
    if re.search(r"\.(jpg|jpeg|png|webp|gif|svg|pdf|xlsx|csv|txt|xml|zip|ico|js|css)$",
                 href, re.I):
        return None
    return href or "/"


def canonical(u, known):
    """Match a link to a real page, tolerating trailing-slash differences."""
    if u in known:
        return u
    for cand in (u.rstrip("/"), u.rstrip("/") + "/", u + "/" if not u.endswith("/") else u[:-1]):
        if cand in known:
            return cand
    return None


def cluster_of(u):
    if u == "/":
        return "(home)"
    parts = [p for p in u.split("/") if p]
    if len(parts) > 1:
        return "/" + parts[0] + "/"
    return "(top level)"


def main():
    pages = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if fn.endswith(".html"):
                pages.append(pathlib.Path(dirpath) / fn)

    if not pages:
        print("No .html files found. Run this from ~/learntoupholster.", file=sys.stderr)
        sys.exit(1)

    url_of = {p: file_to_url(p) for p in pages}
    known = set(url_of.values())

    raw = {}          # url -> list of (target_url, anchor_text)
    noindexed = set()
    for p in pages:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        u = url_of[p]
        if re.search(r'<meta[^>]+noindex', text, re.I):
            noindexed.add(u)
        parser = Links()
        parser.feed(text)
        found = []
        for href, anchor in parser.out:
            t = normalise(href, u)
            if not t:
                continue
            c = canonical(t, known)
            found.append((c or t, anchor, c is not None))
        raw[u] = found

    n = len(raw)

    # Boilerplate = a target present on >= threshold of pages.
    appears_on = collections.Counter()
    for u, links in raw.items():
        for t in {t for t, _a, ok in links if ok}:
            appears_on[t] += 1
    boiler = {t for t, c in appears_on.items() if c >= BOILERPLATE_THRESHOLD * n}

    inbound = collections.Counter()
    outbound = collections.Counter()
    anchors = collections.Counter()
    broken = collections.Counter()
    edges = collections.defaultdict(set)

    for u, links in raw.items():
        for t, a, ok in links:
            if not ok:
                broken[t] += 1
                continue
            if t in boiler or t == u:
                continue
            inbound[t] += 1
            outbound[u] += 1
            anchors[a.lower()[:60] or "(no text)"] += 1
            edges[u].add(t)

    # click depth from "/" over ALL links (nav included - it aids discovery)
    all_edges = collections.defaultdict(set)
    for u, links in raw.items():
        for t, _a, ok in links:
            if ok and t != u:
                all_edges[u].add(t)
    depth = {"/": 0}
    frontier = ["/"] if "/" in raw else [sorted(raw)[0]]
    if frontier[0] != "/":
        depth = {frontier[0]: 0}
    while frontier:
        nxt = []
        for u in frontier:
            for t in all_edges.get(u, ()):
                if t not in depth:
                    depth[t] = depth[u] + 1
                    nxt.append(t)
        frontier = nxt

    L = []
    w = L.append
    w("INTERNAL LINK AUDIT  -  learntoupholster.com")
    w("=" * 60)
    w("pages found:            %d" % n)
    w("noindex pages:          %d" % len(noindexed))
    w("boilerplate targets:    %d  (on >=%d%% of pages; excluded below)"
      % (len(boiler), int(BOILERPLATE_THRESHOLD * 100)))
    total_ctx = sum(inbound.values())
    w("contextual links:       %d  (%.1f per page average)"
      % (total_ctx, total_ctx / n if n else 0))
    w("")

    orphans = sorted(u for u in raw if inbound[u] == 0 and u != "/" and u not in boiler)
    w("ORPHANS - no contextual inbound links (%d)" % len(orphans))
    w("-" * 60)
    for u in orphans[:60]:
        w("  %-52s depth %s" % (u, depth.get(u, "UNREACHABLE")))
    if len(orphans) > 60:
        w("  ... and %d more" % (len(orphans) - 60))
    w("")

    dead = sorted(u for u in raw if outbound[u] == 0)
    w("DEAD ENDS - no contextual outbound links (%d)" % len(dead))
    w("-" * 60)
    for u in dead[:40]:
        w("  " + u)
    if len(dead) > 40:
        w("  ... and %d more" % (len(dead) - 40))
    w("")

    w("CLICK DEPTH FROM HOMEPAGE (all links incl. nav)")
    w("-" * 60)
    dh = collections.Counter(depth.get(u, -1) for u in raw)
    for d in sorted(dh):
        w("  depth %-3s %d pages" % ("?" if d < 0 else d, dh[d]))
    far = sorted(u for u in raw if 4 <= depth.get(u, -1))
    if far:
        w("  4+ clicks deep: " + ", ".join(far[:20]))
    unreach = sorted(u for u in raw if u not in depth)
    if unreach:
        w("  unreachable by any link (sitemap-only): " + ", ".join(unreach[:20]))
    w("")

    w("BY CLUSTER")
    w("-" * 60)
    w("  %-22s %5s %8s %8s" % ("cluster", "pages", "in/page", "orphans"))
    cl = collections.defaultdict(list)
    for u in raw:
        cl[cluster_of(u)].append(u)
    for c in sorted(cl, key=lambda k: -len(cl[k])):
        us = cl[c]
        ins = sum(inbound[u] for u in us) / len(us)
        orp = sum(1 for u in us if inbound[u] == 0)
        w("  %-22s %5d %8.1f %8d" % (c, len(us), ins, orp))
    w("")

    w("LEAST-LINKED PAGES (contextual inbound)")
    w("-" * 60)
    for u in sorted(raw, key=lambda k: (inbound[k], k))[:30]:
        w("  %-52s %3d in  %3d out" % (u, inbound[u], outbound[u]))
    w("")

    w("MOST-LINKED PAGES")
    w("-" * 60)
    for u, c in inbound.most_common(15):
        w("  %-52s %3d" % (u, c))
    w("")

    gen = sum(c for a, c in anchors.items() if a.strip(" .,:;>-\u2192") in GENERIC_ANCHORS)
    w("ANCHOR TEXT")
    w("-" * 60)
    w("  distinct anchors:  %d over %d links" % (len(anchors), total_ctx))
    w("  generic anchors:   %d (%.1f%%)" % (gen, 100 * gen / total_ctx if total_ctx else 0))
    w("  most repeated:")
    for a, c in anchors.most_common(20):
        w("    %4d  %s" % (c, a))
    w("")

    if broken:
        w("LINKS TO PAGES THAT DO NOT EXIST (%d targets)" % len(broken))
        w("-" * 60)
        for t, c in broken.most_common(30):
            w("  %-52s x%d" % (t, c))
        w("")

    if noindexed:
        w("NOINDEX PAGES")
        w("-" * 60)
        for u in sorted(noindexed):
            w("  " + u)
        w("")

    w("BOILERPLATE TARGETS (nav/footer, excluded from counts)")
    w("-" * 60)
    w("  " + ", ".join(sorted(boiler)[:60]))

    report = "\n".join(L)
    (ROOT / "link-audit.txt").write_text(report + "\n", encoding="utf-8")
    print(report)
    print("\n\nwritten to link-audit.txt")


if __name__ == "__main__":
    main()

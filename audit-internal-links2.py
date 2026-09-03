#!/usr/bin/env python3
"""
audit-internal-links2.py
------------------------
Version two. Version one classified links as boilerplate by counting how often a
target appeared, which meant every page listed in the nav dropdown - all the
tools, all the fire-regulations pages, all the sewing pages - was discarded and
reported as having no inbound links. That was a measurement artefact, not a
finding.

This version strips the nav and footer structurally, by walking the DOM and
ignoring everything inside <nav>, <footer> and the site's chrome classes. What
survives is body copy, so a link from a chapter to a calculator is finally
visible even though the calculator is also in the nav.

Remaining links are split two ways:

  templated   a target reached from >=50% of pages through body copy - an
              end-of-chapter block or CTA. Real links, but repeated furniture:
              Google discounts them, though less than nav.
  editorial   everything else. Written into the prose of a specific page.
              This is the number that matters.

Read-only apart from writing link-audit2.txt.
  python3 audit-internal-links2.py
"""

import collections
import html.parser
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
TEMPLATED_THRESHOLD = 0.50
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
CHROME_TAGS = {"nav", "footer"}
CHROME_CLASS = re.compile(
    r"\b(site-nav|site-footer|nav-list|sub-menu|nav-toggle|header-inner|"
    r"foot-grid|foot-legal|foot-social|foot-brand|foot-crest|breadcrumb|"
    r"skip-link|cookie|consent)\b")
SKIP_DIRS = {".git", "node_modules", "assets", "images", "functions",
             ".wrangler", "__pycache__", "md", "backups", "dist"}


class BodyLinks(html.parser.HTMLParser):
    """Collect (href, anchor) from body copy only, skipping chrome containers."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.stack = []
        self.suppress_at = None
        self._href = None
        self._buf = []
        self._anest = 0

    def _is_chrome(self, tag, attrs):
        if tag in CHROME_TAGS:
            return True
        cls = dict(attrs).get("class") or ""
        return bool(CHROME_CLASS.search(cls))

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)
            if self.suppress_at is None and self._is_chrome(tag, attrs):
                self.suppress_at = len(self.stack) - 1
        elif self.suppress_at is None and self._is_chrome(tag, attrs):
            return
        if tag != "a" or self.suppress_at is not None:
            return
        href = dict(attrs).get("href")
        if self._href is not None:
            self._anest += 1
            return
        if href:
            self._href = href
            self._buf = []

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_data(self, data):
        if self._href is not None and self.suppress_at is None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            if self._anest:
                self._anest -= 1
            else:
                text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
                self.out.append((self._href, text))
                self._href = None
                self._buf = []
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == tag:
                del self.stack[i:]
                break
        if self.suppress_at is not None and len(self.stack) <= self.suppress_at:
            self.suppress_at = None

    def error(self, message):
        pass


def file_to_url(p):
    rel = p.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel[: -len(".html")]


def normalise(href, from_url):
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
        href = os.path.normpath(from_url.rsplit("/", 1)[0] + "/" + href)
    if re.search(r"\.(jpg|jpeg|png|webp|gif|svg|pdf|xlsx|csv|txt|xml|zip|ico|js|css)$",
                 href, re.I):
        return None
    return href or "/"


def canonical(u, known):
    if u in known:
        return u
    for c in (u.rstrip("/"), u.rstrip("/") + "/"):
        if c in known:
            return c
    return None


def cluster_of(u):
    if u == "/":
        return "(home)"
    parts = [p for p in u.split("/") if p]
    return "/" + parts[0] + "/" if len(parts) > 1 else "(top level)"


def main():
    pages = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if fn.endswith(".html") and ".bak-" not in fn:
                pages.append(pathlib.Path(dirpath) / fn)
    if not pages:
        print("No .html files found. Run from ~/learntoupholster.", file=sys.stderr)
        sys.exit(1)

    url_of = {p: file_to_url(p) for p in pages}
    known = set(url_of.values())

    raw = {}
    for p in pages:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        u = url_of[p]
        pr = BodyLinks()
        pr.feed(text)
        found = []
        for href, anchor in pr.out:
            t = normalise(href, u)
            if not t:
                continue
            c = canonical(t, known)
            found.append((c or t, anchor, c is not None))
        raw[u] = found

    n = len(raw)
    src_count = collections.Counter()
    for u, links in raw.items():
        for t in {t for t, _a, ok in links if ok and t != u}:
            src_count[t] += 1
    templated = {t for t, c in src_count.items() if c >= TEMPLATED_THRESHOLD * n}

    ed_in = collections.Counter()
    tp_in = collections.Counter()
    ed_out = collections.Counter()
    anchors = collections.defaultdict(collections.Counter)
    for u, links in raw.items():
        for t, a, ok in links:
            if not ok or t == u:
                continue
            if t in templated:
                tp_in[t] += 1
            else:
                ed_in[t] += 1
                ed_out[u] += 1
                anchors[t][a.lower()[:60] or "(no text)"] += 1

    L = []
    w = L.append
    w("INTERNAL LINK AUDIT v2  -  nav and footer stripped structurally")
    w("=" * 66)
    w("pages:                %d" % n)
    w("body-copy links:      %d  (%.1f per page)"
      % (sum(len(v) for v in raw.values()), sum(len(v) for v in raw.values()) / n))
    w("editorial links:      %d  (%.1f per page)"
      % (sum(ed_in.values()), sum(ed_in.values()) / n))
    w("templated targets:    %d  (reached from >=50%% of pages via body copy)"
      % len(templated))
    if templated:
        w("   " + ", ".join(sorted(templated)[:25]))
    w("")

    w("PAGES WITH NO EDITORIAL INBOUND LINK")
    w("-" * 66)
    zero = sorted(u for u in raw if ed_in[u] == 0 and u != "/")
    w("count: %d" % len(zero))
    for u in zero:
        w("  %-50s %3d templated" % (u, tp_in[u]))
    w("")

    w("BY CLUSTER  (editorial inbound only)")
    w("-" * 66)
    w("  %-24s %5s %9s %8s" % ("cluster", "pages", "ed-in/pg", "zero-in"))
    cl = collections.defaultdict(list)
    for u in raw:
        cl[cluster_of(u)].append(u)
    for c in sorted(cl, key=lambda k: -len(cl[k])):
        us = cl[c]
        w("  %-24s %5d %9.1f %8d"
          % (c, len(us), sum(ed_in[u] for u in us) / len(us),
             sum(1 for u in us if ed_in[u] == 0)))
    w("")

    w("CLUSTER RECIPROCITY  (do siblings link to each other?)")
    w("-" * 66)
    groups = {
        "fire regulations": [u for u in raw if u.startswith("/fire-")],
        "sewing": [u for u in raw if u.startswith("/sewing")],
        "calculators/tools": [u for u in raw if re.search(
            r"(calculator|/tools$|fabric-yardage|invoice-template|"
            r"workshop-forms|fabric-visualiser|suppliers)", u)],
    }
    for name, us in groups.items():
        us = sorted(set(us))
        if not us:
            continue
        internal = 0
        for u in us:
            internal += sum(1 for t, _a, ok in raw.get(u, [])
                            if ok and t in us and t != u)
        w("  %-20s %2d pages, %2d sibling links between them"
          % (name, len(us), internal))
        for u in us:
            sib = sorted({t for t, _a, ok in raw.get(u, []) if ok and t in us and t != u})
            w("    %-46s -> %s" % (u, ", ".join(sib) if sib else "(none)"))
        w("")

    w("MOST EDITORIALLY LINKED")
    w("-" * 66)
    for u, c in ed_in.most_common(20):
        top = anchors[u].most_common(1)[0]
        w("  %-46s %3d  (%d distinct anchors, top: %s)"
          % (u, c, len(anchors[u]), top[0][:34]))
    w("")

    w("ANCHOR CONCENTRATION  (one anchor dominating a target)")
    w("-" * 66)
    for u, c in ed_in.most_common(40):
        if c < 5:
            continue
        a, ac = anchors[u].most_common(1)[0]
        if ac / c >= 0.8:
            w("  %-46s %d/%d use \"%s\"" % (u, ac, c, a[:40]))

    report = "\n".join(L)
    (ROOT / "link-audit2.txt").write_text(report + "\n", encoding="utf-8")
    print(report)
    print("\n\nwritten to link-audit2.txt")


if __name__ == "__main__":
    main()

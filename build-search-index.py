#!/usr/bin/env python3
"""
build-search-index.py
---------------------
Regenerates search-index.json, the chapter-browse index that /search filters
client-side. Nothing built this file before: it was written once in July and
went stale, so nine live chapters were missing from browse.

The chapter list comes from contents.html, which is the hand-maintained source
of truth for what is in the book. Add a chapter there, run this, and it appears
in browse. Coming-soon entries are skipped; they have no page to open.

Per-page fields are read from each chapter's own HTML so they cannot drift from
what the page displays:

  url       the path, from contents.html
  title     <h1>, falling back to <title>
  chno      <p class="chno"> exactly as the page shows it - NOT derived from
            position, because the Part Five tools say "Free tool - Reference"
  desc      meta description
  img       og:image, omitted when absent
  headings  <h2> text, minus the standard furniture blocks
  aff       affiliate links, label + url
  body      visible prose, tags and chrome stripped

EXTRAS below are pages kept in browse that are not chapters in contents.html.

  python3 build-search-index.py            report what would change
  python3 build-search-index.py --write    write search-index.json
"""

import html as htmllib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "search-index.json"
WRITE = "--write" in sys.argv

# in the index but not chapters in contents.html - deliberate, keep them
EXTRAS = ["/start-here", "/invoice-template"]

# headings that are page furniture rather than chapter content
SKIP_HEADINGS = {
    "the book this came from", "free upholstery tips by email",
    "have a piece like this?", "rather we did it?", "see it in practice",
    "techniques used in this project", "why we document every job",
    "questions buyers ask", "the gallery",
}

STRIP_BLOCKS = re.compile(
    r"<script.*?</script>|<style.*?</style>|<nav.*?</nav>|<footer.*?</footer>|"
    r"<head.*?</head>", re.S)


def text_of(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", htmllib.unescape(t)).strip()


def chapters_from_contents():
    """[(url, part, title)] for every live chapter listed in contents.html."""
    src = (ROOT / "contents.html").read_text(encoding="utf-8")
    out = []
    for part in re.findall(r'<div class="toc-part">(.*?)</ul>', src, re.S):
        pn = re.search(r'<span class="pn">([^<]+)</span>', part)
        part_name = htmllib.unescape(pn.group(1)) if pn else ""
        for m in re.finditer(r'<li><a href="(/[a-z0-9-]+)">(.*?)</a></li>',
                             part, re.S):
            url, label = m.group(1), m.group(2)
            if "tag-live" not in label:
                continue          # coming soon - no page to open
            title = text_of(re.sub(r'<span class="tag-[^"]*">.*?</span>', "",
                                   label, flags=re.S))
            out.append((url, part_name, title))
    return out


def record(url):
    p = ROOT / (url.lstrip("/") + ".html")
    if not p.exists():
        return None, "no such page"
    raw = p.read_text(encoding="utf-8")
    body_html = STRIP_BLOCKS.sub(" ", raw)

    def one(pattern, source=raw):
        m = re.search(pattern, source, re.S)
        return text_of(m.group(1)) if m else ""

    title = one(r"<h1[^>]*>(.*?)</h1>") or one(r"<title>(.*?)</title>")
    rec = {
        "url": url,
        "title": title,
        "chno": one(r'<p class="chno">(.*?)</p>'),
        "desc": one(r'<meta name="description" content="([^"]*)"'),
    }
    # candidate figures, in page order. img is NOT derived for pages already
    # in the index - see main(). The July index was curated by eye: it holds
    # the second figure on some pages and the first on others, with no signal
    # in the markup to tell them apart. Guessing a rule would silently change
    # images you chose deliberately.
    main_m = re.search(r"<main[^>]*>(.*?)</main>", body_html, re.S)
    scope = main_m.group(1) if main_m else body_html
    figs = []
    for m in re.finditer(r'<img[^>]+src="([^"]+)"', scope):
        src = htmllib.unescape(m.group(1))
        if re.search(r"crest|logo|icon|avatar|amusf|badge", src, re.I):
            continue
        if src not in figs:
            figs.append(src)
    rec["_figs"] = figs

    heads = []
    for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", body_html, re.S):
        h = text_of(m.group(1))
        if h and h.lower() not in SKIP_HEADINGS and h not in heads:
            heads.append(h)
    if heads:
        rec["headings"] = heads

    aff = []
    for m in re.finditer(r'<a[^>]*class="aff"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                         body_html, re.S):
        label = text_of(m.group(2))
        if label and not any(a["label"] == label for a in aff):
            aff.append({"label": label, "url": htmllib.unescape(m.group(1))})
    if aff:
        rec["aff"] = aff

    main = re.search(r"<main[^>]*>(.*?)</main>", body_html, re.S)
    rec["body"] = text_of(main.group(1) if main else body_html)
    return rec, None


def main():
    chapters = chapters_from_contents()
    print("contents.html: %d live chapters" % len(chapters))

    wanted = [(u, p, t) for u, p, t in chapters]
    wanted += [(u, "", "") for u in EXTRAS]

    records, problems = [], []
    for url, _part, _title in wanted:
        rec, err = record(url)
        if err:
            problems.append((url, err))
            continue
        for field in ("title", "chno", "desc"):
            if not rec[field]:
                problems.append((url, "empty %s" % field))
        records.append(rec)

    old = {}
    if OUT.exists():
        old = {r["url"]: r for r in json.loads(OUT.read_text(encoding="utf-8"))}
    new = {r["url"] for r in records}

    # img: keep what is already there, derive only for pages that are new
    derived = []
    for r in records:
        figs = r.pop("_figs", [])
        prev = old.get(r["url"], {}).get("img")
        if prev:
            r["img"] = prev
        elif r["url"] not in old and figs:
            r["img"] = figs[0]
            derived.append((r["url"], figs))
        # a page already indexed with no img keeps having none

    if derived:
        print("\nIMG CHOSEN FOR NEW PAGES (first figure - change by hand if wrong)")
        print("-" * 60)
        for u, figs in derived:
            print("  %-38s %s" % (u, figs[0]))
            for f in figs[1:4]:
                print("  %-38s   alt: %s" % ("", f))
    kept = sum(1 for r in records if r.get("img") and r["url"] in old)
    print("\n  %d existing image(s) preserved unchanged" % kept)

    print("\nADDED (%d)" % len(new - set(old)))
    print("-" * 60)
    for r in records:
        if r["url"] not in old:
            print("  %-42s %s" % (r["url"], r["chno"]))
    gone = set(old) - new
    if gone:
        print("\nDROPPED (%d) - in the old index, not a live chapter" % len(gone))
        print("-" * 60)
        for u in sorted(gone):
            print("  " + u)

    if problems:
        print("\nPROBLEMS (%d)" % len(problems))
        print("-" * 60)
        for u, why in problems:
            print("  %-42s %s" % (u, why))

    for r in records:
        r.pop("_figs", None)
    payload = json.dumps(records, ensure_ascii=False, indent=1)
    print("\n%d records, %.0fKB (was %.0fKB, %d records)"
          % (len(records), len(payload.encode()) / 1024,
             OUT.stat().st_size / 1024 if OUT.exists() else 0, len(old)))

    if WRITE:
        if problems:
            print("\nNot writing - fix the problems above first, or the browse "
                  "list ships with blank fields.")
            sys.exit(1)
        OUT.write_text(payload + "\n", encoding="utf-8")
        print("\nwritten to search-index.json")
    else:
        print("\nre-run with --write to save.")


if __name__ == "__main__":
    main()

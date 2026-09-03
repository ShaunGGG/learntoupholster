#!/usr/bin/env python3
"""
fix-broken-links.py
-------------------
Repairs the three genuinely broken internal link targets found in the audit:

  /our-work           -> /projects/#gallery   (retired page; costs a 301 hop)
  /press-pack.html    -> /press-pack          (extension form won't match)
  /buy-the-book.html  -> /buy-the-book        (same)

It edits source as well as built HTML, because a link living in a .py template
or a .md source would simply come back on the next build.

Only exact href/markdown-target forms are rewritten, so no prose containing the
words is touched. Timestamped backups per changed file. Safe to re-run.

  python3 fix-broken-links.py            report what would change, write nothing
  python3 fix-broken-links.py --apply    make the changes

Also reports where the Parker Knoll "worked example" anchor is generated, so the
missing space in the anchor text can be fixed at source.
"""

import datetime
import os
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
APPLY = "--apply" in sys.argv

EXTS = {".html", ".py", ".md", ".json", ".txt", ".js"}
SKIP_DIRS = {".git", "node_modules", "assets", "images", ".wrangler",
             "__pycache__", "backups", "dist"}
SKIP_NAMES = {"link-audit.txt", "fix-broken-links.py", "audit-internal-links.py"}

# (old, new) - exact token forms only
RULES = []
for old, new in (("/our-work", "/projects/#gallery"),
                 ("/press-pack.html", "/press-pack"),
                 ("/buy-the-book.html", "/buy-the-book")):
    RULES += [
        ('href="%s"' % old, 'href="%s"' % new),
        ("href='%s'" % old, "href='%s'" % new),
        ('"https://www.learntoupholster.com%s"' % old,
         '"https://www.learntoupholster.com%s"' % new),
        ("](%s)" % old, "](%s)" % new),
    ]

ANCHOR_HINT = re.compile(r"[Ww]orked example", re.S)


def walk():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if fn in SKIP_NAMES or fn.endswith(".bak") or ".bak-" in fn:
                continue
            p = pathlib.Path(dirpath) / fn
            if p.suffix.lower() in EXTS:
                yield p


def main():
    changed = {}
    hints = []
    for p in walk():
        try:
            s = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        if p.suffix in (".py", ".html") and ANCHOR_HINT.search(s):
            for m in ANCHOR_HINT.finditer(s):
                a, b = max(0, m.start() - 90), min(len(s), m.end() + 90)
                hints.append((p.relative_to(ROOT).as_posix(),
                              re.sub(r"\s+", " ", s[a:b]).strip()))

        hits = {}
        out = s
        for old, new in RULES:
            c = out.count(old)
            if c:
                hits[old] = hits.get(old, 0) + c
                out = out.replace(old, new)
        if hits:
            changed[p] = (hits, out)

    if not changed:
        print("Nothing to fix - all three targets are already clean.")
    else:
        total = sum(sum(h.values()) for h, _ in changed.values())
        print("%d replacement%s across %d file%s%s\n"
              % (total, "" if total == 1 else "s", len(changed),
                 "" if len(changed) == 1 else "s",
                 "" if APPLY else "   (dry run - nothing written)"))
        for p in sorted(changed):
            hits, out = changed[p]
            rel = p.relative_to(ROOT).as_posix()
            detail = ", ".join("%s x%d" % (k, v) for k, v in sorted(hits.items()))
            print("  %-46s %s" % (rel, detail))
            if APPLY:
                shutil.copy2(p, p.with_name(p.name + ".bak-" + STAMP))
                p.write_text(out, encoding="utf-8")

    if hints:
        print("\n'worked example' anchor is generated here - check for the")
        print("missing space before the project title:")
        seen = set()
        for rel, ctx in hints:
            if rel in seen:
                continue
            seen.add(rel)
            print("\n  %s" % rel)
            print("    ...%s..." % ctx[:170])

    if changed and not APPLY:
        print("\nre-run with --apply to write the changes.")
    elif changed and APPLY:
        print("\ndone. rebuild and redeploy to publish.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
prune-stale-project-blocks.py
-----------------------------
Removes "See it in practice" blocks from pages that are no longer in
link-projects.py's MAP.

link-projects.py only ever visits pages currently in its map, so a page dropped
from the map keeps its block forever - never refreshed, never removed, still
pointing at whichever project was live when it was written. That is why 53
pages, including every business article and every blog post, carry a card
saying the Parker Knoll wing chair is a worked example of them.

The authoritative map is read straight out of link-projects.py with ast, not
copied here, so the two can't drift. link-projects.py is parsed, never executed
- it writes files at import time.

  python3 prune-stale-project-blocks.py           list what would go
  python3 prune-stale-project-blocks.py --apply   remove it

Project pages carry a different marker and are never touched.
"""

import ast
import datetime
import os
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "link-projects.py"
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
APPLY = "--apply" in sys.argv

MARK_CHAP = "<!-- worked-example -->"
BLOCK = re.compile(r'\n?<hr class="seam">\n<section class="wrap read">\n  '
                   + re.escape(MARK_CHAP) + r'.*?</section>\n', re.S)
SKIP_DIRS = {".git", "node_modules", "assets", "images", ".wrangler",
             "__pycache__", "backups", "dist", "projects"}


def load_map():
    """Pull MAP out of link-projects.py without running it."""
    if not SRC.exists():
        sys.exit("ABORT: link-projects.py not found - run from ~/learntoupholster.")
    tree = ast.parse(SRC.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "MAP":
                    return ast.literal_eval(node.value)
    sys.exit("ABORT: no MAP assignment found in link-projects.py.")


def main():
    mapping = load_map()
    live = set()
    for chaps in mapping.values():
        live.update(chaps)
    print("link-projects.py maps %d projects onto %d chapter pages:"
          % (len(mapping), len(live)))
    print("  " + ", ".join(sorted(live)) + "\n")

    marked, stale = [], []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if not fn.endswith(".html") or ".bak-" in fn:
                continue
            p = pathlib.Path(dirpath) / fn
            try:
                s = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if MARK_CHAP not in s:
                continue
            marked.append(p)
            rel = p.relative_to(ROOT).as_posix()
            slug = rel[:-5]
            if slug not in live:
                stale.append((p, s, rel))

    print("pages carrying the marker: %d" % len(marked))
    print("of those, still in the map: %d" % (len(marked) - len(stale)))
    print("stale, to remove:           %d%s\n"
          % (len(stale), "" if APPLY else "   (dry run - nothing written)"))

    if not stale:
        print("Nothing to prune.")
        return

    failed = 0
    for p, s, rel in sorted(stale, key=lambda x: x[2]):
        target = re.search(r'href="(/projects/[^"]+)"', BLOCK.search(s).group(0)) \
            if BLOCK.search(s) else None
        if not BLOCK.search(s):
            print("  !! %-52s marker present but block shape unrecognised" % rel)
            failed += 1
            continue
        print("  %-52s -> %s" % (rel, target.group(1) if target else "?"))
        if APPLY:
            out, n = BLOCK.subn("", s, count=1)
            if MARK_CHAP in out:
                print("     !! marker still present after removal, skipped")
                failed += 1
                continue
            shutil.copy2(p, p.with_name(p.name + ".bak-" + STAMP))
            p.write_text(out, encoding="utf-8")

    if failed:
        print("\n%d file(s) left untouched - inspect those by hand." % failed)
    if not APPLY:
        print("\nre-run with --apply to remove them.")
    else:
        print("\ndone. %d block(s) removed. Deploy as usual - no rebuild needed."
              % (len(stale) - failed))
        print("Re-running link-projects.py will not bring them back: it only")
        print("writes to pages in MAP.")


if __name__ == "__main__":
    main()

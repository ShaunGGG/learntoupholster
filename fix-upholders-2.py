#!/usr/bin/env python3
"""
fix-upholders-2.py
------------------
The three items fix-upholders.py flagged but would not change on its own,
because they are editorial rather than mechanical. All three are wrong on the
facts as the Company states them, and all three sit on pages a reader would
check.

1. HISTORY CHAPTER - "the Upholders' Company chartered (1465)"
   1465 is the grant of arms under Edward IV. The Royal Charter is 1626,
   granted by Charles I on 14 June, destroyed in the 1666 Fire and
   re-exemplified by Charles II in 1668. 2026 is its 400th anniversary.
   Changed to 1626, which keeps the entry first in the eight-event sequence.

2. STANDARDS PAGE - "More ceremonial than operational today"
   Their Trade and Education Committee sits on the Fire Retardancy Regulations
   board and the T-Level Education scheme, visits AMUSF centres, runs six award
   and bursary schemes and publishes a newsletter.

3. STANDARDS PAGE - "membership for senior upholsterers is by invitation"
   Plainly wrong. They describe themselves as an Open Company: you need not
   work in the trade to join, and they offer preferential rates to those who
   do, saying they actively seek trade members.

Items 2 and 3 are replaced together, as one sentence pair, in the register of
the surrounding paragraph.

  python3 fix-upholders-2.py           show what would change
  python3 fix-upholders-2.py --apply   make the changes
"""

import datetime
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
APPLY = "--apply" in sys.argv

EDITS = [
    ("a-brief-opinionated-history-of-upholstery.html",
     "Company chartered (1465)",
     "Company chartered (1626)",
     "1465 is the grant of arms; the charter is 1626",
     True),   # replace every occurrence - it appears in prose and in the
              # figure caption, and they must not disagree

    ("standards-regulations-and-bibliography.html",
     "More ceremonial than operational today, it maintains scholarship funds "
     "for training upholsterers and runs annual awards. Worth knowing about; "
     "membership for senior upholsterers is by invitation.",
     "It is an open company &#8212; you need not work in the trade to join, "
     "and it offers preferential rates to those who do. Its Trade and "
     "Education Committee runs awards and bursaries for students and working "
     "upholsterers, and is represented on the fire retardancy and T-Level "
     "education bodies. Worth knowing about, and worth joining if the City "
     "side of the trade interests you.",
     "corrects 'ceremonial' and the membership claim",
     False),
]


def main():
    print("CORRECTIONS%s\n" % ("" if APPLY else "   (dry run - nothing written)"))
    total = 0
    touched = {}

    for fname, old, new, why, replace_all in EDITS:
        p = ROOT / fname
        if not p.exists():
            print("  !! %-46s file not found" % fname)
            continue
        s = touched.get(fname) or p.read_text(encoding="utf-8")
        n = s.count(old)
        if n == 0:
            print("  -- %-46s already correct, or text has changed" % fname)
            continue
        if n > 1 and not replace_all:
            print("  !! %-46s matches %d times, expected 1 - skipped"
                  % (fname, n))
            continue
        print("  %s   (%d occurrence%s)" % (fname, n, "" if n == 1 else "s"))
        print("       why: %s" % why)
        print("       -   %s" % old[:110])
        print("       +   %s" % new[:110])
        print()
        touched[fname] = s.replace(old, new)
        total += n

    if APPLY:
        for fname, content in touched.items():
            p = ROOT / fname
            shutil.copy2(p, p.with_name(p.name + ".bak-" + STAMP))
            p.write_text(content, encoding="utf-8")

    print("%d change(s)%s." % (total, "" if APPLY else " to make"))

    # anything left that still says 1465 anywhere
    print("\nREMAINING MENTIONS OF 1465")
    print("-" * 66)
    hits = 0
    for p in sorted(ROOT.rglob("*.html")):
        if ".bak-" in p.name:
            continue
        rel = p.relative_to(ROOT).as_posix()
        s = touched.get(rel) or p.read_text(encoding="utf-8", errors="replace")
        c = s.count("1465")
        if c:
            print("  %-46s x%d" % (rel, c))
            hits += c
    if not hits:
        print("  none")
    else:
        print("\n  1465 is still correct wherever it refers to the grant of")
        print("  arms. Check each before changing it.")

    if total and not APPLY:
        print("\nre-run with --apply to make the changes.")
    elif total and APPLY:
        print("\ndone. rebuild and redeploy.")


if __name__ == "__main__":
    main()

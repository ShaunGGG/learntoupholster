#!/usr/bin/env python3
"""
fix-upholders.py
----------------
Corrects references to the Worshipful Company of Upholders.

Two errors, verified against the Company's own history page
(upholders.co.uk/history and /circle-of-life/history-and-charters):

1. NAME. Four pages call them the "Worshipful Company of Upholsterers".
   There is no such company. It is the Worshipful Company of UPHOLDERS -
   "Upholder" being the older word from which "upholstery" descends.

2. DATE. 1465 is a real date in their history, but it is the grant of the
   Coat of Arms under Edward IV. It is not the founding and not the charter.
   The Company's own dates:
       1360  Wardens elected to survey and govern the men of the mistery
       1465  grant of arms
       1474  granted the right to search and seize wares not truly made
       1626  Royal Charter, Charles I (14 June); lost in the 1666 Fire,
             re-exemplified by Charles II in 1668
   The "1474 ordinances" cited in the toolkit chapter are CORRECT and are
   left alone.

Two further items are only reported, not changed - they are editorial
judgements rather than factual errors. See the notes printed at the end.

  python3 fix-upholders.py           show what would change
  python3 fix-upholders.py --apply   make the changes
"""

import datetime
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
APPLY = "--apply" in sys.argv

# (file, old, new, why)
EDITS = [
    ("a-z-glossary.html",
     '<p id="g-worshipful-company-of-upholsterers"><strong>Worshipful Company '
     'of Upholsterers.</strong> The London livery company that has governed '
     'the upholstery trade since 1465.</p>',
     '<p id="g-worshipful-company-of-upholders"><strong>Worshipful Company '
     'of Upholders.</strong> The London livery company that has governed '
     'the upholstery trade since 1360.</p>',
     "glossary entry - the definition readers trust most"),

    ("a-z-glossary.html",
     '"@id":"https://www.learntoupholster.com/a-z-glossary'
     '#g-worshipful-company-of-upholsterers","name":"Worshipful Company of '
     'Upholsterers","description":"The London livery company that has '
     'governed the upholstery trade since 1465."',
     '"@id":"https://www.learntoupholster.com/a-z-glossary'
     '#g-worshipful-company-of-upholders","name":"Worshipful Company of '
     'Upholders","description":"The London livery company that has '
     'governed the upholstery trade since 1360."',
     "JSON-LD DefinedTerm - the structured data Google reads"),

    ("glossary.json",
     '"term": "Worshipful Company of Upholsterers",\n'
     '  "def": "The London livery company that has governed the upholstery '
     'trade since 1465.",\n'
     '  "href": "/a-z-glossary#g-worshipful-company-of-upholsterers"',
     '"term": "Worshipful Company of Upholders",\n'
     '  "def": "The London livery company that has governed the upholstery '
     'trade since 1360.",\n'
     '  "href": "/a-z-glossary#g-worshipful-company-of-upholders"',
     "tooltip source - href must match the new A-Z anchor"),

    ("pricing-and-quoting.html",
     "set by the Worshipful Company of Upholsterers (founded 1465)",
     "set by the Worshipful Company of Upholders (founded 1360)",
     "name + founding date"),

    ("customers-and-the-workshop-year.html",
     "The Worshipful Company of Upholsterers (founded 1465)",
     "The Worshipful Company of Upholders (founded 1360)",
     "name + founding date"),

    ("standards-regulations-and-bibliography.html",
     "<p><strong>The Worshipful Company of Upholsterers</strong> is the City "
     "of London livery company that has governed the trade since 1465.",
     "<p><strong>The Worshipful Company of Upholders</strong> is the City "
     "of London livery company that has governed the trade since 1360.",
     "name + founding date"),
]

# reported only - your call, not mine
NOTES = [
    ("a-brief-opinionated-history-of-upholstery.html",
     "Company chartered (1465)",
     "1465 is the grant of arms, not the charter. The charter is 1626 "
     "(Charles I). Either 'chartered (1626)' or 'founded (1360)' works, and "
     "both still sit first in your eight-event sequence \u2014 but which one "
     "you want depends on the point the sequence is making, so I have not "
     "chosen for you. Note 2026 is the 400th anniversary of the 1626 charter."),

    ("standards-regulations-and-bibliography.html",
     "More ceremonial than operational today",
     "Their Trade & Education Committee sits on the Fire Retardancy "
     "Regulations board and the T-Level Education scheme, visits AMUSF "
     "centres, runs six award and bursary schemes and publishes a newsletter. "
     "'Ceremonial' is arguable but they would not recognise it."),

    ("standards-regulations-and-bibliography.html",
     "membership for senior upholsterers is by invitation",
     "They describe themselves as an 'Open Company' \u2014 you need not work "
     "in the trade to join, and they encourage anyone in the crafts to become "
     "Liverymen or Freemen at preferential rates. This one is simply wrong "
     "and is worth correcting before you write to them."),
]


def main():
    print("CORRECTIONS%s\n" % ("" if APPLY else "   (dry run - nothing written)"))
    done = failed = 0
    touched = {}

    for fname, old, new, why in EDITS:
        p = ROOT / fname
        if not p.exists():
            print("  !! %-46s file not found" % fname)
            failed += 1
            continue
        s = touched.get(fname) or p.read_text(encoding="utf-8")
        n = s.count(old)
        if n == 0:
            print("  -- %-46s already correct, or text has changed" % fname)
            continue
        print("  %-46s %s" % (fname, why))
        print("       - %s" % old[:96])
        print("       + %s" % new[:96])
        touched[fname] = s.replace(old, new)
        done += n

    # any stray uses of the wrong name we did not target explicitly
    print("\nREMAINING USES OF THE WRONG NAME")
    print("-" * 66)
    stray = 0
    for p in sorted(ROOT.rglob("*.html")):
        if ".bak-" in p.name:
            continue
        rel = p.relative_to(ROOT).as_posix()
        s = touched.get(rel) or p.read_text(encoding="utf-8", errors="replace")
        c = s.count("Company of Upholsterers")
        if c:
            print("  %-46s x%d" % (rel, c))
            stray += c
    if not stray:
        print("  none")

    if APPLY:
        for fname, content in touched.items():
            p = ROOT / fname
            shutil.copy2(p, p.with_name(p.name + ".bak-" + STAMP))
            p.write_text(content, encoding="utf-8")

    print("\n%d correction(s)%s." % (done, "" if APPLY else " to make"))

    print("\nWRONG NAME IN SOURCE FILES (a rebuild would undo the fix)")
    print("-" * 66)
    src = 0
    for ext in ("*.py", "*.md", "*.json", "*.txt"):
        for q in sorted(ROOT.rglob(ext)):
            if ".bak-" in q.name or q.name == "fix-upholders.py":
                continue
            try:
                t = q.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            c = t.count("Company of Upholsterers")
            if c:
                print("  %-46s x%d" % (q.relative_to(ROOT).as_posix(), c))
                src += c
    if not src:
        print("  none - the HTML is the source, edits will stick")

    print("\nFOR YOU TO DECIDE - not changed")
    print("=" * 66)
    for fname, quote, note in NOTES:
        p = ROOT / fname
        present = p.exists() and quote in p.read_text(encoding="utf-8",
                                                      errors="replace")
        print("\n  %s" % fname)
        print("  \u201c%s\u201d%s" % (quote, "" if present else "   [NOT FOUND - may already be edited]"))
        print("     %s" % note)

    if not APPLY and done:
        print("\n\nre-run with --apply to make the corrections above.")


if __name__ == "__main__":
    main()

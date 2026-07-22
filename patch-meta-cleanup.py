#!/usr/bin/env python3
"""
patch-meta-cleanup.py — final tidy from the July 2026 re-audit.

Replaces meta descriptions that were still truncated or over-long with
purpose-written versions (<=160 chars, keyword front-loaded). Also syncs
each page's Article schema "description" to match. Idempotent.

Run once from repo root, then deploy (no rebuild step needed — edits pages
directly). Preview with --dry-run.
"""
import re, os, sys, glob

DRY = "--dry-run" in sys.argv
os.chdir(os.path.dirname(os.path.abspath(__file__)))

META = {
 "the-anatomy-of-an-upholstered-piece":
   "A shared vocabulary for every part of an upholstered chair: the outside panels, the seat and its edges, and how a traditional build differs from a modern one.",
 "projects/parker-knoll-wing-chair":
   "Restoring a Parker Knoll wing chair: a sound hardwood frame stripped back from tired brown mohair and rebuilt, with the full re-cover shown stage by stage.",
 "projects/kawasaki-motorbike-seat":
   "Reshaping and re-covering a classic Kawasaki seat: flattening the stepped stock profile and building a new foam shape, then covering it in marine vinyl.",
 "projects/modern-wing-chair":
   "Building a wing chair new from the bare frame: a modern elasticated-webbing and foam build, no stripping or old cover to copy, shown from frame to finish.",
 "projects/fluted-chair":
   "Covering a modern fluted-back chair in three clean movements: the arms, the fluted inside back, and the outside. A study in economical modern upholstery.",
 "projects/renault-twizy-seat-wrap":
   "Wrapping bare Renault Twizy seat pads: making covers for the factory self-skinned foam shells, with contact adhesive on the faces and staples at the edges.",
}

n = 0
for stem, new in META.items():
    f = stem + ".html"
    if not os.path.exists(f):
        print(f"  skip (missing): {f}"); continue
    html = open(f, encoding="utf-8").read()
    orig = html
    html = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="%s">' % new, html, count=1)
    # sync Article schema description
    html = re.sub(r'("@type": "Article"[^}]*?"description": ")[^"]*(")',
                  lambda m: m.group(1) + new + m.group(2), html, count=1)
    if html != orig:
        n += 1
        if not DRY:
            open(f, "w", encoding="utf-8").write(html)
        print(f"  {'would fix' if DRY else 'fixed'}: /{stem} ({len(new)} chars)")

print(f"\n{'DRY RUN — ' if DRY else ''}{n} descriptions {'to update' if DRY else 'updated'}.")

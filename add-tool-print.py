#!/usr/bin/env python3
"""
Adds the shared toolprint.js to each calculator page (before </body>).
Safe to run repeatedly. Run from your project root:
    cd ~/learntoupholster && python3 add-tool-print.py
"""
import pathlib, sys
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
PAGES = ["fabric-yardage.html","reupholstery-cost-calculator.html",
         "deep-buttoning-calculator.html","foam-cushion-calculator.html",
         "leather-hide-calculator.html"]
TAG = '<script src="/toolprint.js" defer></script>'
changed = skipped = missing = 0
for name in PAGES:
    p = ROOT / name
    if not p.exists():
        print(f"  ! not found: {name}"); missing += 1; continue
    t = p.read_text(encoding="utf-8")
    if "toolprint.js" in t:
        print(f"  = already has it: {name}"); skipped += 1; continue
    if "</body>" in t:
        t = t.replace("</body>", "  " + TAG + "\n</body>", 1)
    else:
        t = t + "\n" + TAG + "\n"
    p.write_text(t, encoding="utf-8")
    print(f"  + patched: {name}"); changed += 1
print(f"\nDone. {changed} patched, {skipped} already had it, {missing} missing.")

#!/usr/bin/env python3
"""
ltu-print-orange.py
-------------------
Makes the contract checker's "Print it" button terracotta, so it matches the
print button on the domestic checker. "Create the record" stays green.

Safe to re-run. Writes a .bak3 backup.
"""

import re
import shutil
import sys
from pathlib import Path

PAGE = Path("fire-safety-checker.html")

OLD = ".cc-btns .cc-ghost{background:transparent;color:var(--green,#2F4A3A)}"
NEW = (".cc-btns .cc-ghost{background:var(--terracotta,#B5552D);"
       "color:var(--cream,#FBF6ED);border-color:var(--terracotta,#B5552D)}")

# focus ring should sit against the new colour too
OLD_FOCUS = ".cc-btns button:focus-visible{outline:2px solid var(--gold,#C19A4B);outline-offset:2px}"
NEW_FOCUS = (".cc-btns button:focus-visible{outline:2px solid var(--ink,#2A2622);outline-offset:2px}")


def main():
    if not PAGE.exists():
        sys.exit("ERROR: fire-safety-checker.html not found. Run from the repo root.")

    html = PAGE.read_text(encoding="utf-8")

    if "id=\"cc-checker\"" not in html:
        sys.exit("ERROR: the contract checker isn't on this page. "
                 "Run add-commercial-checker.py first.")

    if NEW in html:
        print("Already applied — the print button is already terracotta.")
        return

    if OLD not in html:
        # be helpful about why
        m = re.search(r"\.cc-btns \.cc-ghost\{[^}]*\}", html)
        print("STOPPED — could not find the expected button rule.")
        if m:
            print("  Found instead:", m.group(0))
            print("  Nothing changed. Paste that line and it can be retargeted.")
        else:
            print("  No .cc-ghost rule found at all.")
        sys.exit(1)

    shutil.copy2(PAGE, PAGE.with_suffix(".html.bak3"))

    out = html.replace(OLD, NEW, 1)
    if OLD_FOCUS in out:
        out = out.replace(OLD_FOCUS, NEW_FOCUS, 1)

    PAGE.write_text(out, encoding="utf-8")
    print("Print button is now terracotta (var(--terracotta), #B5552D fallback).")
    print("  • 'Create the record' stays green")
    print("  • focus ring switched to ink so it stays visible against orange")
    print("  • backup: fire-safety-checker.html.bak3")


if __name__ == "__main__":
    main()

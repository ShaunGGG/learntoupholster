#!/usr/bin/env python3
"""
fix-adstxt.py — make https://learntoupholster.com/ads.txt return 200 directly.

AdSense has the site registered at the apex and reports "Ads.txt status: Not
found" because the apex -> www redirect swallows /ads.txt before the file is
ever served.

This script does two things, both idempotent:

  1. Ensures public/ads.txt exists with the correct single line.
  2. If the apex -> www redirect lives in a _redirects file, inserts an
     exemption for /ads.txt ABOVE it. Cloudflare Pages takes the first
     matching rule, so order is what makes this work.

DRY RUN BY DEFAULT. Nothing is written unless you pass --apply.

If the redirect is NOT in the repo, the script says so and stops. That means
it is a zone-level Redirect Rule, Bulk Redirect or Page Rule, and it has to be
changed in the Cloudflare dashboard -- a script has no business guessing at
zone config it cannot see.
"""

import sys
import shutil
import re
from datetime import datetime
from pathlib import Path

ADS_LINE = "google.com, pub-3728586174960711, DIRECT, f08c47fec0942fa0"
EXEMPT = "https://learntoupholster.com/ads.txt  /ads.txt  200"
MARKER = "# ads.txt must not redirect - AdSense checks the apex"

APPLY = "--apply" in sys.argv
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

changes = []
notes = []


def backup(p: Path):
    b = p.with_name(f"{p.name}.{STAMP}.bak")
    if APPLY:
        shutil.copy2(p, b)
    changes.append(f"  backup -> {b}")


# ---------------------------------------------------------------- ads.txt ---
root = Path.cwd()
candidates = [root / "public" / "ads.txt", root / "static" / "ads.txt"]
existing = [p for p in candidates if p.exists()]

if existing:
    p = existing[0]
    current = p.read_text(encoding="utf-8").strip()
    if current == ADS_LINE:
        notes.append(f"ads.txt      OK, already correct at {p.relative_to(root)}")
    else:
        changes.append(f"REWRITE {p.relative_to(root)}")
        changes.append(f"  was: {current!r}")
        changes.append(f"  now: {ADS_LINE!r}")
        backup(p)
        if APPLY:
            p.write_text(ADS_LINE + "\n", encoding="utf-8")
else:
    target = root / "public" / "ads.txt"
    if not target.parent.is_dir():
        print(f"ABORT: {target.parent} does not exist -- am I in the repo root?")
        sys.exit(1)
    changes.append(f"CREATE {target.relative_to(root)}  ({ADS_LINE})")
    if APPLY:
        target.write_text(ADS_LINE + "\n", encoding="utf-8")

# -------------------------------------------------------------- _redirects ---
redirect_files = [
    p for p in root.rglob("_redirects")
    if "node_modules" not in p.parts and ".git" not in p.parts
]

if not redirect_files:
    notes.append(
        "_redirects   none in repo -- the apex redirect is zone-level.\n"
        "             Fix it in Cloudflare: Rules -> Redirect Rules, add\n"
        '               and not (http.request.uri.path eq "/ads.txt")\n'
        "             to the rule expression. Nothing here can do it for you."
    )
else:
    # The apex rule: matches the bare host being sent to www.
    apex_re = re.compile(
        r"^\s*(https?://)?learntoupholster\.com(/\*|/:splat|/.*)?\s+\S*www\.learntoupholster\.com",
        re.I,
    )
    for p in redirect_files:
        lines = p.read_text(encoding="utf-8").splitlines()
        if any(EXEMPT.split()[0] in ln and "/ads.txt" in ln for ln in lines):
            notes.append(f"_redirects   OK, exemption already present in {p.relative_to(root)}")
            continue

        idx = next((i for i, ln in enumerate(lines) if apex_re.match(ln)), None)
        if idx is None:
            notes.append(
                f"_redirects   {p.relative_to(root)} exists but has no apex->www rule.\n"
                "             Anchor missing, so nothing written. Check by hand."
            )
            continue

        changes.append(f"PATCH {p.relative_to(root)}")
        changes.append(f"  inserting exemption above line {idx + 1}: {lines[idx].strip()}")
        backup(p)
        lines[idx:idx] = [MARKER, EXEMPT, ""]
        if APPLY:
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")

# ------------------------------------------------------------------ report ---
print("=" * 66)
print("fix-adstxt.py — " + ("APPLYING" if APPLY else "DRY RUN (nothing written)"))
print("=" * 66)
for n in notes:
    print(n)
if notes and changes:
    print()
if changes:
    print("\n".join(changes))
else:
    print("\nNo changes needed.")
if not APPLY and changes:
    print("\nRe-run with --apply to write these.")

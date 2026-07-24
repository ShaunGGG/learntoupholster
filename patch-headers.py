#!/usr/bin/env python3
"""
patch-headers.py  —  learntoupholster.com

Adds iframe protection to the LICENSED fire-safety-checker only, while
leaving everything else exactly as it is.

WHY A PATCH AND NOT A NEW FILE
------------------------------
Your live _headers is already doing real work: the RFC 9727 api-catalog
Link header, nosniff, referrer-policy, and 30-day caching on /assets.
Overwriting it would quietly undo the agent-readiness work. This script
reads what is there, changes one thing, and backs up the original first.

Safe to run twice — it updates its own block rather than stacking copies.
"""

import os
import re
import shutil
import sys
from datetime import datetime

HEADERS = "_headers"
MARKER = "# >>> frame-protection (managed) >>>"
END = "# <<< frame-protection (managed) <<<"

BLOCK = f"""{MARKER}
# Licensed embed: AMUSF only.
#
# Deliberately NO X-Frame-Options here. XFO understands only DENY and
# SAMEORIGIN — its ALLOW-FROM was dropped years ago — so setting it would
# block the very people paying for this. frame-ancestors is the only
# directive that can allowlist a third party.
#
# Their apex has no DNS (www-only), so both forms are listed.
# Add one origin per licensee as you sell more seats.
/fire-safety-checker
  Content-Security-Policy: frame-ancestors 'self' https://amusf.org.uk https://*.amusf.org.uk

# Future embed routes: open to everyone, because you WANT these travelling.
/embed/*
  Content-Security-Policy: frame-ancestors *
{END}
"""


def main() -> int:
    if not os.path.exists(HEADERS):
        print(f"✘ No {HEADERS} found in {os.getcwd()}")
        print("  Run this from ~/learntoupholster (the folder you deploy from).")
        return 1

    original = open(HEADERS, encoding="utf-8").read()

    # ---- Safety check: would our CSP collide with an existing one? -----
    # Cloudflare JOINS duplicate headers with a comma rather than
    # overriding, which produces an invalid value and silently blocks
    # framing. Warn loudly rather than ship a broken deploy.
    catchall = re.search(
        r"^/\*\s*$\n((?:[ \t]+.*\n?)*)", original, re.MULTILINE
    )
    if catchall:
        body = catchall.group(1).lower()
        for bad in ("content-security-policy", "x-frame-options"):
            if bad in body and "!" not in body.split(bad)[0].split("\n")[-1]:
                print(f"⚠ Your /* block already sets {bad}.")
                print("  Adding another would produce a comma-joined, invalid")
                print("  header. Paste your _headers back to me before deploying.")
                return 1

    # ---- Back up ------------------------------------------------------
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = f"{HEADERS}.bak-{stamp}"
    shutil.copy2(HEADERS, backup)

    # ---- Insert or refresh our managed block --------------------------
    if MARKER in original:
        updated = re.sub(
            re.escape(MARKER) + r".*?" + re.escape(END) + r"\n?",
            BLOCK,
            original,
            flags=re.DOTALL,
        )
        action = "updated existing"
    else:
        updated = original.rstrip("\n") + "\n\n" + BLOCK
        action = "appended new"

    open(HEADERS, "w", encoding="utf-8").write(updated)

    # ---- Report -------------------------------------------------------
    preserved = len(re.findall(r"^\S", original, re.MULTILINE))
    print(f"✔ {action} frame-protection block in {HEADERS}")
    print(f"✔ backup written to {backup}")
    print(f"✔ {preserved} existing rule line(s) left untouched")
    if "api-catalog" in updated:
        print("✔ api-catalog Link header still present")
    print()
    print("Now deploy. After it lands, confirm with:")
    print("  curl -sI https://www.learntoupholster.com/fire-safety-checker | grep -i frame")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
patch-ahrefs-analytics.py  —  add Ahrefs Web Analytics to every page

USAGE (key is an argument, because each site has its OWN key):

    python3 patch-ahrefs-analytics.py mnyaNgC9ZMkTWzH2ITb6pQ

⚠️  ONE KEY PER SITE. Ahrefs Web Analytics is configured with a single
project key per property. If you paste the Learn to Upholster key onto
Greenwood as well, both sites report into one bucket and neither number
means anything. Get Greenwood's own key from its project in Ahrefs and
run this again inside that repo with that key.

Walks the current directory recursively, inserts the tag immediately
before </head> in every .html file that doesn't already have it.
Safe to run twice — it skips pages already carrying the tag.
"""

import os
import re
import sys

TAG_TEMPLATE = (
    '<script src="https://analytics.ahrefs.com/analytics.js" '
    'data-key="{key}" async></script>'
)

SKIP_DIRS = {".git", "node_modules", "assets", ".wrangler", "functions"}


def main() -> int:
    if len(sys.argv) != 2:
        print("✘ Usage: python3 patch-ahrefs-analytics.py <YOUR_SITE_KEY>")
        print("  Each site has its own key — don't reuse one across sites.")
        return 1

    key = sys.argv[1].strip()
    if len(key) < 10 or " " in key:
        print(f"✘ '{key}' doesn't look like an Ahrefs key. Stopping.")
        return 1

    if not os.path.exists("index.html"):
        print(f"✘ No index.html in {os.getcwd()} — is this the site root?")
        return 1

    tag = TAG_TEMPLATE.format(key=key)

    patched, already, nohead = 0, 0, []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in sorted(files):
            if not name.endswith(".html"):
                continue
            path = os.path.join(root, name)
            html = open(path, encoding="utf-8", errors="ignore").read()

            if "analytics.ahrefs.com" in html:
                already += 1
                continue

            # Match </head> case-insensitively; keep the original casing.
            m = re.search(r"</head\s*>", html, re.I)
            if not m:
                nohead.append(path)
                continue

            html = html[: m.start()] + "  " + tag + "\n" + html[m.start():]
            open(path, "w", encoding="utf-8").write(html)
            patched += 1

    print(f"✔ tag added to {patched} page(s)")
    if already:
        print(f"✔ {already} page(s) already had it — skipped")
    if nohead:
        print(f"⚠ {len(nohead)} file(s) had no </head> and were left alone:")
        for p in nohead[:5]:
            print(f"    {p}")
    print()
    print(f"  key used: {key}")
    print("  Deploy, then load any page and check Ahrefs — events appear")
    print("  within about a minute.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

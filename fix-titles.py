#!/usr/bin/env python3
"""
fix-titles.py — drop the brand suffix from titles that are already long.

The crawl found 66 titles over 60 rendered characters. Nearly all follow
[Topic] - [subtitle] | Learn to Upholster, and the 21-character suffix is
what pushes them past where Google truncates. The brand still shows in the
URL and the sitelink, so dropping it on long titles costs nothing.

Adds a shared helper and rewires the three build scripts to use it.
Entities are decoded before measuring: &amp; is 5 chars in source but 1 on
screen, and measuring the source overstates the problem.

DRY RUN by default. Pass --apply to write.
"""
import os, re, sys, shutil
from datetime import datetime

APPLY = "--apply" in sys.argv
ROOT = os.path.expanduser("~/learntoupholster")
LIMIT = 60
SUFFIX = " | Learn to Upholster"

HELPER = '''

# --- title length helper (added by fix-titles.py) ---------------------
import html as _html, re as _re

def brand_title(title, limit=%d):
    """Append the brand suffix only when the result still fits in a SERP.

    Measured on the RENDERED length: &amp; is one character on screen even
    though it is five in source. Titles that are already long keep their
    own words and lose the suffix, which is the less useful half.
    """
    plain = _re.sub(r'<[^>]+>', '', _html.unescape(str(title)))
    if len(plain) + %d <= limit:
        return "%%s%s" %% title
    return title
# ----------------------------------------------------------------------
''' % (LIMIT, len(SUFFIX), SUFFIX)

TARGETS = [
    ("build-blog.py",
     r"f'<title>\{e\(title\)\} \| Learn to Upholster</title>'",
     "f'<title>{brand_title(e(title))}</title>'"),
    ("build-projects.py",
     r'f"\{title\} &#8212; Upholstery Project \| Learn to Upholster"',
     'brand_title(f"{title} &#8212; Upholstery Project")'),
    ("build-projects.py",
     r'"Upholstery Projects &#8212; Real Jobs, Documented \| Learn to Upholster"',
     'brand_title("Upholstery Projects &#8212; Real Jobs, Documented")'),
    ("build-business.py",
     r"'<title>%s \| Learn to Upholster</title>' % html\.escape\(title\)",
     "'<title>%s</title>' % brand_title(html.escape(title))"),
]

os.chdir(ROOT)
print("mode :", "APPLY" if APPLY else "DRY RUN (pass --apply to write)")
print()

edits = {}
for fn, pattern, repl in TARGETS:
    if not os.path.isfile(fn):
        print("  ! missing:", fn); continue
    text = edits.get(fn) or open(fn, encoding="utf-8").read()
    if re.search(pattern, text):
        text = re.sub(pattern, repl.replace("\\", "\\\\"), text, count=1)
        edits[fn] = text
        print("  + %-20s suffix now conditional" % fn)
    else:
        print("  ? %-20s pattern not found -- check by hand" % fn)
        print("      looking for: %s" % pattern[:70])

for fn in list(edits):
    if "def brand_title" not in edits[fn]:
        lines = edits[fn].split("\n")
        i = 0
        for n, l in enumerate(lines[:40]):
            if l.startswith("import ") or l.startswith("from "):
                i = n + 1
        lines.insert(i, HELPER)
        edits[fn] = "\n".join(lines)
        print("  + %-20s helper added" % fn)

if not edits:
    print("\nNothing to do.")
    sys.exit(0)

if APPLY:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    bdir = os.path.expanduser("~/ltu-backups")
    os.makedirs(bdir, exist_ok=True)
    ok = True
    for fn, text in edits.items():
        shutil.copy2(fn, os.path.join(bdir, fn + ".bak-" + stamp))
        open(fn, "w", encoding="utf-8").write(text)
    import py_compile
    for fn in edits:
        try:
            py_compile.compile(fn, doraise=True)
            print("  syntax ok:", fn)
        except Exception as e:
            print("  SYNTAX FAILED:", fn, e)
            shutil.copy2(os.path.join(bdir, fn + ".bak-" + stamp), fn)
            print("  rolled back:", fn); ok = False
    print("\nWritten." if ok else "\nRolled back.")
    print("Now rebuild:  python3 build-blog.py && python3 build-projects.py && python3 build-business.py")
    print("Then:         ltu-deploy")
else:
    print("\nNothing written. Re-run with --apply.")

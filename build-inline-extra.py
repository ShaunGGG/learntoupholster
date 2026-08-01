#!/usr/bin/env python3
"""
build-inline-extra.py — push the current inlined CSS into subdirectory pages.

build-inline.py works on the site root, so anything under business/, projects/
or state-of-the-trade/ keeps whatever stylesheet was current when that page was
generated. The white tile behind the AMUSF crest is what exposed it: root pages
got it, /business/ and /projects/ did not.

This copies the canonical :root stylesheet out of a freshly-inlined root page and
replaces the stale copy in every subdirectory page. Scoped blocks that do not
start with :root — the .biz-* rules on Business Hub pages, the .sv-* rules on the
survey — are left exactly as they are, because those belong to the page.

Run AFTER build-inline.py, or it will copy a stale stylesheet.
"""

import os, re, sys, glob

REFERENCE = 'webbing.html'
DIRS = ['business', 'projects', 'state-of-the-trade']

STYLE = re.compile(r'<style[^>]*>(.*?)</style>', re.S)


def canonical_css(path):
    """The :root block from a root page — that's the inlined styles.css."""
    h = open(path, encoding='utf-8').read()
    for m in STYLE.finditer(h):
        if m.group(1).strip().startswith(':root'):
            return m.group(0)
    return None


def main():
    if not os.path.exists(REFERENCE):
        sys.exit('Cannot find %s to read the current stylesheet from.' % REFERENCE)

    canon = canonical_css(REFERENCE)
    if not canon:
        sys.exit('No :root <style> block in %s. Run build-inline.py first.' % REFERENCE)

    print('Reference stylesheet: %s (%.1f KB)' % (REFERENCE, len(canon) / 1024.0))

    updated, already, skipped = [], 0, []
    for d in DIRS:
        if not os.path.isdir(d):
            continue
        for path in sorted(glob.glob(os.path.join(d, '**', '*.html'), recursive=True)):
            src = open(path, encoding='utf-8').read()

            target = None
            for m in STYLE.finditer(src):
                if m.group(1).strip().startswith(':root'):
                    target = m
                    break
            if not target:
                skipped.append(path + ' (no :root block)')
                continue

            if target.group(0) == canon:
                already += 1
                continue

            new = src[:target.start()] + canon + src[target.end():]
            open(path, 'w', encoding='utf-8').write(new)
            updated.append(path)

    print('  refreshed     : %d' % len(updated))
    print('  already current: %d' % already)
    for p in updated:
        print('     + ' + p)
    if skipped:
        print('  skipped:')
        for s in skipped:
            print('     - ' + s)

    if not updated and not already:
        print('\nNo subdirectory pages found. Run build-business.py / build-survey.py first.')


if __name__ == '__main__':
    main()

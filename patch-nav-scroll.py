#!/usr/bin/env python3
"""
Fix: on mobile the open menu is taller than the screen, and because .site-nav is
position:sticky the overflow below the fold can't be reached -- sticky elements
don't scroll with the page once pinned.

Fix is to cap the open list to the visible viewport and let it scroll inside itself.
100dvh (dynamic viewport height) is used so the browser's address bar doesn't
steal the bottom rows; a 100vh line sits above it for older browsers.

Run from the site root:  python3 patch-nav-scroll.py
Safe to run twice -- it skips files already patched.
"""
import io, os, sys

OLD = '.nav-list.open{display:flex}'
NEW = ('.nav-list.open{display:flex;'
       'max-height:calc(100vh - 5rem);'
       'max-height:calc(100dvh - 5rem);'
       'overflow-y:auto;'
       'overscroll-behavior:contain;'
       '-webkit-overflow-scrolling:touch}')

MARK = 'overscroll-behavior:contain'

targets, patched, already, missing = [], 0, 0, 0

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', 'md')]
    for f in files:
        if f.endswith('.html') or f == 'styles.css':
            targets.append(os.path.join(root, f))

for path in sorted(targets):
    try:
        c = io.open(path, encoding='utf-8').read()
    except Exception as e:
        print('  skip (unreadable): %s -- %s' % (path, e))
        continue

    if OLD not in c:
        if '.nav-list.open' in c and MARK in c:
            already += 1
        elif '.nav-list.open' in c:
            missing += 1
            print('  ?    %s -- has .nav-list.open but not the expected rule' % path)
        continue

    io.open(path, 'w', encoding='utf-8').write(c.replace(OLD, NEW))
    patched += 1
    print('  ok   %s' % path)

print('\n%d patched, %d already done, %d need a look' % (patched, already, missing))
if missing:
    sys.exit(1)

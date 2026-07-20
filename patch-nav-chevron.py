#!/usr/bin/env python3
"""
Make the Tools expand control obvious.

The first pass used a small chevron at 60% opacity, which reads as decoration
rather than a control. This replaces it with a bordered box carrying a chevron
that rotates when the submenu opens -- the same affordance people already know
from every accordion they've ever used.

Run AFTER patch-nav-collapse.py, from the site root:
    python3 patch-nav-chevron.py

Safe to run twice.
"""
import io, os, sys

OLD = ('.has-sub.collapsible>a::after{content:"\\25B8";font-size:.78em;opacity:.6;'
       'padding-left:.6rem}'
       '.has-sub.collapsible.expanded>a::after{content:"\\25BE"}')

NEW = ('.has-sub.collapsible>a::after{content:"\\25BE";font-size:.8em;line-height:1;'
       'color:var(--green);background:var(--cream-deep);border:1px solid var(--rule);'
       'border-radius:5px;width:1.85rem;height:1.85rem;display:inline-flex;'
       'align-items:center;justify-content:center;flex:0 0 auto;margin-left:.7rem;'
       'transition:transform .18s ease}'
       '.has-sub.collapsible.expanded>a::after{transform:rotate(180deg)}')

SKIP_DIRS = {'.git', 'node_modules', 'md'}
done = notfound = already = 0

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in sorted(files):
        if not (f.endswith('.html') or f == 'styles.css'):
            continue
        p = os.path.join(root, f)
        try:
            c = io.open(p, encoding='utf-8').read()
        except Exception:
            continue

        if OLD in c:
            io.open(p, 'w', encoding='utf-8').write(c.replace(OLD, NEW))
            done += 1
            print('  ok   %s' % p)
        elif 'has-sub.collapsible.expanded>a::after{transform' in c:
            already += 1
        elif 'has-sub.collapsible' not in c and 'nav-list' in c:
            notfound += 1

print('\n%d files updated, %d already done' % (done, already))
if notfound:
    print('\n%d page(s) have a nav but no collapsible submenu.' % notfound)
    print('Run patch-nav-collapse.py first, then this one.')
    sys.exit(1)

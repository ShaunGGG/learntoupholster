#!/usr/bin/env python3
"""Inline styles.css into every page (kills the render-blocking CSS request).
styles.css stays the source of truth — rerun this after editing it."""
import glob, re
css = open('styles.css').read()
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
css = re.sub(r'\s+', ' ', css).replace('} ', '}').replace('{ ', '{').replace('; ', ';').strip()
style = '<style>' + css + '</style>'
n = 0
for f in glob.glob('*.html'):
    c = open(f).read()
    c2, k = re.subn(r'<link rel="stylesheet" href="/styles.css\?v=\d+">', style, c)
    if not k:
        c2, k = re.subn(r'<style>:root\{.*?</style>', style, c, count=1, flags=re.S)
    if k:
        open(f, 'w').write(c2); n += 1
print(f'inlined into {n} pages ({len(style)//1024}KB minified)')

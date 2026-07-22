#!/usr/bin/env python3
"""Fixes a latent bug in build-inline.py: the mobile-nav chevron CSS
content:"\25BE" contains a backslash that crashes re.subn's replacement
parser ("invalid group reference"). Switches to a literal lambda replacement.
Safe to run once; idempotent."""
s = open('build-inline.py').read()
if 'lambda _: style' in s:
    print("build-inline.py already fixed — nothing to do."); raise SystemExit
a = "c2, k = re.subn(r'<link rel=\"stylesheet\" href=\"/styles.css\\?v=\\d+\">', style, c)"
b = "c2, k = re.subn(r'<link rel=\"stylesheet\" href=\"/styles.css\\?v=\\d+\">', lambda _: style, c)"
c = "c2, k = re.subn(r'<style>:root\\{.*?</style>', style, c, count=1, flags=re.S)"
d = "c2, k = re.subn(r'<style>:root\\{.*?</style>', lambda _: style, c, count=1, flags=re.S)"
s = s.replace(a,b).replace(c,d)
open('build-inline.py','w').write(s)
print("build-inline.py patched (literal replacement).")

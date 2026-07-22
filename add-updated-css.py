#!/usr/bin/env python3
"""Adds the .updated style (for the 'Last updated' line) to styles.css if absent."""
css = open('styles.css').read()
if '.updated{' in css:
    print(".updated rule already present."); raise SystemExit
rule = '.updated{font-family:var(--display);font-size:.8rem;letter-spacing:.04em;color:var(--sage);margin:.6rem auto 0;text-transform:uppercase}\n'
open('styles.css','a').write(rule)
print("Added .updated rule to styles.css.")

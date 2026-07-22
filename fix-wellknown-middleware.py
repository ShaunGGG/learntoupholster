#!/usr/bin/env python3
"""Fixes the /.well-known/ 404: functions/_middleware.js blocks every path
starting with '/.' (to hide internal dotfiles), which also caught
/.well-known/api-catalog and the MCP server card. This narrows the guard so
.well-known is served while .py/.git/etc stay hidden. Idempotent."""
p = 'functions/_middleware.js'
src = open(p).read()
if '/.well-known/' in src:
    print("_middleware.js already allows .well-known — nothing to do."); raise SystemExit
old = "path.startsWith('/.')"
new = "(path.startsWith('/.') && !path.startsWith('/.well-known/'))"
if old not in src:
    print("WARNING: expected guard not found; no change made."); raise SystemExit
src = src.replace(old, new, 1)
open(p,'w').write(src)
print("Patched functions/_middleware.js — /.well-known/ now served.")

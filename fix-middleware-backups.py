#!/usr/bin/env python3
"""
fix-middleware-backups.py — learntoupholster.com

Closes the backup-file hole in functions/_middleware.js.

THE BUG: the block rule was

    /\\.(py|toml|sql|bak)$/i.test(path)

The `$` anchors immediately after `bak`, so it only caught an exact `.bak`
ending. Every suffixed variant walked straight through and was served:

    fire-safety-checker.html.bak    404  blocked
    fire-safety-checker.html.bak2   200  SERVED
    fire-safety-checker.html.bak3   200  SERVED
    index.html.bak-20260809-092202  200  SERVED   <- all 115 of them

THE FIX: keep the anchored list for fixed extensions, add `orig`/`tmp`/`swp`
while we're here, and match `.bak` anywhere in the path rather than only at
the end.

Named fix-* rather than patch-* deliberately: .gitignore excludes patch-*.py,
which is why the previous attempt at this never made it into the repo.

Idempotent. Safe to re-run.

Usage:
    python3 fix-middleware-backups.py
    python3 fix-middleware-backups.py --dry-run
"""

import re
import sys

TARGET = 'functions/_middleware.js'

OLD = r'/\.(py|toml|sql|bak)$/i.test(path)'
NEW = r'/\.(py|toml|sql|orig|tmp|swp)$/i.test(path) || /\.bak/i.test(path)'

DRY = '--dry-run' in sys.argv


def main():
    print('fix-middleware-backups' + ('  [DRY RUN - nothing written]' if DRY else ''))

    try:
        src = open(TARGET, encoding='utf-8').read()
    except FileNotFoundError:
        print('  ! %s not found - are you in the repo root?' % TARGET)
        sys.exit(1)

    if NEW in src:
        print('  = already patched, nothing to do')
        return

    if OLD not in src:
        print('  ! the expected rule was not found in %s' % TARGET)
        print('    Looking for: %s' % OLD)
        print('    Aborting rather than guessing. Paste me the file and I will adjust.')
        sys.exit(1)

    out = src.replace(OLD, NEW, 1)

    if not DRY:
        open(TARGET, 'w', encoding='utf-8').write(out)

    line = next(i for i, l in enumerate(out.split('\n'), 1) if NEW in l)
    print('  + patched line %d of %s' % (line, TARGET))
    print('    now blocks: *.py *.toml *.sql *.orig *.tmp *.swp, and ANY *.bak*')
    print('  done.')


if __name__ == '__main__':
    main()

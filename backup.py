#!/usr/bin/env python3
"""
backup.py — learntoupholster.com

Backups belong OUTSIDE the deploy root. Anything sitting next to index.html
gets uploaded by `wrangler pages deploy .` and served publicly, which is how
119 copies of the site ended up live on 9 August.

This writes to ~/ltu-backups/<YYYYMMDD-HHMMSS>/ instead, mirroring the repo's
directory structure. Cloudflare never sees them, git never tracks them, and a
restore is one command instead of renaming files by hand.

USE IN BUILD SCRIPTS
    from backup import backup
    backup('index.html')        # call before overwriting

    All calls within one script run land in the same timestamped folder.

CLI
    python3 backup.py --import          sweep stray *.bak-* out of the repo
    python3 backup.py --list            show stored runs
    python3 backup.py --restore RUN     put a run back (--dry-run to preview)
    python3 backup.py --prune           keep the newest KEEP_RUNS, delete older
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
_NAMED = {'learntoupholster': 'ltu-backups'}
BACKUP_ROOT = Path.home() / _NAMED.get(REPO.name, REPO.name + '-backups')
KEEP_RUNS = 10

# Matches the legacy sibling-file naming: index.html.bak-20260809-092202
LEGACY = re.compile(r'^(?P<orig>.+)\.bak-(?P<stamp>\d{8}-\d{6})$')

# One folder per script run, created lazily on first backup() call.
_run_dir = None


# ---------------------------------------------------------------- library API

def run_dir():
    """The folder for this process's backups. Created on first use."""
    global _run_dir
    if _run_dir is None:
        _run_dir = BACKUP_ROOT / datetime.now().strftime('%Y%m%d-%H%M%S')
        _run_dir.mkdir(parents=True, exist_ok=True)
    return _run_dir


def backup(path):
    """Copy `path` into this run's backup folder, preserving its relative path.

    Returns the backup location, or None if the file doesn't exist yet (which
    is normal for a first build — there's nothing to preserve)."""
    src = Path(path)
    if not src.exists():
        return None

    try:
        rel = src.resolve().relative_to(REPO)
    except ValueError:
        rel = Path(src.name)          # outside the repo — flatten it

    dest = run_dir() / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


# ---------------------------------------------------------------- commands

def cmd_import(dry):
    """Sweep legacy *.bak-<stamp> files out of the repo, grouped by stamp."""
    found = [p for p in REPO.rglob('*.bak-*')
             if '.git' not in p.parts and LEGACY.match(p.name)]

    if not found:
        print('No stray .bak- files in the repo. Nothing to import.')
        return

    groups = {}
    for p in found:
        m = LEGACY.match(p.name)
        groups.setdefault(m.group('stamp'), []).append((p, m.group('orig')))

    total = 0
    for stamp, items in sorted(groups.items()):
        dest_root = BACKUP_ROOT / stamp
        print(f'\n  {stamp}  ({len(items)} files) -> {dest_root}')
        for src, orig_name in items:
            rel = src.relative_to(REPO).parent / orig_name
            dest = dest_root / rel
            if not dry:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))
            total += 1

    verb = 'would move' if dry else 'moved'
    print(f'\n  {verb} {total} files into {len(groups)} run(s) under {BACKUP_ROOT}')
    if not dry:
        print('  repo is clean — redeploy to drop them from the live site')


def cmd_list():
    if not BACKUP_ROOT.exists():
        print(f'No backups yet ({BACKUP_ROOT} does not exist).')
        return

    runs = sorted([d for d in BACKUP_ROOT.iterdir() if d.is_dir()])
    if not runs:
        print('No backup runs stored.')
        return

    print(f'{len(runs)} run(s) in {BACKUP_ROOT}:\n')
    for d in runs:
        files = [f for f in d.rglob('*') if f.is_file()]
        size = sum(f.stat().st_size for f in files)
        when = datetime.strptime(d.name, '%Y%m%d-%H%M%S').strftime('%d %b %Y, %H:%M')
        print(f'  {d.name}   {len(files):>4} files   {size/1024/1024:>6.1f} MB   {when}')


def cmd_restore(run, dry):
    src_root = BACKUP_ROOT / run
    if not src_root.is_dir():
        print(f'No such run: {run}\nUse --list to see what is available.')
        sys.exit(1)

    files = [f for f in src_root.rglob('*') if f.is_file()]
    print(f'{"Would restore" if dry else "Restoring"} {len(files)} files from {run}:\n')

    for f in files:
        rel = f.relative_to(src_root)
        dest = REPO / rel
        state = 'overwrite' if dest.exists() else 'create'
        print(f'  {state:>9}  {rel}')
        if not dry:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)

    if dry:
        print('\n  Dry run — nothing written. Drop --dry-run to apply.')
    else:
        print(f'\n  Restored. Rebuild and redeploy to push these live.')


def cmd_prune(dry):
    if not BACKUP_ROOT.exists():
        print('Nothing to prune.')
        return

    runs = sorted([d for d in BACKUP_ROOT.iterdir() if d.is_dir()])
    old = runs[:-KEEP_RUNS] if len(runs) > KEEP_RUNS else []

    if not old:
        print(f'{len(runs)} run(s) stored, keeping {KEEP_RUNS}. Nothing to prune.')
        return

    for d in old:
        print(f'  {"would delete" if dry else "deleted"}  {d.name}')
        if not dry:
            shutil.rmtree(d)
    print(f'\n  {len(runs) - len(old)} run(s) kept.')


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description='Backup management for learntoupholster')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--import', dest='do_import', action='store_true',
                   help='sweep stray *.bak-* files out of the repo')
    g.add_argument('--list', action='store_true', help='show stored runs')
    g.add_argument('--restore', metavar='RUN', help='restore a run into the repo')
    g.add_argument('--prune', action='store_true',
                   help=f'delete all but the newest {KEEP_RUNS} runs')
    ap.add_argument('--dry-run', action='store_true', help='preview only')
    a = ap.parse_args()

    if a.do_import:
        cmd_import(a.dry_run)
    elif a.list:
        cmd_list()
    elif a.restore:
        cmd_restore(a.restore, a.dry_run)
    elif a.prune:
        cmd_prune(a.dry_run)


if __name__ == '__main__':
    main()

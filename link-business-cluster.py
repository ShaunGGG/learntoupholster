#!/usr/bin/env python3
"""
link-business-cluster.py — give every Business Hub article sibling links.

The problem, measured from business-sources/*.txt:

  * 9 of 19 articles link to no sibling at all, only outward to reference
    pages. Those are the July 31 batch, written before the convention settled.
  * 9 of 19 receive no inbound link from any sibling.

Google reports most of /business/ as "Discovered - currently not indexed",
meaning it knows the URLs but has never fetched them. A flat hub-and-spoke
gives Googlebot one route in and no reason to think the spokes matter. This
turns the spokes into a mesh.

What it does: tops up each article's `related:` list to MIN_SIBLINGS sibling
links, preferring articles in the same section, then in an affinity-related
section, and among those the ones with fewest inbound links so far. Existing
entries are never removed or reordered -- your editorial choices stand, this
only appends.

Deterministic: same inputs give the same output, so re-running changes
nothing. Backs up to ~/ltu-backups/<stamp>/business-sources/.

  python3 link-business-cluster.py            # dry run
  python3 link-business-cluster.py --apply

Then rebuild and check the diff:
  python3 build-business.py && git diff --stat business/
"""

import os
import re
import sys
import glob
import shutil
import datetime

SRC_DIR = 'business-sources'
MIN_SIBLINGS = 3
MIN_INBOUND = 2
MAX_RELATED = 5
APPLY = '--apply' in sys.argv

# Sections whose readers plausibly want each other. Symmetric.
AFFINITY = [
    {'Pricing & Profit', 'Quoting Jobs', 'Dealing With Customers'},
    {'Starting Out', 'Getting Customers', 'Pricing & Profit'},
    {'Working With the Trade', 'Money & Finance', 'Growing the Business'},
    {'Problems Nobody Talks About', 'Running the Workshop', 'Dealing With Customers'},
    {'Starting Out', 'Problems Nobody Talks About'},
]


def parse_front(path):
    """Return (dict of front matter, list of raw lines)."""
    lines = open(path, encoding='utf-8').read().split('\n')
    meta, end = {}, 0
    for i, ln in enumerate(lines):
        if ln.strip() == '':
            end = i
            break
        m = re.match(r'^([a-z_]+):\s*(.*)$', ln)
        if m:
            meta[m.group(1)] = m.group(2).strip()
    return meta, lines, end


def main():
    if not os.path.isdir(SRC_DIR):
        sys.exit(f'ABORT: {SRC_DIR}/ not found -- run from ~/learntoupholster')

    arts = {}
    for path in sorted(glob.glob(os.path.join(SRC_DIR, '*.txt'))):
        slug = os.path.splitext(os.path.basename(path))[0]
        meta, lines, end = parse_front(path)
        if 'title' not in meta:
            print(f'  skipping {path} (no title in front matter)')
            continue
        rel = [r.strip() for r in meta.get('related', '').split(',') if r.strip()]
        arts[slug] = {'path': path, 'meta': meta, 'lines': lines,
                      'section': meta.get('section', ''), 'related': rel,
                      'title': meta['title']}

    if not arts:
        sys.exit(f'ABORT: no parseable sources in {SRC_DIR}/')

    own = {f'/business/{s}' for s in arts}

    # Current inbound count, siblings only.
    inbound = {s: 0 for s in arts}
    for a in arts.values():
        for r in a['related']:
            if r in own:
                inbound[r.rsplit('/', 1)[1]] += 1

    def affinity_rank(sec_a, sec_b):
        if sec_a == sec_b:
            return 0
        for grp in AFFINITY:
            if sec_a in grp and sec_b in grp:
                return 1
        return 2

    added = {}
    for slug in sorted(arts):
        a = arts[slug]
        sibs = [r for r in a['related'] if r in own]
        need = MIN_SIBLINGS - len(sibs)
        room = MAX_RELATED - len(a['related'])
        need = min(need, room)
        if need <= 0:
            continue

        current = set(a['related'])
        cands = [s for s in arts
                 if s != slug and f'/business/{s}' not in current]
        # Nearest section first, then least-linked, then alphabetical.
        cands.sort(key=lambda s: (affinity_rank(a['section'], arts[s]['section']),
                                  inbound[s], s))
        picks = cands[:need]
        if not picks:
            continue

        added[slug] = picks
        for p in picks:
            inbound[p] += 1
            a['related'].append(f'/business/{p}')

    # --- pass 2: guarantee inbound -------------------------------------
    # Outbound alone does not get a page discovered. Any article nothing
    # links to stays invisible however many links it emits, so give every
    # one at least MIN_INBOUND donors.
    for slug in sorted(arts, key=lambda s: (inbound[s], s)):
        while inbound[slug] < MIN_INBOUND:
            target = f'/business/{slug}'
            donors = [d for d in arts
                      if d != slug
                      and target not in arts[d]['related']
                      and len(arts[d]['related']) < MAX_RELATED]
            if not donors:
                print(f'  !! no donor with room for {slug} '
                      f'(all at MAX_RELATED={MAX_RELATED})')
                break
            donors.sort(key=lambda d: (affinity_rank(arts[slug]['section'],
                                                     arts[d]['section']),
                                       len(arts[d]['related']), d))
            d = donors[0]
            arts[d]['related'].append(target)
            inbound[slug] += 1
            added.setdefault(d, []).append(slug)

    print('=' * 66)
    print('link-business-cluster.py — ' + ('APPLYING' if APPLY else 'DRY RUN'))
    print('=' * 66)
    print(f'{len(arts)} articles, {sum(1 for s in arts if inbound[s] == 0)} '
          f'still with no inbound sibling link\n')

    if not added:
        print('Every article already has enough sibling links. Nothing to do.')
        return 0

    for slug in sorted(added):
        print(f'{slug}  [{arts[slug]["section"]}]')
        for p in added[slug]:
            print(f'    + /business/{p}   ({arts[p]["section"]})')

    if not APPLY:
        print('\nDRY RUN — nothing written. Re-run with --apply.')
        return 0

    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    bdir = os.path.join(os.path.expanduser('~'), 'ltu-backups', stamp, SRC_DIR)
    os.makedirs(bdir, exist_ok=True)

    for slug in sorted(added):
        a = arts[slug]
        shutil.copy2(a['path'], os.path.join(bdir, os.path.basename(a['path'])))
        newline = 'related: ' + ', '.join(a['related'])
        lines, wrote = a['lines'], False
        for i, ln in enumerate(lines):
            if ln.strip() == '':
                break
            if ln.startswith('related:'):
                lines[i], wrote = newline, True
                break
        if not wrote:
            # No related: line -- insert after section: to keep front matter tidy.
            for i, ln in enumerate(lines):
                if ln.startswith('section:'):
                    lines.insert(i + 1, newline)
                    wrote = True
                    break
        if not wrote:
            print(f'  !! {slug}: could not place related: line, left untouched')
            continue
        open(a['path'], 'w', encoding='utf-8').write('\n'.join(lines))

    print(f'\n{len(added)} sources updated. Backup: ~/ltu-backups/{stamp}/{SRC_DIR}/')
    print('Now: python3 build-business.py')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""
check-suppliers.py — re-verify the directory. Run every six months.

    python3 check-suppliers.py

Reads supplier-data.py, fetches every listed site, and reports what has changed.
It does not edit anything: a directory is an editorial product and removing a
supplier should be a decision, not a side effect of a timeout.

Important: a 403, or a bot-check page, means the site is UP and defending itself.
Several perfectly healthy suppliers behave that way. Those are reported as
"blocked", never as gone.

After running, update VERIFIED in supplier-data.py to today, deal with anything
flagged, and re-run build-suppliers.py.
"""

import re, ssl, sys, os, datetime, importlib.util
import urllib.request, urllib.error
import concurrent.futures as cf

UA = {'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                     '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

PARKED = re.compile(r'domain (is )?for sale|this domain|parked|godaddy|sedo|'
                    r'under construction|coming soon|site is currently unavailable', re.I)
SIGNAL = re.compile(r'upholster|foam|webbing|fabric|supplies|vinyl|trimming', re.I)
BOTWALL = re.compile(r'bot verification|checking your browser|cf-browser-verification|'
                     r'enable javascript and cookies|attention required', re.I)


def load():
    spec = importlib.util.spec_from_file_location('sd', 'supplier-data.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check(s):
    try:
        r = urllib.request.urlopen(urllib.request.Request(s['url'], headers=UA),
                                   timeout=35, context=CTX)
        body = r.read(250000).decode('utf-8', 'ignore')
        if BOTWALL.search(body) or len(body) < 1200:
            return s, 'blocked', 'site up, refuses automated checks'
        if PARKED.search(body):
            return s, 'GONE', 'looks like a parked or for-sale domain'
        if not SIGNAL.search(body):
            return s, 'CHECK', 'page loads but reads nothing like a supplier'
        return s, 'live', ''
    except urllib.error.HTTPError as e:
        if e.code in (403, 405, 406, 429):
            return s, 'blocked', 'HTTP %d \u2014 site up, blocking automation' % e.code
        if e.code in (404, 410):
            return s, 'CHECK', 'HTTP %d \u2014 homepage missing' % e.code
        return s, 'CHECK', 'HTTP %d' % e.code
    except Exception as e:
        return s, 'CHECK', 'unreachable: %s' % str(e)[:60]


def main():
    if not os.path.exists('supplier-data.py'):
        sys.exit('Run this from ~/learntoupholster.')
    data = load()
    print('Re-checking %d suppliers (last verified %s)\n' % (len(data.SUPPLIERS), data.VERIFIED))

    results = []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for s, state, why in ex.map(check, data.SUPPLIERS):
            results.append((s, state, why))

    order = {'GONE': 0, 'CHECK': 1, 'blocked': 2, 'live': 3}
    results.sort(key=lambda r: (order[r[1]], r[0]['country'], r[0]['name']))

    counts = {}
    for s, state, why in results:
        counts[state] = counts.get(state, 0) + 1

    needs_action = [r for r in results if r[1] in ('GONE', 'CHECK')]
    changed = [r for r in results if r[1] != r[0]['status'] and r[1] in ('live', 'blocked')]

    if needs_action:
        print('NEEDS A LOOK \u2014 %d\n' % len(needs_action))
        for s, state, why in needs_action:
            print('  %-6s %s %-34s %s' % (state, s['country'], s['name'], s['url']))
            print('         %s' % why)
        print()

    if changed:
        print('STATUS CHANGED (update the status field) \u2014 %d' % len(changed))
        for s, state, why in changed:
            print('  %s %-34s %s -> %s' % (s['country'], s['name'], s['status'], state))
        print()

    print('Summary: ' + ', '.join('%s %d' % (k, v) for k, v in sorted(counts.items())))
    if not needs_action and not changed:
        print('\nNothing to do. Update VERIFIED to %s in supplier-data.py and rebuild.'
              % datetime.date.today().isoformat())
    else:
        print('\nNothing has been changed automatically. Deal with the above by hand,')
        print('then set VERIFIED = \'%s\' in supplier-data.py and re-run build-suppliers.py.'
              % datetime.date.today().isoformat())


if __name__ == '__main__':
    main()

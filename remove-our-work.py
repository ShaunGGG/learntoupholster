#!/usr/bin/env python3
"""
remove-our-work.py — retire /our-work now the gallery lives on /projects/.

Deleting the file on its own would turn every inbound link, bookmark and search
result for /our-work into a 404, and throw away whatever authority the URL has
built. So this does three things:

  1. Adds a permanent redirect to functions/_middleware.js, sending /our-work to
     /projects/#gallery \u2014 straight to the photographs, not the top of the page.

     The redirect goes in the middleware rather than a _redirects file because
     the middleware demonstrably runs on this site, and I could not verify from
     outside whether _redirects fires underneath a root middleware. Guessing
     about a redirect is how you find out weeks later that it never worked.

  2. Deletes our-work.html and its markdown variant, so the forty-three
     photographs are not sitting on two URLs as near-duplicate content.

  3. Leaves a backup of both.

Run after merge-gallery.py has put the gallery on /projects/. Idempotent.
"""

import os, re, sys, shutil, datetime

PAGE = 'our-work.html'
MD = os.path.join('md', 'our-work.md')
MW = os.path.join('functions', '_middleware.js')
MARK = 'ltu-our-work-retired'

REDIRECT = """
  // %s
  // The gallery moved onto the projects page. Permanent redirect so inbound
  // links, bookmarks and search results keep working.
  if (path === '/our-work' || path === '/our-work/') {
    return Response.redirect(new URL('/projects/#gallery', request.url).toString(), 301);
  }
""" % MARK


def main():
    if not os.path.exists('index.html'):
        sys.exit('Run this from ~/learntoupholster.')
    if not os.path.exists(MW):
        sys.exit('Cannot find %s. Nothing written.' % MW)

    gallery_moved = False
    proj = os.path.join('projects', 'index.html')
    if os.path.exists(proj):
        gallery_moved = 'ltu-gallery-merged' in open(proj, encoding='utf-8').read()
    if not gallery_moved:
        sys.exit('The gallery is not on /projects/ yet. Run merge-gallery.py first,\n'
                 'or the photographs will simply disappear.')

    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    bdir = os.path.join(os.path.expanduser('~'), 'ltu-backups', stamp)
    os.makedirs(bdir, exist_ok=True)

    # ---- 1. the redirect
    mw = open(MW, encoding='utf-8').read()
    if MARK in mw:
        print('Redirect already in place.')
    else:
        m = re.search(r'(const path = url\.pathname;\s*\n)', mw)
        if not m:
            sys.exit('Could not find where to insert the redirect in %s. Nothing written.' % MW)
        shutil.copy2(MW, os.path.join(bdir, '_middleware.js'))
        mw = mw[:m.end()] + REDIRECT + mw[m.end():]
        open(MW, 'w', encoding='utf-8').write(mw)
        print('Redirect added to %s' % MW)
        print('   /our-work -> /projects/#gallery  (301)')

    # ---- 2. the files
    removed = []
    for f in (PAGE, MD):
        if os.path.exists(f):
            shutil.copy2(f, os.path.join(bdir, f.replace(os.sep, '__')))
            os.remove(f)
            removed.append(f)
    if removed:
        print('\nDeleted:')
        for f in removed:
            print('   ' + f)
    else:
        print('\nNothing to delete \u2014 already removed.')

    print('\nBackup: ~/ltu-backups/%s/' % stamp)
    print('\nNow rebuild so the sitemap and llms files drop it:')
    print('  python3 build-md-extra.py && python3 build-llms.py && python3 update-sitemap.py')
    print('\nThen check after deploying:')
    print('  curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\\n" '
          'https://www.learntoupholster.com/our-work')
    print('  expect: 301 -> https://www.learntoupholster.com/projects/#gallery')


if __name__ == '__main__':
    main()

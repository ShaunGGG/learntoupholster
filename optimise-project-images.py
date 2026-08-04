#!/usr/bin/env python3
"""
optimise-project-images.py — dimensions and webp for the project pages.

Two problems this fixes, both across every project page:

  1. No width/height on the photos. The browser cannot reserve space, so the
     text jumps as each image loads. Google measures that as layout shift and
     it is one of the cheapest Core Web Vitals wins available.

  2. Plain full-size JPEGs. One project page was carrying 1.6 MB of them. The
     AMUSF crest is already served as a <picture> with a webp source, so the
     pattern exists in the build \u2014 it was just never applied to the photos.

Run after build-projects.py, before build-inline.py. Idempotent: images already
wrapped are skipped, and a webp is only rebuilt if the jpeg is newer.

Needs Pillow:  sudo apt install python3-pil python3-pil.imagetk
"""

import os, re, sys, glob, shutil, datetime

try:
    from PIL import Image
except ImportError:
    sys.exit('Pillow not installed. Run:  sudo apt install python3-pil')

DIRS = ['projects']
QUALITY = 82          # visually indistinguishable from the jpeg at this level
MAX_WIDTH = 1600      # nothing on the site is displayed wider than this
SKIP = ('crest', 'logo', 'icon', 'og-')

IMG = re.compile(r'<img\b[^>]*>', re.I)


def attr(tag, name):
    m = re.search(r'\b%s="([^"]*)"' % name, tag, re.I)
    return m.group(1) if m else None


def make_webp(src_path):
    """Return (webp_path, saved_bytes) or (None, 0)."""
    webp = os.path.splitext(src_path)[0] + '.webp'
    try:
        if os.path.exists(webp) and os.path.getmtime(webp) >= os.path.getmtime(src_path):
            return webp, 0
        im = Image.open(src_path)
        if im.mode not in ('RGB', 'RGBA'):
            im = im.convert('RGB')
        if im.width > MAX_WIDTH:
            im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
        im.save(webp, 'WEBP', quality=QUALITY, method=6)
        saved = os.path.getsize(src_path) - os.path.getsize(webp)
        # A webp bigger than the jpeg helps nobody.
        if saved <= 0:
            os.remove(webp)
            return None, 0
        return webp, saved
    except Exception as e:
        print('   ! %s: %s' % (src_path, e))
        return None, 0


def main():
    if not os.path.exists('index.html'):
        sys.exit('Run this from ~/learntoupholster.')

    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    bdir = os.path.join(os.path.expanduser('~'), 'ltu-backups', stamp)

    files = []
    for d in DIRS:
        if os.path.isdir(d):
            files += sorted(glob.glob(os.path.join(d, '**', '*.html'), recursive=True))
    if not files:
        sys.exit('No project pages found. Run build-projects.py first.')

    tot_dims = tot_webp = 0
    tot_saved = 0
    changed = []

    for path in files:
        src = open(path, encoding='utf-8').read()
        out = src
        dims = webps = 0

        for tag in IMG.findall(src):
            s = attr(tag, 'src') or ''
            if not s.startswith('/') or any(k in s.lower() for k in SKIP):
                continue
            if not re.search(r'\.(jpe?g|png)$', s, re.I):
                continue
            # Already inside a <picture>? leave it alone.
            i = out.find(tag)
            if i > 0 and '<picture' in out[max(0, i - 220):i]:
                continue

            disk = s.lstrip('/')
            if not os.path.exists(disk):
                continue

            new_tag = tag

            # --- width and height, read from the file itself
            if not attr(tag, 'width'):
                try:
                    with Image.open(disk) as im:
                        w, hgt = im.size
                    new_tag = new_tag[:-1].rstrip() + ' width="%d" height="%d">' % (w, hgt)
                    dims += 1
                except Exception:
                    pass

            if 'loading=' not in new_tag:
                new_tag = new_tag[:-1].rstrip() + ' loading="lazy" decoding="async">'

            # --- webp alternative
            webp, saved = make_webp(disk)
            if webp:
                wsrc = '/' + webp.replace(os.sep, '/')
                new_tag = ('<picture><source srcset="%s" type="image/webp">%s</picture>'
                           % (wsrc, new_tag))
                webps += 1
                tot_saved += saved

            if new_tag != tag:
                out = out.replace(tag, new_tag, 1)

        if out != src:
            os.makedirs(bdir, exist_ok=True)
            shutil.copy2(path, os.path.join(bdir, path.replace(os.sep, '__')))
            open(path, 'w', encoding='utf-8').write(out)
            changed.append((path, dims, webps))
            tot_dims += dims
            tot_webp += webps

    print('%d project pages scanned' % len(files))
    for p, d, w in changed:
        print('   %-46s +%d dims  +%d webp' % (p, d, w))
    print('\n  width/height added : %d images' % tot_dims)
    print('  webp sources added : %d images' % tot_webp)
    print('  bytes saved        : %.1f MB (when a browser takes the webp)' % (tot_saved / 1024 / 1024))
    if changed:
        print('\nBackups: ~/ltu-backups/%s/' % stamp)
    else:
        print('\nNothing to do \u2014 already optimised.')


if __name__ == '__main__':
    main()

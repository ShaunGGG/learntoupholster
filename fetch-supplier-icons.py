#!/usr/bin/env python3
"""
fetch-supplier-icons.py — one icon per directory listing.

Fetches each supplier's own site icon, normalises it to 64x64 PNG and saves it
under assets/supplier-icons/. Run after editing supplier-data.py, before
build-suppliers.py.

Design decisions worth knowing:

  Self-hosted, not hot-linked. It would be one line to point at Google's
  favicon service instead, but that sends every visitor's browsing to a third
  party and breaks the day they change it. Fetched once at build time, served
  from your own domain, cached forever.

  Site icons rather than logos. A favicon is what a site publishes as its own
  identifying mark, it is a consistent square, and using it to identify the
  company you are linking to is ordinary directory practice. Scraping full
  brand logos would look better and is a murkier thing to do with fifty-nine
  companies' trademarks.

  Everything gets an icon. Where a site has none, or blocks the fetch, a
  lettermark is generated in the site palette. A directory where half the rows
  have an image and half have a gap looks broken.

Needs Pillow:  sudo apt install python3-pil
"""

import os, re, ssl, sys, io, importlib.util
import urllib.request, urllib.error
import concurrent.futures as cf

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit('Pillow not installed. Run:  sudo apt install python3-pil')

OUT_DIR = os.path.join('assets', 'supplier-icons')
SIZE = 64
UA = {'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                     '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

CREAM = (251, 246, 237)
GREEN = (34, 56, 44)

FONT_CANDIDATES = [
    '/mnt/skills/examples/canvas-design/canvas-fonts/YoungSerif-Regular.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
]


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def get(url, limit=400000):
    r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25, context=CTX)
    return r.read(limit)


def icon_candidates(site_url):
    """Icon URLs a site declares, best first, plus the conventional fallback."""
    from urllib.parse import urljoin
    out = []
    try:
        html = get(site_url, 250000).decode('utf-8', 'ignore')
        found = []
        for m in re.finditer(r'<link[^>]+rel="([^"]*icon[^"]*)"[^>]*>', html, re.I):
            tag = m.group(0)
            href = re.search(r'href="([^"]+)"', tag, re.I)
            if not href:
                continue
            sizes = re.search(r'sizes="(\d+)', tag, re.I)
            px = int(sizes.group(1)) if sizes else (180 if 'apple' in tag.lower() else 32)
            found.append((px, urljoin(site_url, href.group(1))))
        # Prefer something near our target size but not enormous.
        # Raster first: an SVG favicon is common now and unusable here.
        found.sort(key=lambda t: (t[1].lower().endswith('.svg'),
                                  abs(t[0] - 128), -t[0]))
        out = [u for _px, u in found]
    except Exception:
        pass
    for p in ('/apple-touch-icon.png', '/apple-touch-icon-precomposed.png',
              '/favicon.ico', '/favicon.png', '/favicon-32x32.png',
              '/favicon-96x96.png', '/icon.png', '/logo.png'):
        u = urljoin(site_url, p)
        if u not in out:
            out.append(u)
    return out


def normalise(raw):
    head = raw[:64].lstrip()[:32].lower()
    # A great many sites answer /favicon.ico with their HTML 404 page and a 200
    # status. Opening that as an image throws a confusing error, so reject it.
    if head.startswith(b'<!doctype') or head.startswith(b'<html'):
        raise ValueError('served HTML, not an image')
    if head.startswith(b'<svg') or b'<svg' in raw[:400].lower():
        raise ValueError('SVG \u2014 Pillow cannot rasterise it')

    im = Image.open(io.BytesIO(raw))
    if getattr(im, 'is_animated', False):
        im.seek(0)
    # .ico files carry several sizes. Pillow picks one; ask it for the biggest.
    if im.format == 'ICO':
        try:
            sizes = im.info.get('sizes')
            if sizes:
                im = Image.open(io.BytesIO(raw))
                im.size = max(sizes)
                im.load()
        except Exception:
            im = Image.open(io.BytesIO(raw))
    im = im.convert('RGBA')
    if im.width < 16 or im.height < 16:
        raise ValueError('too small to be useful')
    canvas = Image.new('RGBA', (SIZE, SIZE), (255, 255, 255, 0))
    im.thumbnail((SIZE, SIZE), Image.LANCZOS)
    canvas.paste(im, ((SIZE - im.width) // 2, (SIZE - im.height) // 2), im)
    return canvas


def lettermark(name):
    """Fallback: initials on the site's cream, so every row has something."""
    words = [w for w in re.split(r'[^A-Za-z0-9]+', name) if w]
    initials = (words[0][0] + (words[1][0] if len(words) > 1 else '')).upper()
    im = Image.new('RGBA', (SIZE, SIZE), CREAM + (255,))
    d = ImageDraw.Draw(im)
    font = None
    for f in FONT_CANDIDATES:
        if os.path.exists(f):
            font = ImageFont.truetype(f, 30 if len(initials) > 1 else 36)
            break
    if font is None:
        font = ImageFont.load_default()
    box = d.textbbox((0, 0), initials, font=font)
    d.text(((SIZE - (box[2] - box[0])) / 2 - box[0],
            (SIZE - (box[3] - box[1])) / 2 - box[1]),
           initials, font=font, fill=GREEN + (255,))
    return im


def work(entry):
    name, url = entry['name'], entry['url']
    path = os.path.join(OUT_DIR, slug(name) + '.png')
    if os.path.exists(path):
        return name, 'kept', path
    for cand in icon_candidates(url):
        try:
            raw = get(cand, 400000)
            if len(raw) < 40:
                continue
            normalise(raw).save(path, 'PNG', optimize=True)
            return name, 'fetched', path
        except Exception:
            continue
    lettermark(name).save(path, 'PNG', optimize=True)
    return name, 'lettermark', path


def main():
    if not os.path.exists('supplier-data.py'):
        sys.exit('Run this from ~/learntoupholster.')
    spec = importlib.util.spec_from_file_location('sd', 'supplier-data.py')
    data = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(data)

    os.makedirs(OUT_DIR, exist_ok=True)
    counts = {'fetched': 0, 'lettermark': 0, 'kept': 0}
    fallbacks = []

    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for name, state, _p in ex.map(work, data.SUPPLIERS):
            counts[state] += 1
            if state == 'lettermark':
                fallbacks.append(name)

    total = sum(counts.values())
    size = sum(os.path.getsize(os.path.join(OUT_DIR, f))
               for f in os.listdir(OUT_DIR) if f.endswith('.png'))
    print('%d icons in %s (%.0f KB total)' % (total, OUT_DIR, size / 1024))
    print('  fetched from the site : %d' % counts['fetched'])
    print('  lettermark fallback   : %d' % counts['lettermark'])
    print('  already present       : %d' % counts['kept'])
    if fallbacks:
        print('\nNo usable icon found, lettermark used:')
        for f in fallbacks:
            print('   - ' + f)
        print('\nDelete the file from %s to retry one.' % OUT_DIR)


if __name__ == '__main__':
    main()

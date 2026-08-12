#!/usr/bin/env python3
"""
build-home-feeds.py — learntoupholster.com

Surfaces the blog and business articles on the homepage.

WHY: Ahrefs shows /business/ at 7.5 views per visitor and /blog/ at 8.1 —
the deepest engagement anywhere on the site, well above the 5.5 average.
But only 33 and 12 visitors respectively reached them in 30 days, because
both sit at crawl depth 3 behind a hub. Best-retaining content, least
discovered. This puts a sample of each one click from the homepage, which
helps readers and gives Googlebot a shorter path to the 60 URLs currently
stuck in "Discovered - currently not indexed".

Reads the same source files build-blog.py and build-business.py use, so the
lists regenerate on every build and never go stale. Nothing is hardcoded.

Reuses the existing .parts / .part / .pn CSS. The only new rule is scoped
inline in the injected block, so styles.css is untouched and there's no
cache version to bump.

Idempotent: injects between markers, replaces on every subsequent run.

Usage:
    python3 build-home-feeds.py             # apply
    python3 build-home-feeds.py --dry-run   # preview, write nothing
"""

import glob
import html
import os
import re
import sys

PAGE = 'index.html'
N_BLOG = 6
N_BIZ = 6

START = '<!-- home-feeds:start -->'
END = '<!-- home-feeds:end -->'

# Insert before the "Free tool" fabric-calculator block on first run.
ANCHOR = '<section class="wrap">\n  <div class="block block--green" style="text-align:center">'

# Mirrors build-business.py so the spread across sections stays sensible.
SECTION_ORDER = [
    'Starting Out', 'Pricing & Profit', 'Quoting Jobs', 'Getting Customers',
    'Dealing With Customers', 'Running the Workshop', 'Money & Finance',
    'Working With the Trade', 'Growing the Business', 'Problems Nobody Talks About',
    'Templates & Documents',
]

DRY = '--dry-run' in sys.argv


def parse_front_matter(path):
    """Same shape as build-business.py's parse_source: key: value, with
    indented continuation lines folded into the previous key."""
    raw = open(path, encoding='utf-8').read().replace('\r\n', '\n')
    head = raw.split('---BODY---', 1)[0].split('\n\n', 1)[0]
    meta, key = {}, None
    for line in head.split('\n'):
        m = re.match(r'^([a-z][a-z-]*):\s*(.*)$', line)
        if m:
            key = m.group(1)
            meta[key] = m.group(2).strip()
        elif key and line.startswith((' ', '\t')):
            meta[key] += ' ' + line.strip()
    meta['slug'] = os.path.basename(path)[:-4]
    return meta


def trim(text, limit=118):
    """Shorten to a word boundary so cards stay even."""
    text = re.sub(r'\s+', ' ', (text or '').strip())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(' ', 1)[0].rstrip(' ,.;:—-')
    return cut + '\u2026'


def card(url, label, title, blurb):
    return (
        '    <a class="part part--link" href="%s">\n'
        '      <span class="pn">%s</span>\n'
        '      <h3>%s</h3>\n'
        '      <p>%s</p>\n'
        '    </a>\n'
        % (url, html.escape(label), html.escape(title), html.escape(blurb))
    )


def blog_cards():
    posts = [parse_front_matter(p) for p in glob.glob('blog-sources/*.txt')]
    posts = [p for p in posts if p.get('title')]
    # Newest first. Missing dates sort last rather than crashing the build.
    posts.sort(key=lambda p: p.get('date', ''), reverse=True)
    return ''.join(
        card('/blog/%s' % p['slug'], p.get('category', 'Blog'),
             p['title'], trim(p.get('description', '')))
        for p in posts[:N_BLOG]
    ), len(posts)


def business_cards():
    arts = [parse_front_matter(p) for p in glob.glob('business-sources/*.txt')]
    arts = [a for a in arts if a.get('title')]

    by_section = {}
    for a in arts:
        by_section.setdefault(a.get('section', 'Business'), []).append(a)
    for rows in by_section.values():
        rows.sort(key=lambda a: (a.get('order', ''), a['title']))

    ordered = ([s for s in SECTION_ORDER if s in by_section] +
               sorted(s for s in by_section if s not in SECTION_ORDER))

    # One per section first, so the six cards span the breadth of the hub
    # rather than showing six articles about pricing.
    picked, round_no = [], 0
    while len(picked) < N_BIZ and round_no < 12:
        for sec in ordered:
            if len(picked) >= N_BIZ:
                break
            if round_no < len(by_section[sec]):
                picked.append(by_section[sec][round_no])
        round_no += 1

    return ''.join(
        card('/business/%s' % a['slug'], a.get('section', 'Business'),
             a['title'], trim(a.get('question', '')))
        for a in picked
    ), len(arts)


def build_block():
    blog_html, n_blog = blog_cards()
    biz_html, n_biz = business_cards()

    block = (
        START + '\n'
        '<style>.part--link{display:block;text-decoration:none;color:inherit;'
        'transition:border-color .15s ease,transform .15s ease}'
        '.part--link:hover{border-color:var(--gold);transform:translateY(-2px)}'
        '.part--link:hover h3{color:var(--terracotta)}'
        '.feed-grid{grid-template-columns:repeat(3,1fr)}'
        '@media(max-width:980px){.feed-grid{grid-template-columns:repeat(2,1fr)}}'
        '@media(max-width:620px){.feed-grid{grid-template-columns:1fr}}</style>\n'
        '\n'
        '<hr class="seam">\n'
        '\n'
        '<section class="wrap">\n'
        '  <p class="eyebrow" style="text-align:center">From the workshop journal</p>\n'
        '  <h2 style="text-align:center;margin-top:.3rem">Recent writing</h2>\n'
        '  <div class="parts feed-grid">\n'
        + blog_html +
        '  </div>\n'
        '  <div class="btn-row" style="justify-content:center;margin-top:1.1rem">\n'
        '    <a class="btn btn-primary" href="/blog/">Read all %d posts</a>\n'
        '  </div>\n'
        '</section>\n'
        '\n'
        '<hr class="seam">\n'
        '\n'
        '<section class="wrap">\n'
        '  <p class="eyebrow" style="text-align:center">The business hub</p>\n'
        '  <h2 style="text-align:center;margin-top:.3rem">Running an upholstery business</h2>\n'
        '  <p class="read" style="text-align:center;color:#574f46;margin-bottom:.4rem">'
        'Pricing, quoting, customers and the parts of the trade the old manuals never mention '
        '&#8212; written from thirty years of running a workshop.</p>\n'
        '  <div class="parts feed-grid">\n'
        + biz_html +
        '  </div>\n'
        '  <div class="btn-row" style="justify-content:center;margin-top:1.1rem">\n'
        '    <a class="btn btn-primary" href="/business/">All %d business articles</a>\n'
        '  </div>\n'
        '  <p class="read" style="text-align:center;margin:1.4rem auto 0;font-size:1.05rem;'
        'color:#574f46">In the trade? <a href="/state-of-the-trade/take-part">'
        '<strong>Take the State of the Trade survey</strong></a> &#8212; thirteen questions '
        'on rates, lead times and what actually pays. Three minutes, anonymous, and the '
        '<a href="/state-of-the-trade/">results</a> are free for anyone to use.</p>\n'
        '</section>\n'
        '\n'
        + END
    ) % (n_blog, n_biz)

    return block, n_blog, n_biz


def main():
    print('build-home-feeds' + ('  [DRY RUN - nothing written]' if DRY else ''))

    if not os.path.exists(PAGE):
        print('  ! %s not found - are you in the repo root?' % PAGE)
        sys.exit(1)

    block, n_blog, n_biz = build_block()
    if not n_blog and not n_biz:
        print('  ! no sources parsed - aborting rather than writing an empty block')
        sys.exit(1)

    page = open(PAGE, encoding='utf-8').read()

    if START in page and END in page:
        page = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: block,
                      page, flags=re.S)
        action = 'replaced'
    elif ANCHOR in page:
        page = page.replace(ANCHOR, block + '\n\n' + ANCHOR, 1)
        action = 'inserted'
    else:
        print('  ! anchor not found and no existing markers.')
        print('    The "Free tool" section may have been edited. Paste me')
        print('    index.html around that block and I will adjust the anchor.')
        sys.exit(1)

    if not DRY:
        open(PAGE, 'w', encoding='utf-8').write(page)

    print('  %s feed block: %d blog cards (of %d), %d business cards (of %d)'
          % (action, min(N_BLOG, n_blog), n_blog, min(N_BIZ, n_biz), n_biz))
    print('  done.')


if __name__ == '__main__':
    main()

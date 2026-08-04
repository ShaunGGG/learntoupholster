#!/usr/bin/env python3
"""
merge-gallery.py — put the gallery on the projects page.

Two pages were doing halves of the same job. /projects/ documents six jobs stage
by stage, which is what the site is for. /our-work holds forty-three photographs
of finished pieces with no write-up, which is a portfolio.

Split like that, the documented work looks thin and the gallery looks like
advertising. Together they read properly: here is how the work is done, and here
is a great deal more of it from the same bench.

This lifts the gallery figures out of our-work.html and adds them to
projects/index.html as a closing section, with the gallery CSS carried across.
It is a post-processor rather than an edit, so it survives build-projects.py
regenerating the hub \u2014 run it after.

Idempotent. Backs up before writing.
"""

import os, re, sys, shutil, datetime

SRC = 'our-work.html'
DEST = os.path.join('projects', 'index.html')
MARK = 'ltu-gallery-merged'

INTRO = (
    '<h2>More from the bench</h2>\n'
    '<p>The jobs above are documented start to finish. These are pieces that went '
    'through the same workshop without a camera on every stage \u2014 Victorian '
    'show-frames, Queen Anne wing chairs, mid-century settees and a good deal of '
    'deep buttoning.</p>\n')


def extract_gallery(src_html):
    """Just the figures.

    The <div class="gallery-wrap"> that holds them also contains a promotional
    paragraph about Greenwood being insured, a Facebook group callout, and a
    sidenote. Taking the wrapper drags all three across — and the callout's
    inline SVG loses the CSS that sizes it, so the Facebook icon renders at full
    size. Take the inner gallery div and nothing else.
    """
    m = re.search(r'<div class="gallery"[^>]*>.*?</div>\s*(?=</div>|<h2|<div class="capture"|</article>|</section>)',
                  src_html, re.S)
    if not m:
        return None, None

    block = m.group(0)

    # Gallery rules from the page's own <style> blocks, so the section looks
    # the same once it moves.
    css = []
    for st in re.findall(r'<style[^>]*>(.*?)</style>', src_html, re.S):
        if st.strip().startswith(':root'):
            continue                      # sitewide stylesheet, already present
        for rule in re.findall(r'[^{}]*\{[^{}]*\}', st):
            if re.search(r'\.gallery|\.lightbox|figure|figcaption', rule):
                css.append(rule.strip())
    return block, '\n'.join(css)


def find_lightbox_js(src_html):
    """Whatever makes data-full open large. Without it the figures are inert."""
    out = []
    for s in re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', src_html, re.S):
        if 'data-full' in s or 'lightbox' in s.lower():
            out.append(s)
    return '\n'.join(out)


def main():
    if not os.path.exists(SRC):
        sys.exit('Cannot find %s. Run this from ~/learntoupholster.' % SRC)
    if not os.path.exists(DEST):
        sys.exit('Cannot find %s. Run build-projects.py first.' % DEST)

    src = open(SRC, encoding='utf-8').read()
    dest = open(DEST, encoding='utf-8').read()

    if MARK in dest:
        # Remove the previous merge so this can repair an earlier one rather
        # than refusing and leaving the page wrong.
        before = dest
        dest = re.sub(r'\n<!-- %s -->.*?(?=<h2[^>]*>Why we document|<div class="capture"|</article>|</section>)' % MARK,
                      '', dest, flags=re.S)
        dest = re.sub(r'<style>/\* %s \*/.*?</style>\s*' % MARK, '', dest, flags=re.S)
        dest = re.sub(r'<script>/\* %s \*/.*?</script>\s*' % MARK, '', dest, flags=re.S)
        if dest != before:
            print('Previous merge removed \u2014 redoing it.')

    block, css = extract_gallery(src)
    if not block:
        sys.exit('Could not find the gallery block in %s. Nothing written.' % SRC)

    figures = len(re.findall(r'<figure', block))
    js = find_lightbox_js(src)

    # Place it after the last content section, before the closing wrapper.
    anchor = None
    for pat in (r'(?=<h2[^>]*>Why we document)', r'(?=<div class="capture")',
                r'(?=</article>)', r'(?=</section>)'):
        m = re.search(pat, dest)
        if m:
            anchor = m.start()
            break
    if anchor is None:
        sys.exit('Could not find a place to insert the gallery. Nothing written.')

    add = '\n<!-- %s -->\n%s%s\n' % (MARK, INTRO, block)
    out = dest[:anchor] + add + dest[anchor:]

    if css:
        out = out.replace('</head>', '<style>/* %s */\n%s\n</style>\n</head>' % (MARK, css), 1)
    if js and 'data-full' not in dest:
        out = out.replace('</body>', '<script>/* %s */\n%s\n</script>\n</body>' % (MARK, js), 1)

    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    bdir = os.path.join(os.path.expanduser('~'), 'ltu-backups', stamp)
    os.makedirs(bdir, exist_ok=True)
    shutil.copy2(DEST, os.path.join(bdir, 'projects__index.html'))
    open(DEST, 'w', encoding='utf-8').write(out)

    print('Gallery merged into %s' % DEST)
    print('  figures moved  : %d' % figures)
    print('  gallery CSS    : %s' % ('carried across' if css else 'none found \u2014 check the look'))
    print('  lightbox script: %s' % ('carried across' if js else 'none found \u2014 check it still opens'))
    print('\nBackup: ~/ltu-backups/%s/projects__index.html' % stamp)
    print('\n%s is untouched. See the README for what to do with it.' % SRC)


if __name__ == '__main__':
    main()

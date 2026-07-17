#!/usr/bin/env python3
"""Wire the Reader's Bench into the site (idempotent):
  1. Footer link on every page (after 'Find an upholsterer').
  2. Start Here: extend the 'Then do it again' sidenote with the submit invitation.
  3. Our-work gallery + homepage: a one-line pointer.
  4. Privacy policy: Reader's Bench submissions section.
  5. sitemap.xml + llms.txt entries."""
import glob, re

FOOT_MARK = '<p class="foot-small"><a href="/find-an-upholsterer">Find an upholsterer</a></p>'
FOOT_ADD  = FOOT_MARK + '\n        <p class="foot-small"><a href="/readers-bench">Reader&#8217;s Bench</a></p>'

n = 0
for f in sorted(glob.glob('*.html') + glob.glob('projects/*.html')):
    c = open(f).read()
    if '/readers-bench">Reader' in c and FOOT_ADD in c:
        continue
    if FOOT_MARK in c and FOOT_ADD not in c:
        open(f, 'w').write(c.replace(FOOT_MARK, FOOT_ADD))
        n += 1
print(f'footer link added on {n} pages')

# ---- 2. Start Here sidenote --------------------------------------------------
c = open('start-here.html').read()
if 'readers-bench' not in c.split('foot-small')[0]:
    old = ('you\u2019ll be under two hours a seat by the fourth, and that\u2019s the moment '
           'this stops being a project and starts being a skill.')
    new = old + (' And when the first one&#8217;s done &mdash; wonky pleats and all &mdash; '
                 '<a href="/readers-bench">put it up on the Reader&#8217;s Bench</a>. '
                 'Every workshop has a wall for first pieces; this site has one too.')
    assert old in c, 'start-here sidenote marker not found'
    open('start-here.html', 'w').write(c.replace(old, new, 1))
    print('start-here: invitation added')
else:
    print('start-here: already linked')

# ---- 3. our-work + homepage pointers ----------------------------------------
c = open('our-work.html').read()
if 'readers-bench' not in c.split('site-footer')[0]:
    m = re.search(r'(<article class="article wrap read">|<section class="wrap read">)', c)
    band = ('<div class="sidenote" style="background:#fff;border:1px solid var(--rule);'
            'border-left:4px solid var(--gold)">\n'
            '    <span class="tag">Made something yourself?</span>\n'
            '    <p>This page is our work &mdash; but there&#8217;s a wall for yours too. '
            '<a href="/readers-bench"><strong>The Reader&#8217;s Bench</strong></a> is where '
            'readers&#8217; first seats go up: send a photo of your first drop-in and get featured.</p>\n'
            '  </div>\n  ')
    if m:
        c = c.replace(m.group(1), m.group(1) + '\n  ' + band, 1)
        open('our-work.html', 'w').write(c)
        print('our-work: band added')
    else:
        print('our-work: NO ANCHOR FOUND — skipped')
else:
    print('our-work: already linked')

c = open('index.html').read()
if 'readers-bench' not in c.split('site-footer')[0]:
    old = '<a href="/our-work">See all our work</a>'
    if old in c:
        c = c.replace(old, old + ' &nbsp;&middot;&nbsp; <a href="/readers-bench">Readers&#8217; first seats &rarr;</a>', 1)
        open('index.html', 'w').write(c)
        print('homepage: pointer added')
    else:
        print('homepage: anchor not found — skipped (footer link still present)')
else:
    print('homepage: already linked')

# ---- 4. privacy policy -------------------------------------------------------
p = open('privacy-policy.html').read()
if 'Reader&#8217;s Bench submissions' not in p:
    section = ('<h3>Reader&#8217;s Bench submissions</h3>\n'
               '  <p>If you submit a project to the Reader&#8217;s Bench, we collect the photo you upload, '
               'your first name, your town, an optional note about the job, and your email address. '
               'Every submission is reviewed by a person before anything appears on the site. If approved, '
               'the photo, your first name, your town and your note are displayed publicly; '
               '<strong>your email address is never published</strong> and is used only to tell you when '
               'your piece is featured. Submissions that are not approved are deleted, and unreviewed '
               'submissions are deleted automatically after 90 days. To have a featured piece removed at '
               'any time, <a href="/contact">contact us</a> and it will be taken down.</p>\n  ')
    m = re.search(r'<h3>Analytics</h3>', p)
    assert m, 'privacy anchor not found'
    p = p.replace(m.group(0), section + m.group(0), 1)
    open('privacy-policy.html', 'w').write(p)
    print('privacy-policy: section added')
else:
    print('privacy-policy: already present')

# ---- 5. sitemap + llms.txt ---------------------------------------------------
s = open('sitemap.xml').read()
if '/readers-bench<' not in s:
    mark = '  <url><loc>https://www.learntoupholster.com/start-here</loc></url>\n'
    assert mark in s
    open('sitemap.xml', 'w').write(s.replace(mark, mark + '  <url><loc>https://www.learntoupholster.com/readers-bench</loc></url>\n', 1))
    print('sitemap: added')

t = open('llms.txt').read()
if '/readers-bench)' not in t:
    entry = ("- [The Reader's Bench — first seats by readers](https://www.learntoupholster.com/readers-bench): "
             "A moderated gallery of first upholstery projects made by readers of the book — drop-in seats and "
             "early pieces, submitted by the people who made them, with a form to submit your own.")
    lines = t.split('\n')
    items = [(i, l) for i, l in enumerate(lines) if l.startswith('- [')]
    pos = next((i for i, l in items if l[3:l.index(']')].lower() > 'the reader'), items[-1][0] + 1)
    lines.insert(pos, entry)
    open('llms.txt', 'w').write('\n'.join(lines))
    print('llms.txt: added')

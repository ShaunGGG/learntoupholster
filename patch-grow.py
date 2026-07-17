#!/usr/bin/env python3
"""AdSense -> Grow by Mediavine swap:
  1. Replaces the AdSense loader with the Grow script on every page that has it.
  2. Adds Grow to the three pages that never had AdSense (404 + both policies).
  3. Rewrites the advertising sections of the cookie & privacy policies for Grow/Mediavine.
  4. Updates the two policy descriptions in llms.txt.
Idempotent — safe to re-run."""
import glob, re

GROW = ('<!-- Grow by Mediavine -->\n'
        '<script data-grow-initializer="">!(function(){window.growMe||((window.growMe=function(e){window.growMe._.push(e);}),(window.growMe._=[]));'
        'var e=document.createElement("script");(e.type="text/javascript"),(e.src="https://faves.grow.me/main.js"),(e.defer=!0),'
        'e.setAttribute("data-grow-faves-site-id","U2l0ZTo4Y2Q5OWRmNC00NjQ3LTQxN2YtOWI1Mi0yZmM3ZjIzYzMzNzE=");'
        'var t=document.getElementsByTagName("script")[0];t.parentNode.insertBefore(e,t);})();</script>')

ADS_RE = re.compile(
    r'(?:<!-- Google AdSense -->\s*)?'
    r'<script async src="https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js\?client=ca-pub-3728586174960711"'
    r'[^>]*>\s*</script>', re.S)

swapped, inserted, untouched = [], [], []
for f in sorted(glob.glob('*.html') + glob.glob('projects/*.html')):
    c = open(f).read()
    if 'faves.grow.me' in c:
        untouched.append(f); continue
    c2, n = ADS_RE.subn(GROW, c)
    if n:
        # collapse any duplicate loaders down to one
        if n > 1:
            first = c2.find('<!-- Grow by Mediavine -->')
            c2 = c2[:first + len(GROW)] + ADS_RE.sub('', c2[first + len(GROW):]).replace(GROW, '')
        open(f, 'w').write(c2); swapped.append(f)
    elif '</head>' in c:
        open(f, 'w').write(c.replace('</head>', GROW + '\n</head>', 1)); inserted.append(f)
print(f'grow: swapped-in-for-adsense {len(swapped)}, inserted-fresh {inserted}, already-done {len(untouched)}')

# ---- cookie policy ----------------------------------------------------------
c = open('cookie-policy.html').read()
old = re.search(r'<h3>2\. Advertising \(Google AdSense\)</h3>.*?(?=<h3>3\. Analytics</h3>)', c, re.S)
if old:
    new = ('<h3>2. Advertising &amp; audience measurement (Grow by Mediavine)</h3>\n'
           '  <p>We use <a href="https://grow.me/" target="_blank" rel="noopener">Grow by Mediavine</a>, '
           'a reader-engagement and audience-measurement tool, as we prepare to serve advertising through '
           'Mediavine&#8217;s Journey programme. Grow sets first-party cookies and similar storage to measure '
           'visits and engagement, remember your preferences and, if you choose to use its features, let you '
           'save content or subscribe. Mediavine describes its data practices in its '
           '<a href="https://www.mediavine.com/legal-and-privacy-center/" target="_blank" rel="noopener">Legal '
           'and Privacy Center</a>. We no longer use Google AdSense.</p>\n'
           '  <p>Once adverts are being served, Mediavine and its advertising partners will use cookies and '
           'similar technologies to serve and personalise ads and to measure how they perform. In the UK, the '
           'European Economic Area (EEA) and Switzerland, these advertising cookies are only set '
           '<strong>after you have given consent</strong> (see below), and you can review each vendor&#8217;s '
           'own choices through the consent tool.</p>\n\n  ')
    c = c.replace(old.group(0), new)
c = c.replace('a Google-certified consent management platform that meets the IAB Transparency &amp; Consent '
              'Framework (TCF v2.2), which is the standard Google requires for advertising in these regions.',
              'a consent management platform that meets the IAB Transparency &amp; Consent Framework '
              '(TCF v2.2), the standard required for advertising in these regions.')
c = c.replace('(managed by Google)', '(managed by our advertising provider)')
c = c.replace('including functional storage and Google AdSense advertising cookies',
              'including functional storage and Grow by Mediavine engagement and advertising cookies')
open('cookie-policy.html', 'w').write(c)
print('cookie-policy: section rewritten:', 'Grow by Mediavine' in c and 'Advertising (Google AdSense)' not in c)

# ---- privacy policy ---------------------------------------------------------
p = open('privacy-policy.html').read()
old = re.search(r'<h3>Google AdSense and third-party advertising</h3>.*?(?=<h3>Analytics</h3>)', p, re.S)
if old:
    new = ('<h3>Advertising and audience measurement (Grow by Mediavine)</h3>\n'
           '  <p>We use Grow by Mediavine, a reader-engagement and audience-measurement tool, as we prepare '
           'to serve advertising through Mediavine&#8217;s Journey programme. Grow sets first-party cookies '
           'and similar storage to measure visits and engagement and to provide optional features such as '
           'saving content or subscribing by email. Mediavine&#8217;s handling of this data is described in '
           'its <a href="https://www.mediavine.com/legal-and-privacy-center/" target="_blank" '
           'rel="noopener nofollow">Legal and Privacy Center</a>. We no longer use Google AdSense.</p>\n'
           '  <p>Where adverts are served through Mediavine, third-party advertising vendors may use cookies '
           'to serve ads based on your prior visits to this and other websites, subject to consent where '
           'required. You may opt out of personalised advertising from many providers using the tools at '
           '<a href="https://www.aboutads.info/choices" target="_blank" rel="noopener nofollow">aboutads.info/choices</a> '
           'and <a href="https://www.youronlinechoices.eu" target="_blank" rel="noopener nofollow">youronlinechoices.eu</a>. '
           'Opting out does not remove adverts; it makes them less tailored to you.</p>\n'
           '  <p>Other ad networks may also place cookies where adverts are served. We do not control these, '
           'and recommend reviewing the relevant third party&#8217;s own privacy policy.</p>\n  ')
    p = p.replace(old.group(0), new)
p = p.replace('including cookies, Google AdSense advertising, analytics',
              'including cookies, Grow by Mediavine advertising, analytics')
open('privacy-policy.html', 'w').write(p)
print('privacy-policy: section rewritten:', 'Grow by Mediavine' in p and 'AdSense and third-party' not in p)

# ---- llms.txt ---------------------------------------------------------------
t = open('llms.txt').read()
t = t.replace('including functional storage and Google AdSense advertising cookies',
              'including functional storage and Grow by Mediavine engagement and advertising cookies')
t = t.replace('including cookies, Google AdSense advertising, analytics',
              'including cookies, Grow by Mediavine advertising, analytics')
open('llms.txt', 'w').write(t)
print('llms.txt updated')

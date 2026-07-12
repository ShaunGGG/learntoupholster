#!/usr/bin/env python3
"""Routes every class="aff" amazon.co.uk link through /go/amazon so non-UK
visitors land on their home marketplace. UK visitors still receive the exact
original tagged link. Idempotent. Run from repo root: python3 patch-amazon-go.py"""
import glob, html, re, urllib.parse

PAT = re.compile(r'(<a class="aff" href=")(https://www\.amazon\.co\.uk/[^"]+)("[^>]*>)(.*?)(</a>)', re.S)

def search_terms(orig_url, link_text):
    """Best search phrase: the k= from search links, else cleaned link text."""
    real = html.unescape(orig_url)
    m = re.search(r'[?&]k=([^&]+)', real)
    if m:
        return urllib.parse.unquote_plus(m.group(1))
    txt = html.unescape(re.sub(r'<[^>]+>', '', link_text))
    txt = re.sub(r'[\u2033\u2032"\']', ' inch ', txt, count=1)      # 8″ -> 8 inch
    txt = re.sub(r'\s+', ' ', txt).strip()
    if 'upholster' not in txt.lower():
        txt = 'upholstery ' + txt
    return txt

changed = total = 0
for f in glob.glob('*.html'):
    t = open(f, encoding='utf-8').read()
    n = 0
    def _rw(m):
        global n_local
        pre, orig, mid, text, post = m.groups()
        q = search_terms(orig, text)
        new_href = '/go/amazon?q=' + urllib.parse.quote_plus(q) + '&u=' + urllib.parse.quote(html.unescape(orig), safe='')
        return pre + new_href + mid + text + post
    new_t, n = PAT.subn(_rw, t)
    if n:
        open(f, 'w', encoding='utf-8').write(new_t)
        changed += 1; total += n
print(f"done - {total} affiliate links rerouted across {changed} pages")
